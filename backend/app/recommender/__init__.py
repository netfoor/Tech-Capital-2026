"""Recomendador inclusivo de itinerarios (spec 015).

Paquete puro: no usa base de datos ni FastAPI. La API (spec 014) lo consume con:

    recomendar(solicitud: SolicitudRuta, pois: list[POICandidato]) -> RespuestaRuta
    recomendar_multidia(solicitud: SolicitudMultidia, pois: list[POICandidato],
                        alternativas: list[POICandidato]) -> RespuestaMultidia

``planear_multidia(solicitud, catalogo)`` es la forma directa con ``solicitud.poi_ids``.
"""

from .motor import VERSION, recomendar
from .multidia import planear_multidia, recomendar_multidia
from .tipos import (
    AtributoAcc,
    AtributoAcceso,
    DiaPlan,
    NoIncluido,
    Parada,
    POICandidato,
    RespuestaMultidia,
    RespuestaRuta,
    Restricciones,
    SolicitudMultidia,
    SolicitudRuta,
)

MOTOR = VERSION

__all__ = [
    "MOTOR",
    "AtributoAcc",
    "AtributoAcceso",
    "DiaPlan",
    "NoIncluido",
    "POICandidato",
    "Parada",
    "RespuestaMultidia",
    "RespuestaRuta",
    "Restricciones",
    "SolicitudMultidia",
    "SolicitudRuta",
    "planear_multidia",
    "recomendar",
    "recomendar_multidia",
]
