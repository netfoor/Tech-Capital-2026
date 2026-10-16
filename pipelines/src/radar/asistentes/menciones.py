"""Menciones de destinos en las respuestas: por términos y, en ko y zh, con un extractor."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass

from radar import catalogo
from radar.catalogo import Destino

IDIOMAS_CON_EXTRACTOR = ("ko", "zh")


@dataclass(frozen=True)
class Mencion:
    destino_id: str
    orden: int
    metodo: str  # «terminos» o «extractor»


def instruccion_extractor(texto: str, destinos: list[Destino]) -> str:
    catalogo_texto = "\n".join(f"- {d.destino_id}: {d.nombre}" for d in destinos)
    return (
        "Eres un anotador. Lee la respuesta de un asistente de viajes y di cuáles destinos del "
        "catálogo menciona de forma explícita, aunque estén escritos en otro alfabeto "
        "(coreano o chino) o transliterados.\n"
        "Reglas: incluye `puebla` solo si la respuesta habla de la ciudad de Puebla (su centro "
        "histórico, la capital); no lo incluyas si solo nombra al estado. Incluye un destino "
        "solo si el texto lo nombra; no lo deduzcas.\n"
        f"Catálogo (destino_id: nombre):\n{catalogo_texto}\n\n"
        'Responde solo con JSON: {"destinos": ["destino_id", ...]}.\n\n'
        f"Respuesta a anotar:\n{texto}"
    )


def leer_respuesta_extractor(salida: str, destinos: list[Destino]) -> list[str]:
    """Ids válidos del JSON devuelto por el extractor; ignora lo que no esté en el catálogo."""
    coincidencia = re.search(r"\{.*\}", salida, flags=re.DOTALL)
    if not coincidencia:
        return []
    try:
        datos = json.loads(coincidencia.group(0))
    except json.JSONDecodeError:
        return []
    validos = {d.destino_id for d in destinos}
    vistos: list[str] = []
    for d in datos.get("destinos", []):
        if d in validos and d not in vistos:
            vistos.append(d)
    return vistos


def extraer(texto: str, destinos: list[Destino], llamar: Callable[[str], str]) -> list[str]:
    return leer_respuesta_extractor(llamar(instruccion_extractor(texto, destinos)), destinos)


def menciones_de_respuesta(
    texto: str,
    idioma: str,
    destinos: list[Destino],
    terminos_idiomas: dict[tuple[str, str], tuple[str, ...]] | None = None,
    extraidos: list[str] | None = None,
) -> list[Mencion]:
    """Menciones por términos y, para lo que solo halló el extractor, al final."""
    por_terminos = catalogo.detectar(texto, idioma, destinos, terminos_idiomas)
    menciones = [Mencion(m.destino_id, i + 1, "terminos") for i, m in enumerate(por_terminos)]
    vistos = {m.destino_id for m in menciones}
    for destino_id in extraidos or []:
        if destino_id not in vistos:
            vistos.add(destino_id)
            menciones.append(Mencion(destino_id, len(menciones) + 1, "extractor"))
    return menciones
