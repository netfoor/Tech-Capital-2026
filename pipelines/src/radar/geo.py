"""Geometría mínima: distancia, punto en polígono y límites de INEGI.

Sin dependencias geoespaciales: los límites vienen en GeoJSON simplificado
(`data/referencia/geo/`) y basta con un algoritmo de cruce de rayos.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from radar import config

RADIO_TIERRA_M = 6_371_008.8

Anillo = list[tuple[float, float]]  # (lon, lat)


def distancia_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia haversine en metros."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * RADIO_TIERRA_M * math.asin(math.sqrt(a))


def _en_anillo(lon: float, lat: float, anillo: Anillo) -> bool:
    dentro = False
    j = len(anillo) - 1
    for i in range(len(anillo)):
        xi, yi = anillo[i]
        xj, yj = anillo[j]
        if (yi > lat) != (yj > lat):
            x = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < x:
                dentro = not dentro
        j = i
    return dentro


@dataclass(frozen=True)
class Area:
    """Un polígono o multipolígono con su caja envolvente."""

    clave: str
    nombre: str
    poligonos: tuple[tuple[Anillo, ...], ...]  # cada polígono: exterior + huecos
    caja: tuple[float, float, float, float]  # lon_min, lat_min, lon_max, lat_max

    def contiene(self, lat: float, lon: float) -> bool:
        x0, y0, x1, y1 = self.caja
        if not (x0 <= lon <= x1 and y0 <= lat <= y1):
            return False
        for poligono in self.poligonos:
            exterior, *huecos = poligono
            if _en_anillo(lon, lat, exterior) and not any(_en_anillo(lon, lat, h) for h in huecos):
                return True
        return False


def _area(clave: str, nombre: str, geometria: dict) -> Area:
    coords = geometria["coordinates"]
    if geometria["type"] == "Polygon":
        coords = [coords]
    poligonos = tuple(
        tuple([(float(p[0]), float(p[1])) for p in anillo] for anillo in poligono)
        for poligono in coords
    )
    xs = [p[0] for pol in poligonos for p in pol[0]]
    ys = [p[1] for pol in poligonos for p in pol[0]]
    return Area(clave, nombre, poligonos, (min(xs), min(ys), max(xs), max(ys)))


def leer_areas(ruta: Path, clave: str = "cvegeo", nombre: str = "nomgeo") -> list[Area]:
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    if datos["type"] == "GeometryCollection":
        return [_area(str(i), "", g) for i, g in enumerate(datos["geometries"])]
    areas = []
    for i, f in enumerate(datos["features"]):
        props = f.get("properties") or {}
        areas.append(_area(str(props.get(clave, i)), str(props.get(nombre, "")), f["geometry"]))
    return areas


@lru_cache(maxsize=1)
def municipios() -> tuple[Area, ...]:
    return tuple(leer_areas(config.ruta(config.REFERENCIA, "geo", "municipios-puebla.geojson")))


@lru_cache(maxsize=1)
def estado() -> tuple[Area, ...]:
    return tuple(leer_areas(config.ruta(config.REFERENCIA, "geo", "estado-puebla.geojson")))


def en_puebla(lat: float, lon: float) -> bool:
    return any(a.contiene(lat, lon) for a in estado())


def municipio_de(lat: float, lon: float) -> str:
    """Clave INEGI del municipio que contiene el punto; vacía si ninguno."""
    for a in municipios():
        if a.contiene(lat, lon):
            return a.clave
    return ""
