"""Cálculos del tablero contra valores hechos a mano (spec 019)."""

import pytest
from sqlalchemy import select

from app.models import DataLineage, MetricDefinition
from app.services import definiciones, metricas
from app.services.metricas import FilaOficial


def _filas(centro, destino, nivel, datos):
    """datos: {periodo: {indicador: valor}}."""
    return [
        FilaOficial(centro, destino, nivel, p, ind, v)
        for p, indicadores in datos.items()
        for ind, v in indicadores.items()
    ]


def _mes(disp, ocup, lleg, noches):
    return {
        "cuartos_disponibles": disp,
        "cuartos_ocupados": ocup,
        "llegadas_turistas": lleg,
        "turistas_noche": noches,
    }


@pytest.fixture
def pequeno():
    # Enero (31 días) y febrero (28 días) de 2026: 59 días en la ventana.
    return (
        _filas(
            "A",
            "a",
            "destino",
            {"2026-01": _mes(100, 50, 60, 120), "2026-02": _mes(100, 70, 40, 80)},
        )
        + _filas(
            "B",
            "b",
            "destino",
            {"2026-01": _mes(200, 40, 30, 30), "2026-02": _mes(200, 40, 10, 10)},
        )
        + _filas(
            "Estado",
            None,
            "agregado",
            {"2026-01": _mes(300, 90, 90, 150), "2026-02": _mes(300, 110, 50, 90)},
        )
        # Los subcentros no entran al índice.
        + _filas("Sub", None, "subcentro", {"2026-01": _mes(10, 9, 1000, 1000)})
    )


def test_ocupacion_cuartos_libres_y_estadia(pequeno):
    r = metricas.calcular_oferta_demanda(pequeno, {"a": "Destino A", "b": "Destino B"})
    d = {x["destino_id"]: x for x in r["destinos"]}
    # A: 120 ocupados / 200 disponibles; (200 − 120) / 59 días; 200 noches / 100 llegadas.
    assert d["a"]["ocupacion_pct"] == pytest.approx(60.0)
    assert d["a"]["cuartos_libres_dia"] == pytest.approx(80 / 59)
    assert d["a"]["estadia_noches"] == pytest.approx(2.0)
    # B: 80 / 400; 320 / 59; 40 / 40.
    assert d["b"]["ocupacion_pct"] == pytest.approx(20.0)
    assert d["b"]["cuartos_libres_dia"] == pytest.approx(320 / 59)
    assert d["b"]["estadia_noches"] == pytest.approx(1.0)
    assert d["a"]["nombre"] == "Destino A"
    # Estado desde la fila de la fuente: 200 / 600.
    assert r["estado"]["ocupacion_pct"] == pytest.approx(100 / 3)
    assert r["ventana"] == {"desde": "2026-01", "hasta": "2026-02", "meses": 2}
    assert d["a"]["serie_ocupacion"][0] == {"periodo": "2026-01", "ocupacion_pct": 50.0}


def test_hhi_y_participacion(pequeno):
    r = metricas.calcular_oferta_demanda(pequeno)
    d = {x["destino_id"]: x for x in r["destinos"]}
    # Llegadas: A 100, B 40 → 71.43 % y 28.57 %; HHI = 71.43² + 28.57² = 5918.37.
    assert d["a"]["participacion_pct"] == pytest.approx(100 / 1.4)
    assert d["b"]["participacion_pct"] == pytest.approx(40 / 1.4)
    assert r["hhi"]["ventana_12m"] == pytest.approx(5918.3673, abs=1e-3)
    assert r["hhi"]["centros"] == 2
    assert r["hhi"]["cobertura_estado_pct"] == pytest.approx(100.0)
    anual = r["hhi"]["serie_anual"]
    assert anual == [
        {
            "anio": 2026,
            "hhi": pytest.approx(5918.3673, abs=1e-3),
            "meses": 2,
            "centros": 2,
            "parcial": True,
        }
    ]


