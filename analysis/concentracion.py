"""Medidas de concentración para el análisis del problema (spec 013).

Funciones puras, sin dependencias del resto del análisis, para poder probarlas
contra un cálculo a mano.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd


def _valores(valores: Iterable[float]) -> np.ndarray:
    x = np.asarray(list(valores), dtype=float)
    if x.size == 0:
        raise ValueError("Se necesita al menos un valor")
    if np.isnan(x).any():
        raise ValueError("Hay valores vacíos")
    if (x < 0).any():
        raise ValueError("Los valores no pueden ser negativos")
    if x.sum() == 0:
        raise ValueError("La suma de los valores es cero")
    return x


def participaciones(valores: pd.Series) -> pd.Series:
    """Participación de cada elemento en el total (escala 0–1)."""
    x = _valores(valores)
    return pd.Series(x / x.sum(), index=valores.index, name="participacion")


def hhi(valores: Iterable[float]) -> float:
    """Índice de Herfindahl-Hirschman en escala 0–1: suma de participaciones al cuadrado.

    Multiplicado por 10,000 da la escala usual (0–10,000).
    """
    x = _valores(valores)
    s = x / x.sum()
    return float((s**2).sum())


def gini(valores: Iterable[float]) -> float:
    """Coeficiente de Gini (0 = reparto igual; tiende a 1 = todo en uno).

    G = 2·Σ(i·x_i) / (n·Σx) − (n + 1)/n, con x ordenado de menor a mayor e i = 1..n.
    """
    x = np.sort(_valores(valores))
    n = x.size
    i = np.arange(1, n + 1)
    return float(2 * (i * x).sum() / (n * x.sum()) - (n + 1) / n)
