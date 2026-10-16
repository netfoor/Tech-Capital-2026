from pathlib import Path

import pytest

from app.recommender import (
    AtributoAcc,
    POICandidato,
    Restricciones,
    SolicitudRuta,
    recomendar,
)
from app.recommender.carga import cargar_catalogo
from app.recommender.verificador import verificar

DATOS = Path(__file__).parent / "datos"
CENTRO = (19.0433, -98.1981)


def _poi(pid, dlat=0.0, dlon=0.0, categoria="museo", **kw) -> POICandidato:
    base = dict(
        poi_id=pid,
        nombre=kw.pop("nombre", f"Lugar {pid}"),
        categoria=categoria,
        destino_id="puebla",
        corredor_id="c1",
        lat=CENTRO[0] + dlat,
        lon=CENTRO[1] + dlon,
        costo_rango="gratis",
        horario_osm="Mo-Su 08:00-20:00",
        accesibilidad={},
        es_destino_alternativo=False,
        popularidad=0.5,
    )
    base.update(kw)
    return POICandidato(**base)


def _sin_escalones(estado="verificado", valor="si", confianza=0.9, origen="equipo"):
    return {"acceso_sin_escalones": AtributoAcc(valor, estado, origen, confianza)}


@pytest.fixture
def catalogo_sintetico():
    return cargar_catalogo(DATOS / "poi_sintetico.csv", DATOS / "poi_accesibilidad_sintetico.csv")


def test_catalogo_sintetico_esta_rotulado(catalogo_sintetico):
    assert len(catalogo_sintetico) >= 40
    assert all(p.is_synthetic for p in catalogo_sintetico)


def test_reporte_reciente_sustituye_a_la_verificacion(catalogo_sintetico):
    poi = next(p for p in catalogo_sintetico if p.poi_id == "syn-cen-01")
    assert poi.accesibilidad["acceso_sin_escalones"].estado == "reportado"


def test_sin_escalones_clasifica_los_cuatro_casos():
    pois = [
        _poi("verificado", 0.001, accesibilidad=_sin_escalones()),
        _poi("confiable", 0.002, accesibilidad=_sin_escalones("sin_verificar", confianza=0.6)),
        _poi("baja", 0.003, accesibilidad=_sin_escalones("sin_verificar", confianza=0.59)),
        _poi("sin-dato", 0.004),
        _poi("no", 0.005, accesibilidad=_sin_escalones(valor="no")),
        _poi("limitado", 0.006, accesibilidad=_sin_escalones(valor="limitado")),
        _poi("reportado", 0.007, accesibilidad=_sin_escalones("reportado", confianza=0.99)),
    ]
    s = SolicitudRuta(
        horas_disponibles=6, punto_partida=CENTRO, restricciones=Restricciones(sin_escalones=True)
    )
    r = recomendar(s, pois)
    en_ruta = {p.poi_id for p in r.paradas}
    assert en_ruta <= {"verificado", "confiable"}
    assert {"verificado", "confiable"} <= en_ruta
    assert set(r.alternativos) >= {"baja", "sin-dato"}
    excluidos = dict(r.no_incluidos)
    assert {"no", "limitado", "reportado"} <= set(excluidos)
    assert not ({"no", "limitado", "reportado"} & set(r.alternativos))
    assert any("sin verificar" in d.lower() for d in r.datos_desconocidos)


def test_sin_alternativos_los_sin_dato_van_a_no_incluidos():
    pois = [_poi("a", accesibilidad=_sin_escalones()), _poi("b", 0.002)]
    s = SolicitudRuta(
        horas_disponibles=3,
        punto_partida=CENTRO,
        restricciones=Restricciones(sin_escalones=True),
        incluir_alternativos=False,
    )
    r = recomendar(s, pois)
    assert r.alternativos == []
    assert "b" in dict(r.no_incluidos)


