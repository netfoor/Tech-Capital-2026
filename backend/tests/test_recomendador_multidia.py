import random
from pathlib import Path

import pytest

from app.recommender import (
    AtributoAcc,
    Restricciones,
    SolicitudMultidia,
    SolicitudRuta,
    planear_multidia,
    recomendar_multidia,
)
from app.recommender.carga import cargar_catalogo
from app.recommender.tipos import RespuestaRuta
from app.recommender.verificador import verificar

DATOS = Path(__file__).parent / "datos"


@pytest.fixture(scope="module")
def catalogo():
    return cargar_catalogo(DATOS / "poi_sintetico.csv", DATOS / "poi_accesibilidad_sintetico.csv")


def _atractivos(catalogo):
    return [p for p in catalogo if p.categoria != "banio"]


def _verificar_dias(resp, sol, por_id):
    """Cada día pasa el verificador de una ruta con las mismas restricciones."""
    for i, dia_plan in enumerate(resp.dias):
        paradas = dia_plan.paradas
        dia = sol.dia_semana_inicio
        s = SolicitudRuta(
            horas_disponibles=sol.horas_por_dia,
            restricciones=sol.restricciones,
            hora_inicio=sol.hora_inicio,
            dia_semana=None if dia is None else (dia + i) % 7,
        )
        r = RespuestaRuta(
            paradas=paradas,
            no_incluidos=[],
            alternativos=[],
            explicacion="",
            datos_desconocidos=[],
            metricas={"linea_tiempo": resp.metricas["linea_tiempo_por_dia"][i]},
        )
        assert verificar(r, s, por_id) == [], i


def test_sin_duplicados_y_todo_contabilizado(catalogo):
    ids = [p.poi_id for p in _atractivos(catalogo)][::2]
    sol = SolicitudMultidia(poi_ids=ids + ids[:3], dias=3, horas_por_dia=6)
    r = planear_multidia(sol, catalogo)
    asignados = [p.poi_id for d in r.dias for p in d.paradas if p.poi_id in ids]
    assert len(asignados) == len(set(asignados))
    no_incl = [pid for pid, _ in r.no_incluidos]
    assert set(asignados) | set(no_incl) == set(ids)
    assert not set(asignados) & set(no_incl)
    assert all(m for _, m in r.no_incluidos)
    assert len(r.dias) == 3


def test_capacidad_por_dia(catalogo):
    ids = [p.poi_id for p in _atractivos(catalogo)]
    sol = SolicitudMultidia(poi_ids=ids, dias=2, horas_por_dia=4)
    r = planear_multidia(sol, catalogo)
    assert all(t <= 240 for t in r.metricas["tiempo_por_dia_min"])
    assert r.metricas["n_no_asignados"] > 0
    assert any("No cabe" in m for _, m in r.no_incluidos)


def test_restricciones_se_respetan_cada_dia(catalogo):
    por_id = {p.poi_id: p for p in catalogo}
    rng = random.Random(3)
    for _ in range(10):
        ids = rng.sample([p.poi_id for p in _atractivos(catalogo)], 14)
        sol = SolicitudMultidia(
            poi_ids=ids,
            dias=rng.choice([1, 2, 3]),
            horas_por_dia=rng.choice([4, 6, 8]),
            restricciones=Restricciones(
                sin_escalones=rng.random() < 0.6,
                banio_accesible=rng.random() < 0.4,
                descansos_cada_min=rng.choice([None, 30, 45]),
                pendiente_max_pct=rng.choice([None, 8.0]),
            ),
            dia_semana_inicio=rng.choice([None, 0, 4, 5]),
        )
        r = planear_multidia(sol, catalogo)
        _verificar_dias(r, sol, por_id)
        if sol.restricciones.sin_escalones:
            for d in r.dias:
                for p in d.paradas:
                    if p.poi_id in por_id:
                        assert "acceso_sin_escalones" in por_id[p.poi_id].accesibilidad


def test_sin_verificar_sale_con_motivo(catalogo):
    sin_dato = [
        p.poi_id for p in _atractivos(catalogo) if "acceso_sin_escalones" not in p.accesibilidad
    ][:3]
    sol = SolicitudMultidia(
        poi_ids=sin_dato, dias=1, horas_por_dia=6, restricciones=Restricciones(sin_escalones=True)
    )
    r = planear_multidia(sol, catalogo)
    assert [d.paradas for d in r.dias] == [[]]
    motivos = dict(r.no_incluidos)
    assert all("sin verificar" in motivos[pid] for pid in sin_dato)


