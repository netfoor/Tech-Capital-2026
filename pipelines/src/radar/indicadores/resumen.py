"""Resumen anual por centro turístico a partir de la tabla mensual."""

from __future__ import annotations

import pandas as pd

ADITIVOS = [
    "cuartos_disponibles",
    "cuartos_ocupados",
    "llegadas_turistas",
    "turistas_noche",
    "afluencia_visitantes",
    "derrama_mxn",
]


def anual(tabla: pd.DataFrame) -> pd.DataFrame:
    """Suma los indicadores aditivos por año y recalcula los cocientes con esas sumas.

    Solo se incluyen años con los 12 meses; los años parciales se marcan con `meses` < 12.
    """
    ancha = tabla.pivot_table(
        index=["centro_ot", "destino_id", "nivel", "anio", "mes"],
        columns="indicador",
        values="valor",
        aggfunc="first",
    ).reset_index()
    grupos = ancha.groupby(["centro_ot", "destino_id", "nivel", "anio"], dropna=False)
    suma = grupos[ADITIVOS].sum(min_count=1)
    suma["meses"] = grupos["mes"].nunique()
    suma = suma.reset_index()
    suma["ocupacion_pct"] = suma["cuartos_ocupados"] / suma["cuartos_disponibles"] * 100
    suma["estadia_promedio_dias"] = suma["turistas_noche"] / suma["llegadas_turistas"]
    suma["derrama_por_visitante_mxn"] = suma["derrama_mxn"] / suma["afluencia_visitantes"]
    suma["cuartos_libres_por_dia"] = (suma["cuartos_disponibles"] - suma["cuartos_ocupados"]) / (
        suma["meses"] * 365 / 12
    )
    return suma.sort_values(["anio", "afluencia_visitantes"], ascending=[True, False])


def participacion(anual_df: pd.DataFrame, anio: int) -> dict[str, float]:
    """Participación de la capital y de los 12 Pueblos Mágicos en la afluencia estatal."""
    del_anio = anual_df[anual_df["anio"] == anio]
    estado = del_anio.loc[del_anio["centro_ot"] == "Estado", "afluencia_visitantes"].sum()
    capital = del_anio.loc[del_anio["destino_id"] == "puebla", "afluencia_visitantes"].sum()
    return {"estado": estado, "capital": capital, "capital_pct": capital / estado * 100}