def test_hhi_casos_limite():
    assert metricas.hhi([1, 0, 0]) == pytest.approx(10_000)
    assert metricas.hhi([1, 1, 1, 1]) == pytest.approx(2_500)
    assert metricas.hhi([]) is None


def test_candidatos_y_crecimiento_sin_evidencia(pequeno):
    r = metricas.calcular_oferta_demanda(pequeno)
    # Mediana de cuartos libres: (80/59 + 320/59) / 2. B tiene 20 % < 33.3 % y 5.42 ≥ 3.39.
    assert r["mediana_cuartos_libres_dia"] == pytest.approx(200 / 59)
    assert [c["destino_id"] for c in r["candidatos"]] == ["b"]
    assert "menor que la del Estado" in r["candidatos"][0]["motivo"]
    d = {x["destino_id"]: x for x in r["destinos"]}
    assert d["b"]["crecimiento_llegadas_pct"] is None
    assert d["b"]["crecimiento_motivo"].startswith("sin evidencia suficiente")


def test_crecimiento_con_24_meses():
    datos = {}
    for i in range(24):
        anio, mes = 2024 + i // 12, i % 12 + 1
        datos[f"{anio}-{mes:02d}"] = _mes(100, 50, 10 if i < 12 else 15, 20)
    r = metricas.calcular_oferta_demanda(_filas("A", "a", "destino", datos))
    assert r["destinos"][0]["crecimiento_llegadas_pct"] == pytest.approx(50.0)
    assert r["ventana"]["desde"] == "2025-01"
    # Sin fila «Estado», el Estado es la suma de los centros.
    assert r["estado"]["origen"] == "suma de los centros"


def test_wilson_y_bootstrap():
    lo, hi = metricas.wilson(5, 10)
    assert lo == pytest.approx(0.2366, abs=1e-4) and hi == pytest.approx(0.7634, abs=1e-4)
    assert metricas.wilson(0, 0) is None
    valores = [1, 2, 3, 4, 5] * 4
    ic = metricas.bootstrap_media(valores)
    assert ic[0] < 3 < ic[1]
    assert metricas.bootstrap_media(valores) == ic  # semilla fija


def test_supresion_complementaria():
    grupos = [
        {"personas": 1, "valor": 5},
        {"personas": 4, "valor": 6},
        {"personas": 3, "valor": 7},
    ]
    metricas.suprimir(grupos, 3, ["valor"])
    assert [g["suprimido"] for g in grupos] == [True, False, True]
    assert grupos[2]["supresion_complementaria"] is True
    assert grupos[0]["valor"] is None and grupos[0]["personas"] is None
    assert grupos[1]["valor"] == 6


def test_csv_con_metadatos():
    texto = metricas.a_csv({"modulo": "x"}, [{"a": 1.5, "b": None, "c": True}])
    assert texto.splitlines() == ["# modulo: x", "a,b,c", "1.5000,,true"]


def test_definiciones(sesion, catalogo):
    contenido = definiciones.leer()
    ids = {f["id"] for f in contenido["indicadores"]}
    assert {"hhi_llegadas", "ocupacion_12m", "cobertura_info_accesibilidad"} <= ids
    for ficha in contenido["indicadores"]:
        assert set(definiciones.CAMPOS_FICHA) <= set(ficha)
        assert ficha["fuentes"]
    # La semilla las carga: definición y linaje por fuente.
    hhi = sesion.get(MetricDefinition, "hhi_llegadas")
    assert hhi.version_formula == "1" and hhi.fuente_id == "sectur-ot-2026-06"
    fuentes = sesion.scalars(
        select(DataLineage.fuente_id).where(
            DataLineage.entidad == "metric_definition",
            DataLineage.entidad_id == "candidato_destino_alternativo",
        )
    ).all()
    assert sorted(fuentes) == ["pv360-catalogo", "sectur-ot-2026-06"]
    # Idempotente.
    antes = sesion.query(DataLineage).count()
    definiciones.cargar(sesion)
    sesion.commit()
    assert sesion.query(DataLineage).count() == antes
