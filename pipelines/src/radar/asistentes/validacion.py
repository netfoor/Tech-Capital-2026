"""Validación manual de la detección de menciones (T006-11): muestra y métricas."""

from __future__ import annotations

import random
from collections import defaultdict

SEMILLA = 11
POR_IDIOMA = 12
COLUMNAS = [
    "corrida_id",
    "idioma",
    "proveedor",
    "prompt",
    "respuesta",
    "detectados",
    "sobran",
    "faltan",
    "notas",
]


def muestra(
    corridas: list[dict],
    menciones: dict[str, list[str]],
    nombres: dict[str, str],
    por_idioma: int = POR_IDIOMA,
    semilla: int = SEMILLA,
) -> list[dict]:
    """Muestra estratificada por idioma (12 × 5 = 60) con los destinos detectados por nombre."""
    azar = random.Random(semilla)
    por: dict[str, list[dict]] = defaultdict(list)
    for c in corridas:
        por[c["idioma"]].append(c)
    filas = []
    for idioma in sorted(por):
        for c in azar.sample(por[idioma], min(por_idioma, len(por[idioma]))):
            ids = menciones.get(c["corrida_id"], [])
            filas.append(
                {
                    "corrida_id": c["corrida_id"],
                    "idioma": idioma,
                    "proveedor": c["proveedor"],
                    "prompt": c["prompt"],
                    "respuesta": c["texto"],
                    "detectados": " | ".join(nombres.get(i, i) for i in ids),
                    "sobran": "",
                    "faltan": "",
                    "notas": "",
                }
            )
    return filas


def _lista(valor: str) -> set[str]:
    return {v.strip().lower() for v in str(valor or "").split("|") if v.strip()}


def metricas(filas: list[dict]) -> dict:
    """Precisión y exhaustividad a partir de lo que la persona marcó como sobrante o faltante.

    `sobran` y `faltan` usan los mismos nombres que `detectados`, separados con «|».
    """
    vp = fp = fn = 0
    for f in filas:
        detectados = _lista(f["detectados"])
        sobran = _lista(f["sobran"]) & detectados
        vp += len(detectados) - len(sobran)
        fp += len(sobran)
        fn += len(_lista(f["faltan"]) - detectados)
    precision = vp / (vp + fp) if vp + fp else 1.0
    exhaustividad = vp / (vp + fn) if vp + fn else 1.0
    return {
        "respuestas": len(filas),
        "verdaderos_positivos": vp,
        "falsos_positivos": fp,
        "falsos_negativos": fn,
        "precision": round(precision, 3),
        "exhaustividad": round(exhaustividad, 3),
    }
