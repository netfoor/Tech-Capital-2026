"""Percentiles con empates e intervalo de Wilson, compartidos por los contextos."""

from __future__ import annotations

import math
from collections.abc import Sequence

Z_95 = 1.959964


def percentiles(valores: Sequence[float | None]) -> list[float | None]:
    """Percentil de cada valor entre los no nulos: `(rango - 1) / (n - 1) × 100`.

    Los empates reciben el rango promedio. Los valores nulos (o NaN) se quedan en `None` y
    no cuentan para `n`. Con menos de dos valores no hay percentil y todo queda en `None`.
    """
    presentes = [
        (i, float(v)) for i, v in enumerate(valores) if v is not None and not math.isnan(float(v))
    ]
    resultado: list[float | None] = [None] * len(valores)
    n = len(presentes)
    if n < 2:
        return resultado
    orden = sorted(presentes, key=lambda p: p[1])
    j = 0
    while j < n:
        k = j
        while k + 1 < n and orden[k + 1][1] == orden[j][1]:
            k += 1
        rango = (j + 1 + k + 1) / 2  # rango promedio de los empatados (base 1)
        pctl = (rango - 1) / (n - 1) * 100
        for m in range(j, k + 1):
            resultado[orden[m][0]] = pctl
        j = k + 1
    return resultado


def mediana(valores: Sequence[float]) -> float:
    ordenados = sorted(valores)
    n = len(ordenados)
    if n == 0:
        raise ValueError("No hay valores para calcular la mediana")
    medio = n // 2
    return ordenados[medio] if n % 2 else (ordenados[medio - 1] + ordenados[medio]) / 2


def wilson(exitos: int, total: int, z: float = Z_95) -> tuple[float, float]:
    """Intervalo de Wilson para una proporción, en porcentaje (0–100).

    Con `total = 0` no hay información y el intervalo es todo el rango.
    """
    if total < 0 or exitos < 0 or exitos > total:
        raise ValueError("Se requiere 0 <= éxitos <= total")
    if total == 0:
        return 0.0, 100.0
    p = exitos / total
    z2 = z * z
    centro = (p + z2 / (2 * total)) / (1 + z2 / total)
    margen = z * math.sqrt(p * (1 - p) / total + z2 / (4 * total * total)) / (1 + z2 / total)
    return max(0.0, centro - margen) * 100, min(1.0, centro + margen) * 100
