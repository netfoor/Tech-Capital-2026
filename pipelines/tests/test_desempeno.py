import pandas as pd
import pytest

from radar import config
from radar.radar import desempeno


def serie(destino, indicador, valores, desde="2024-07"):
    filas = []
    periodo = desde
    for v in valores:
        filas.append(
            {
                "destino_id": destino,
                "nivel": "destino",
                "periodo": periodo,
                "indicador": indicador,
                "valor": v,
            }
        )
        periodo = desempeno._sumar_meses(periodo, 1)
    return filas


def juguete():
    filas = []
    filas += serie("x", "cuartos_disponibles", [100] * 24)
    filas += serie("x", "cuartos_ocupados", [50] * 12 + [60] * 12)
    filas += serie("x", "llegadas_turistas", [10] * 12 + [15] * 12)
    return pd.DataFrame(filas)


def test_periodo_de_referencia_son_los_ultimos_12_meses():
    assert desempeno.periodo_referencia(juguete()) == ("2025-07", "2026-06")


def test_metricas_con_numeros_de_juguete():
    r = desempeno.calcular(juguete(), ["x"]).iloc[0]
    assert r["ocupacion_12m"] == pytest.approx(60.0)
    assert r["llegadas_12m"] == 180
    assert r["crecimiento_llegadas_pct"] == pytest.approx(50.0)
    # (100-60)*12 cuartos libres entre 365 días
    assert r["cuartos_libres_dia_12m"] == pytest.approx(480 / 365)
    assert r["notas"] == ""


def test_destino_con_meses_faltantes_se_anota():
    df = juguete()
    df = df[~((df["indicador"] == "cuartos_ocupados") & (df["periodo"] == "2026-01"))]
    r = desempeno.calcular(df, ["x"]).iloc[0]
    assert "11 de 12" in r["notas"]


def test_sin_serie_previa_no_hay_crecimiento():
    df = juguete()
    df = df[df["periodo"] >= "2025-07"]
    r = desempeno.calcular(df, ["x"]).iloc[0]
    assert pd.isna(r["crecimiento_llegadas_pct"])
    assert "crecimiento" in r["notas"]


def test_cuetzalan_coincide_con_el_calculo_manual_del_csv():
    ruta = config.ruta(config.CURADO, "indicadores_oficiales_mensual.csv")
    if not ruta.exists():
        pytest.skip("Ejecuta `uv run radar indicadores` primero")
    mensual = pd.read_csv(ruta)
    r = desempeno.calcular(mensual, ["cuetzalan"]).iloc[0]
    sub = mensual[
        (mensual["destino_id"] == "cuetzalan")
        & (mensual["nivel"] == "destino")
        & (mensual["periodo"] >= "2025-07")
    ]
    ocupados = sub[sub["indicador"] == "cuartos_ocupados"]["valor"].sum()
    disponibles = sub[sub["indicador"] == "cuartos_disponibles"]["valor"].sum()
    assert r["ocupacion_12m"] == pytest.approx(ocupados / disponibles * 100)
    assert r["periodo_ref"] == "2026-06"
