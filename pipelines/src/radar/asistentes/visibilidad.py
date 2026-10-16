"""Visibilidad de cada destino por segmento, con intervalo de Wilson al 95 %."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from radar.comun.estadistica import wilson

DIMENSIONES = ("proveedor", "idioma", "tono", "brazo")


def segmentos_de(corrida: dict) -> list[str]:
    """Segmentos a los que pertenece una corrida."""
    s = ["total"]
    s += [f"{d}={corrida[d]}" for d in DIMENSIONES]
    s.append(f"proveedor={corrida['proveedor']};idioma={corrida['idioma']}")
    return s


def calcular(corridas: Iterable[dict], menciones: dict[str, set[str]], destinos: list[str]):
    """`menciones` mapea corrida_id a los destinos mencionados en esa corrida."""
    n_por_segmento: dict[str, int] = {}
    k_por_segmento: dict[tuple[str, str], int] = {}
    for c in corridas:
        mencionados = menciones.get(c["corrida_id"], set())
        for segmento in segmentos_de(c):
            n_por_segmento[segmento] = n_por_segmento.get(segmento, 0) + 1
            for d in mencionados:
                k_por_segmento[(d, segmento)] = k_por_segmento.get((d, segmento), 0) + 1
    filas = []
    for segmento in sorted(n_por_segmento, key=lambda s: (s != "total", s)):
        n = n_por_segmento[segmento]
        for d in destinos:
            k = k_por_segmento.get((d, segmento), 0)
            bajo, alto = wilson(k, n)
            filas.append(
                {
                    "destino_id": d,
                    "segmento": segmento,
                    "n": n,
                    "k": k,
                    "visibilidad_pct": k / n * 100,
                    "ic95_bajo": bajo,
                    "ic95_alto": alto,
                }
            )
    return pd.DataFrame(filas)
