"""Zonas de consulta: el corredor piloto y los centros de los Pueblos Mágicos.

Los centros salen de las cabeceras municipales de INEGI (`destinos.csv`, fuente
`inegi-cabeceras`). San Andrés Cholula no es un destino propio del catálogo (pertenece a
`cholula`), así que su cabecera se fija aquí con el dato del mismo servicio de INEGI.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from radar import catalogo, geo

CORREDOR_ID = "puebla-cholula"
RADIO_PUEBLO_MAGICO_M = 1500
RADIO_CENTRO_CORREDOR_M = 1200

# INEGI, localidad 211190001 (San Andrés Cholula), consultada el 2026-10-16.
CABECERA_SAN_ANDRES = (19.0509439, -98.3006556)


@dataclass(frozen=True)
class Corredor:
    corredor_id: str
    nombre: str
    descripcion: str
    lat_min: float
    lon_min: float
    lat_max: float
    lon_max: float
    municipios: tuple[str, ...]

    def contiene(self, lat: float, lon: float) -> bool:
        return self.lat_min <= lat <= self.lat_max and self.lon_min <= lon <= self.lon_max


CORREDOR = Corredor(
    corredor_id=CORREDOR_ID,
    nombre="Centro Histórico de Puebla → San Pedro y San Andrés Cholula",
    descripcion=(
        "Corredor piloto entre el polo más visitado del estado (Centro Histórico de Puebla) "
        "y Cholula (San Pedro y San Andrés Cholula), a unos 12 km al poniente."
    ),
    lat_min=19.0300,
    lon_min=-98.3150,
    lat_max=19.0720,
    lon_max=-98.1850,
    municipios=("21114", "21119", "21140"),
)


@dataclass(frozen=True)
class Centro:
    """Un círculo de consulta."""

    zona_id: str
    destino_id: str
    lat: float
    lon: float
    radio_m: int

    def contiene(self, lat: float, lon: float) -> bool:
        return geo.distancia_m(self.lat, self.lon, lat, lon) <= self.radio_m


@lru_cache(maxsize=1)
def centros_corredor() -> tuple[Centro, ...]:
    """Centros del corredor donde se piden alimentos, baños, bancas y artesanías."""
    destinos = {d.destino_id: d for d in catalogo.cargar()}
    puebla, cholula = destinos["puebla"], destinos["cholula"]
    return (
        Centro("puebla-centro", "puebla", puebla.lat, puebla.lon, RADIO_CENTRO_CORREDOR_M),
        Centro("san-pedro-cholula", "cholula", cholula.lat, cholula.lon, RADIO_CENTRO_CORREDOR_M),
        Centro("san-andres-cholula", "cholula", *CABECERA_SAN_ANDRES, RADIO_CENTRO_CORREDOR_M),
    )


@lru_cache(maxsize=1)
def centros_pueblos_magicos() -> tuple[Centro, ...]:
    """Un círculo por Pueblo Mágico. Cholula ya está cubierto por el corredor."""
    return tuple(
        Centro(d.destino_id, d.destino_id, d.lat, d.lon, RADIO_PUEBLO_MAGICO_M)
        for d in sorted(catalogo.cargar(), key=lambda d: d.destino_id)
        if d.pueblo_magico and d.destino_id != "cholula"
    )


def zona_de(lat: float, lon: float) -> tuple[str, str]:
    """(corredor_id, destino_id de la zona) del punto; cadenas vacías si no cae en ninguna."""
    if CORREDOR.contiene(lat, lon):
        return CORREDOR_ID, ""
    for c in centros_pueblos_magicos():
        if c.contiene(lat, lon):
            return "", c.destino_id
    return "", ""


def en_alguna_zona(lat: float, lon: float) -> bool:
    return zona_de(lat, lon) != ("", "")
