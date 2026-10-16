"""Acuerdo entre personas y clasificador (κ de Cohen) y matriz de confusión."""

from __future__ import annotations

from collections import Counter


def kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    if n == 0 or n != len(b):
        raise ValueError("Las listas deben tener el mismo largo y no estar vacías")
    observado = sum(x == y for x, y in zip(a, b, strict=True)) / n
    ca, cb = Counter(a), Counter(b)
    esperado = sum(ca[k] * cb[k] for k in ca) / (n * n)
    return 1.0 if esperado == 1 else (observado - esperado) / (1 - esperado)


def matriz(real: list[str], predicho: list[str]) -> dict[str, dict[str, int]]:
    m: dict[str, dict[str, int]] = {}
    for r, p in zip(real, predicho, strict=True):
        m.setdefault(r, {}).setdefault(p, 0)
        m[r][p] += 1
    return m


def informe(persona_a: list[str], persona_b: list[str], consenso: list[str], clasif: list[str]):
    k = kappa(clasif, consenso)
    return {
        "n": len(consenso),
        "kappa_entre_personas": round(kappa(persona_a, persona_b), 3),
        "kappa_clasificador": round(k, 3),
        "cumple_umbral": k >= 0.6,
        "matriz_confusion": matriz(consenso, clasif),
    }
