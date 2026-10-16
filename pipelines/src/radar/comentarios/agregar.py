"""Agregados por destino con supresión de celdas n < 5. Sin texto de comentarios."""

from __future__ import annotations

from collections import Counter

import pandas as pd

MIN_CELDA = 5
MIN_DESTINO = 30
COLUMNAS = ["destino_id", "tipo", "valor", "n", "proporcion"]


def opinion_agregada(clasificados: list[dict]) -> pd.DataFrame:
    filas = []
    por_destino: dict[str, list[dict]] = {}
    for c in clasificados:
        por_destino.setdefault(c["destino_id"], []).append(c)
    for destino, items in sorted(por_destino.items()):
        total = len(items)
        if total < MIN_DESTINO:
            continue
        for cat, n in Counter(i["categoria"] for i in items).items():
            if n >= MIN_CELDA:
                filas.append((destino, "categoria", cat, n, round(n / total, 4)))
        fricciones = [i for i in items if i["categoria"] == "friccion"]
        for sub, n in Counter(i["friccion"] or "otro" for i in fricciones).items():
            if n >= MIN_CELDA:
                filas.append((destino, "friccion", sub, n, round(n / len(fricciones), 4)))
    return pd.DataFrame(filas, columns=COLUMNAS)