def test_presupuesto_excluye_costos_mayores_y_avisa_si_no_hay_dato():
    pois = [
        _poi("gratis", 0.001, costo_rango="gratis"),
        _poi("alto", 0.002, costo_rango="alto"),
        _poi("sin-costo", 0.003, costo_rango=None, categoria="templo"),
    ]
    r = recomendar(
        SolicitudRuta(horas_disponibles=5, presupuesto="bajo", punto_partida=CENTRO), pois
    )
    assert "alto" not in {p.poi_id for p in r.paradas}
    assert "alto" in dict(r.no_incluidos)
    parada = next(p for p in r.paradas if p.poi_id == "sin-costo")
    assert "Costo sin verificar" in parada.advertencias


def test_presupuesto_invalido():
    with pytest.raises(ValueError):
        recomendar(SolicitudRuta(horas_disponibles=2, presupuesto="caro"), [_poi("a")])


def test_horario_cerrado_excluye_y_no_interpretable_advierte():
    pois = [
        _poi("cerrado-lunes", 0.001, horario_osm="Tu-Su 10:00-17:00"),
        _poi("raro", 0.002, horario_osm="Mo-Su sunrise-sunset", categoria="templo"),
        _poi("abierto", 0.003, horario_osm="Mo-Su 09:00-18:00", categoria="galeria"),
    ]
    s = SolicitudRuta(horas_disponibles=4, punto_partida=CENTRO, dia_semana=0)
    r = recomendar(s, pois)
    ids = {p.poi_id for p in r.paradas}
    assert "cerrado-lunes" not in ids
    assert "lunes" in dict(r.no_incluidos)["cerrado-lunes"]
    assert {"raro", "abierto"} <= ids
    raro = next(p for p in r.paradas if p.poi_id == "raro")
    assert any("Horario sin verificar" in a for a in raro.advertencias)


def test_espera_a_que_abra_y_respeta_cierre():
    pois = [_poi("abre-tarde", horario_osm="Mo-Su 11:00-12:30")]
    s = SolicitudRuta(horas_disponibles=4, punto_partida=CENTRO, hora_inicio="10:30")
    r = recomendar(s, pois)
    assert [p.poi_id for p in r.paradas] == ["abre-tarde"]
    assert any("Espera" in a for a in r.paradas[0].advertencias)
    assert verificar(r, s, {p.poi_id: p for p in pois}) == []
    # Si ya no da tiempo antes del cierre, no entra.
    tarde = SolicitudRuta(horas_disponibles=4, punto_partida=CENTRO, hora_inicio="12:00")
    assert recomendar(tarde, pois).paradas == []


def test_tiempo_total_no_excede_lo_disponible(catalogo_sintetico):
    for horas in (1, 2, 3.5, 6):
        s = SolicitudRuta(horas_disponibles=horas, punto_partida=CENTRO, intereses=["historia"])
        r = recomendar(s, catalogo_sintetico)
        assert r.metricas["tiempo_usado_min"] <= horas * 60
        fin = max((e["fin"] for e in r.metricas["linea_tiempo"]), default=0)
        assert fin <= horas * 60


def test_lugar_lejano_no_cabe():
    pois = [_poi("lejos", 0.05)]  # ~5.5 km
    r = recomendar(SolicitudRuta(horas_disponibles=1, punto_partida=CENTRO), pois)
    assert r.paradas == []
    assert "caminando" in dict(r.no_incluidos)["lejos"]


def test_explicacion_no_vacia_y_motivo_por_parada(catalogo_sintetico):
    s = SolicitudRuta(
        horas_disponibles=4,
        punto_partida=CENTRO,
        intereses=["historia", "gastronomia"],
        restricciones=Restricciones(sin_escalones=True),
    )
    r = recomendar(s, catalogo_sintetico)
    assert r.explicacion.strip()
    assert r.paradas
    for p in r.paradas:
        assert p.motivo.strip()
        if p.poi_id not in ("descanso",) and not p.poi_id.endswith(("b1", "b2")):
            assert p.motivo.startswith("Te lo recomendamos porque")
    assert r.datos_desconocidos


