"""Registros sin coordenadas (§14).

La API registra método, ruta sin parámetros, código y duración; nunca cuerpos ni query strings.
Además, un filtro oculta cualquier número con forma de coordenada que llegue a un mensaje.
"""

import logging
import re
import time
from collections.abc import Awaitable, Callable

from starlette.requests import Request
from starlette.responses import Response

# Decimales con 4 o más cifras (≈ 11 m de precisión o mejor): latitudes y longitudes.
PATRON_COORDENADA = re.compile(r"-?\d{1,3}\.\d{4,}")
OCULTO = "[coordenada oculta]"

registro_api = logging.getLogger("puebla_viva.api")


def ocultar_coordenadas(texto: str) -> str:
    return PATRON_COORDENADA.sub(OCULTO, texto)


class FiltroCoordenadas(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        mensaje = ocultar_coordenadas(record.getMessage())
        record.msg, record.args = mensaje, None
        return True


def configurar() -> None:
    # Los filtros de un logger no se heredan: se ponen en cada logger que emite.
    for nombre in ("puebla_viva", "puebla_viva.api", "uvicorn.access", "uvicorn.error"):
        logger = logging.getLogger(nombre)
        if not any(isinstance(f, FiltroCoordenadas) for f in logger.filters):
            logger.addFilter(FiltroCoordenadas())
    raiz = logging.getLogger("puebla_viva")
    if raiz.level == logging.NOTSET:
        raiz.setLevel(logging.INFO)


async def registrar_peticion(
    peticion: Request, siguiente: Callable[[Request], Awaitable[Response]]
) -> Response:
    inicio = time.perf_counter()
    respuesta = await siguiente(peticion)
    duracion = (time.perf_counter() - inicio) * 1000
    registro_api.info(
        "%s %s %s %.1fms",
        peticion.method,
        peticion.url.path,
        respuesta.status_code,
        duracion,
    )
    return respuesta
