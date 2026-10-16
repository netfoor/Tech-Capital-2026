import pandas as pd
import pytest

from radar import catalogo, config, fuentes
from radar.indicadores import sectur_ot


def test_fuentes_coinciden_con_su_huella():
    assert fuentes.verificar() == []


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("Cuartos disponibles", "cuartos_disponibles"),
        ("rCousartos disponibles", "cuartos_disponibles"),
        ("lDucearrnama económica", "derrama_mxn"),
        ("aPorcentaje de ocupación", "ocupacion_pct"),
    ],
)
def test_corrige_indicadores_mezclados(texto, esperado):
    assert sectur_ot._indicador(texto).indicador_id == esperado


@pytest.mark.parametrize(
    ("centro_pdf", "centro_ot", "nivel"),
    [
        ("Cd.Puebla", "Ciudad de Puebla", "destino"),
        ("Izúcar de Matamo", "Izúcar de Matamoros", "destino"),
        ("San Andrés Cholul", "San Andrés Cholula", "subcentro"),
        ("Estado", "Estado", "agregado"),
    ],
)
def test_resuelve_nombres_cortados(centro_pdf, centro_ot, nivel):
    por_centro = catalogo.por_centro_ot(catalogo.cargar())
    resuelto = sectur_ot._resolver_centro(centro_pdf, por_centro)
    assert resuelto[0] == centro_ot
    assert resuelto[2] == nivel


def test_numero_vacio_es_faltante():
    assert sectur_ot._numero("") is None
    assert sectur_ot._numero("20,894.00") == 20894.0


@pytest.fixture(scope="module")
def mensual() -> pd.DataFrame:
    ruta = config.ruta(config.CURADO, "indicadores_oficiales_mensual.csv")
    if not ruta.exists():
        pytest.skip("Ejecuta `uv run radar indicadores` primero")
    return pd.read_csv(ruta)


def test_tabla_curada_cubre_los_doce_pueblos(mensual):
    pm = {d.destino_id for d in catalogo.cargar() if d.pueblo_magico}
    assert pm <= set(mensual["destino_id"].dropna())


def test_procedencia_segun_glosario(mensual):
    derivados = set(mensual.loc[mensual["procedencia"] == "derivado", "indicador"])
    assert derivados == {"afluencia_visitantes", "derrama_mxn"}


def test_sin_meses_no_publicados(mensual):
    assert mensual["periodo"].max() <= "2026-06"
    ultimo = mensual[mensual["periodo"] == mensual["periodo"].max()]
    assert (ultimo.loc[ultimo["indicador"] == "llegadas_turistas", "valor"] > 0).all()


def test_llave_unica(mensual):
    llave = ["centro_ot", "indicador", "anio", "mes"]
    assert not mensual.duplicated(llave).any()