def test_metricas_y_agrupamiento_mejoran_el_orden_ingenuo(catalogo):
    # Orden intercalado entre Puebla y Cholula: el peor caso del orden ingenuo.
    puebla = [p.poi_id for p in _atractivos(catalogo) if p.destino_id == "puebla"][:6]
    cholula = [p.poi_id for p in _atractivos(catalogo) if p.destino_id == "cholula"][:6]
    intercalado = [x for par in zip(puebla, cholula, strict=True) for x in par]
    sol = SolicitudMultidia(poi_ids=intercalado, dias=2, horas_por_dia=8)
    r = planear_multidia(sol, catalogo)
    m = r.metricas
    for clave in (
        "distancia_total_m",
        "distancia_orden_ingenuo_m",
        "cruces_entre_dias",
        "n_no_asignados",
        "n_no_asignados_orden_ingenuo",
    ):
        assert clave in m
    assert m["n_asignados"] >= m["n_asignados_orden_ingenuo"]
    # Cada día queda en una sola ciudad.
    for d in r.dias:
        destinos = {next(p for p in catalogo if p.poi_id == x.poi_id).destino_id
                    for x in d.paradas if x.poi_id in intercalado}  # fmt: skip
        assert len(destinos) <= 1


def test_alternativos_son_destinos_alternativos_no_seleccionados(catalogo):
    ids = [p.poi_id for p in _atractivos(catalogo) if p.destino_id == "puebla"][:5]
    r = planear_multidia(SolicitudMultidia(poi_ids=ids, dias=1, horas_por_dia=6), catalogo)
    por_id = {p.poi_id: p for p in catalogo}
    assert len(r.alternativos) <= 2
    for pid in r.alternativos:
        assert pid not in ids
        assert por_id[pid].es_destino_alternativo


def test_determinista(catalogo):
    ids = [p.poi_id for p in _atractivos(catalogo)][::3]
    sol = SolicitudMultidia(poi_ids=ids, dias=2, horas_por_dia=6)
    a = planear_multidia(sol, catalogo)
    b = planear_multidia(sol, list(reversed(catalogo)))
    assert [[p.poi_id for p in d.paradas] for d in a.dias] == [
        [p.poi_id for p in d.paradas] for d in b.dias
    ]


def test_id_desconocido_y_dias_invalidos(catalogo):
    r = planear_multidia(
        SolicitudMultidia(poi_ids=["no-existe"], dias=1, horas_por_dia=4), catalogo
    )
    assert dict(r.no_incluidos)["no-existe"] == "No está en el catálogo"
    with pytest.raises(ValueError):
        planear_multidia(SolicitudMultidia(poi_ids=[], dias=0, horas_por_dia=4), catalogo)


def test_atributo_reportado_excluye_en_multidia(catalogo):
    # syn-cen-01 tiene una barrera reportada después de su verificación.
    assert catalogo  # el catálogo de prueba existe
    r = planear_multidia(
        SolicitudMultidia(
            poi_ids=["syn-cen-01"],
            dias=1,
            horas_por_dia=6,
            restricciones=Restricciones(sin_escalones=True),
        ),
        catalogo,
    )
    assert [d.paradas for d in r.dias] == [[]]
    assert "barrera reportada" in dict(r.no_incluidos)["syn-cen-01"]
    assert AtributoAcc  # tipo exportado


def test_firma_del_endpoint_recomendar_multidia(catalogo):
    elegidos = [p for p in _atractivos(catalogo) if p.destino_id == "puebla"][:4]
    resto = [p for p in catalogo if p not in elegidos]
    r = recomendar_multidia(SolicitudMultidia(dias=2, horas_por_dia=5), elegidos, resto)
    assert [d.dia for d in r.dias] == [1, 2]
    asignados = {p.poi_id for d in r.dias for p in d.paradas}
    assert asignados <= {p.poi_id for p in catalogo}
    assert {p.poi_id for p in elegidos} == asignados | {n.poi_id for n in r.no_incluidos}
    assert r.explicacion and r.motor == "015-v1"
    assert all(n.motivo for n in r.no_incluidos)