def test_pertinencia_prefiere_el_interes():
    pois = [
        _poi("museo", 0.001, categoria="museo", descripcion="historia colonial"),
        _poi("cafe", 0.001, categoria="cafe", descripcion="café de especialidad"),
    ]
    s = SolicitudRuta(horas_disponibles=1.2, punto_partida=CENTRO, intereses=["historia"])
    r = recomendar(s, pois)
    assert r.paradas[0].poi_id == "museo"
    assert "historia" in r.paradas[0].motivo


def test_diversidad_premia_destino_alternativo():
    pois = [
        _poi("polo", 0.001, categoria="templo", popularidad=0.95),
        _poi("alterno", -0.001, categoria="templo", popularidad=0.1, es_destino_alternativo=True),
    ]
    s = SolicitudRuta(horas_disponibles=0.6, punto_partida=CENTRO)
    r = recomendar(s, pois)
    assert [p.poi_id for p in r.paradas] == ["alterno"]


def test_una_sola_comida_por_ruta():
    pois = [_poi(f"r{i}", 0.001 * i, categoria="restaurante") for i in range(3)]
    s = SolicitudRuta(horas_disponibles=6, punto_partida=CENTRO, intereses=["gastronomia"])
    r = recomendar(s, pois)
    assert len(r.paradas) == 1


def test_descansos_y_banios_se_insertan():
    banio = _poi(
        "banio-1",
        0.002,
        categoria="banio",
        accesibilidad={
            "banio_accesible": AtributoAcc("si", "verificado", "equipo", 0.9),
            "acceso_sin_escalones": AtributoAcc("si", "verificado", "equipo", 0.9),
        },
    )
    pois = [_poi(f"m{i}", 0.003 * i, 0.002 * (i % 2)) for i in range(4)] + [banio]
    s = SolicitudRuta(
        horas_disponibles=4,
        punto_partida=CENTRO,
        restricciones=Restricciones(banio_accesible=True, descansos_cada_min=30),
    )
    r = recomendar(s, pois)
    ids = [p.poi_id for p in r.paradas]
    assert "banio-1" in ids
    assert r.metricas["n_descansos"] >= 1 or any(
        "pausa" in " ".join(p.advertencias) for p in r.paradas
    )
    assert verificar(r, s, {p.poi_id: p for p in pois}) == []


def test_sin_banios_disponibles_la_ruta_se_acorta_y_no_viola():
    pois = [_poi(f"m{i}", 0.002 * i) for i in range(5)]
    s = SolicitudRuta(
        horas_disponibles=5, punto_partida=CENTRO, restricciones=Restricciones(banio_accesible=True)
    )
    r = recomendar(s, pois)
    assert r.metricas["tiempo_usado_min"] <= 90
    assert verificar(r, s, {p.poi_id: p for p in pois}) == []


def test_pendiente_maxima():
    def pend(v, estado="verificado"):
        return {"pendiente_pct": AtributoAcc(v, estado, "equipo", 0.9)}

    pois = [
        _poi("plano", 0.001, accesibilidad=pend("3.0")),
        _poi("empinado", 0.002, accesibilidad=pend("12"), categoria="templo"),
        _poi("sin-dato", 0.003, categoria="galeria"),
    ]
    s = SolicitudRuta(
        horas_disponibles=4, punto_partida=CENTRO, restricciones=Restricciones(pendiente_max_pct=6)
    )
    r = recomendar(s, pois)
    assert {p.poi_id for p in r.paradas} == {"plano"}
    assert "empinado" in dict(r.no_incluidos)
    assert "sin-dato" in r.alternativos


def test_determinista(catalogo_sintetico):
    s = SolicitudRuta(
        horas_disponibles=5,
        intereses=["arte", "religion"],
        restricciones=Restricciones(sin_escalones=True, descansos_cada_min=45),
    )
    a = recomendar(s, catalogo_sintetico)
    b = recomendar(s, list(reversed(catalogo_sintetico)))
    assert [p.poi_id for p in a.paradas] == [p.poi_id for p in b.paradas]
    assert a.explicacion == b.explicacion


def test_catalogo_vacio():
    r = recomendar(SolicitudRuta(horas_disponibles=3), [])
    assert r.paradas == []
    assert "No encontramos" in r.explicacion
