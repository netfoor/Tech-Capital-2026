"""Desempeño turístico de cada destino en el periodo de referencia (últimos 12 meses publicados)."""

from __future__ import annotations

import calendar

import pandas as pd


def _sumar_meses(periodo: str, meses: int) -> str:
    anio, mes = (int(p) for p in periodo.split("-"))
    indice = anio * 12 + (mes - 1) + meses
    return f"{indice // 12:04d}-{indice % 12 + 1:02d}"


def periodo_referencia(mensual: pd.DataFrame) -> tuple[str, str]:
    """(desde, hasta) de los últimos 12 meses publicados en la serie de destinos."""
    hasta = str(mensual.loc[mensual["nivel"] == "destino", "periodo"].max())
    return _sumar_meses(hasta, -11), hasta


def _dias(desde: str, hasta: str) -> int:
    total = 0
    actual = desde
    while actual <= hasta:
        anio, mes = (int(p) for p in actual.split("-"))
        total += calendar.monthrange(anio, mes)[1]
        actual = _sumar_meses(actual, 1)
    return total


def calcular(mensual: pd.DataFrame, destinos: list[str]) -> pd.DataFrame:
    """Métricas de desempeño por destino. Solo usa valores medidos de la serie mensual."""
    desde, hasta = periodo_referencia(mensual)
    previo_desde, previo_hasta = _sumar_meses(desde, -12), _sumar_meses(hasta, -12)
    dias = _dias(desde, hasta)
    base = mensual[mensual["nivel"] == "destino"]

    def suma(destino: str, indicador: str, d: str, h: str) -> tuple[float, int]:
        filas = base[
            (base["destino_id"] == destino)
            & (base["indicador"] == indicador)
            & (base["periodo"] >= d)
            & (base["periodo"] <= h)
        ]
        return float(filas["valor"].sum()), int(filas["valor"].notna().sum())

    filas = []
    for destino in destinos:
        ocupados, n_ocupados = suma(destino, "cuartos_ocupados", desde, hasta)
        disponibles, n_disponibles = suma(destino, "cuartos_disponibles", desde, hasta)
        llegadas, n_llegadas = suma(destino, "llegadas_turistas", desde, hasta)
        llegadas_previas, n_previas = suma(destino, "llegadas_turistas", previo_desde, previo_hasta)
        notas = []
        meses = min(n_ocupados, n_disponibles)
        if meses < 12:
            notas.append(f"Desempeño con {meses} de 12 meses del periodo de referencia")
        crecimiento = None
        if n_llegadas == 12 and n_previas == 12 and llegadas_previas > 0:
            crecimiento = (llegadas / llegadas_previas - 1) * 100
        else:
            notas.append("Sin 12 meses previos para el crecimiento de llegadas")
        filas.append(
            {
                "destino_id": destino,
                "periodo_ref_desde": desde,
                "periodo_ref": hasta,
                "ocupacion_12m": ocupados / disponibles * 100 if disponibles else None,
                "cuartos_libres_dia_12m": (disponibles - ocupados) / dias if disponibles else None,
                "llegadas_12m": int(round(llegadas)) if n_llegadas else None,
                "crecimiento_llegadas_pct": crecimiento,
                "meses_desempeno": meses,
                "notas": "; ".join(notas),
            }
        )
    return pd.DataFrame(filas)
