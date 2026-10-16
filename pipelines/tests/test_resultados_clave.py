"""Resultados clave de los indicadores oficiales (T002-06): si cambian, algo se rompió."""

import pandas as pd
import pytest

from radar import config


@pytest.fixture(scope="module")
def anual():
    return pd.read_csv(config.ruta(config.CURADO, "indicadores_oficiales_anual.csv"))


def test_participacion_en_la_afluencia_estatal_2025(anual):
    a = anual[(anual["anio"] == 2025) & (anual["meses"] == 12)]
    estado = a[a["nivel"] == "agregado"]["afluencia_visitantes"].iloc[0]
    capital = a[a["destino_id"] == "puebla"]["afluencia_visitantes"].iloc[0]
    destinos = pd.read_csv(config.ruta(config.REFERENCIA, "destinos.csv"))
    pueblos = set(destinos.loc[destinos["pueblo_magico"], "destino_id"])
    pm = a[a["destino_id"].isin(pueblos) & (a["nivel"] == "destino")]["afluencia_visitantes"].sum()
    assert capital / estado * 100 == pytest.approx(59.9, abs=0.05)
    assert pm / estado * 100 == pytest.approx(28.8, abs=0.05)


def test_factor_de_afluencia_de_cuetzalan():
    f = pd.read_csv(config.ruta(config.CURADO, "factor_afluencia_por_centro.csv"))
    fila = f[f["centro_ot"] == "Cuetzalan"].iloc[0]
    assert fila["factor_mas_frecuente"] == pytest.approx(2.222)
    assert fila["proporcion_desde_2019"] == pytest.approx(1.0)
