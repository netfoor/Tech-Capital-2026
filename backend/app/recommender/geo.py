"""Geometría mínima: distancias, tiempos peatonales y zonas.

Limitación: la distancia es en línea recta (haversine) multiplicada por un
factor de desvío. No usa la red peatonal real; OSMnx queda como mejora.
"""

from __future__ import annotations

import math

from .config import CONFIG_DEFECTO, Config

RADIO_TIERRA_M = 6_371_000.0


def haversine_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * RADIO_TIERRA_M * math.asin(min(1.0, math.sqrt(h)))


def distancia_caminable_m(
    a: tuple[float, float], b: tuple[float, float], config: Config = CONFIG_DEFECTO
) -> float:
    return haversine_m(a, b) * config.factor_desvio


def minutos_caminando(
    a: tuple[float, float], b: tuple[float, float], config: Config = CONFIG_DEFECTO
) -> int:
    metros_por_min = config.velocidad_kmh * 1000 / 60
    return math.ceil(distancia_caminable_m(a, b, config) / metros_por_min)


def zona(lat: float, lon: float, config: Config = CONFIG_DEFECTO) -> str:
    """Celda de ``tamano_zona_m`` metros, estable y sin dependencias."""
    paso_lat = config.tamano_zona_m / 111_320.0
    paso_lon = config.tamano_zona_m / (111_320.0 * math.cos(math.radians(lat)) or 1.0)
    return f"{math.floor(lat / paso_lat)}:{math.floor(lon / paso_lon)}"


def segmentos_se_cruzan(
    p1: tuple[float, float],
    p2: tuple[float, float],
    q1: tuple[float, float],
    q2: tuple[float, float],
) -> bool:
    """Cruce propio de dos segmentos en el plano (lat, lon)."""

    def orient(a, b, c) -> float:
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    d1 = orient(q1, q2, p1)
    d2 = orient(q1, q2, p2)
    d3 = orient(p1, p2, q1)
    d4 = orient(p1, p2, q2)
    return (d1 * d2 < 0) and (d3 * d4 < 0)
