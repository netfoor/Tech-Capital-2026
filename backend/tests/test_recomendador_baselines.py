from pathlib import Path

import pytest

from app.recommender import Restricciones, SolicitudRuta, recomendar
from app.recommender.baselines import BASELINES
from app.recommender.carga import cargar_catalogo
from app.recommender.verificador import verificar, violaciones_indispensables

DATOS = Path(__file__).parent / "datos"
CENTRO = (19.0433, -98.1981)


@pytest.fixture(scope="module")
def catalogo():
    return cargar_catalogo(DATOS / "poi_sintetico.csv", DATOS / "poi_accesibilidad_sintetico.csv")


@pytest.mark.parametrize("nombre", sorted(BASELINES))
def test_baselines_corren_y_respetan_tiempo(nombre, catalogo):
    s = SolicitudRuta(horas_disponibles=4, punto_partida=CENTRO)
    r = BASELINES[nombre](s, catalogo)
    assert r.paradas
    assert r.metricas["tiempo_usado_min"] <= 240
    tipos = {v.tipo for v in verificar(r, s, {p.poi_id: p for p in catalogo})}
    assert "tiempo" not in tipos and "horario" not in tipos


def test_el_verificador_detecta_violaciones_de_las_baselines(catalogo):
    por_id = {p.poi_id: p for p in catalogo}
    s = SolicitudRuta(
        horas_disponibles=4,
        punto_partida=CENTRO,
        restricciones=Restricciones(sin_escalones=True, descansos_cada_min=30),
    )
    total_baselines = sum(
        len(violaciones_indispensables(verificar(f(s, catalogo), s, por_id)))
        for f in BASELINES.values()
    )
    assert total_baselines > 0
    assert violaciones_indispensables(verificar(recomendar(s, catalogo), s, por_id)) == []


def test_cercania_ordena_por_distancia(catalogo):
    s = SolicitudRuta(horas_disponibles=1, punto_partida=CENTRO)
    r = BASELINES["cercania"](s, catalogo)
    assert r.paradas
    assert r.paradas[0].traslado_min <= 10
