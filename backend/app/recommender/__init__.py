"""Recomendador inclusivo de itinerarios (spec 015).

Paquete puro: no usa base de datos ni FastAPI. La spec 014 lo consume con
``recomendar()`` y ``planear_multidia()``.
"""

from .motor import recomendar
from .multidia import planear_multidia
from .tipos import (
    AtributoAcc,
    Parada,
    POICandidato,
    RespuestaMultidia,
    RespuestaRuta,
    Restricciones,
    SolicitudMultidia,
    SolicitudRuta,
)

__all__ = [
    "AtributoAcc",
    "POICandidato",
    "Parada",
    "RespuestaMultidia",
    "RespuestaRuta",
    "Restricciones",
    "SolicitudMultidia",
    "SolicitudRuta",
    "planear_multidia",
    "recomendar",
]
