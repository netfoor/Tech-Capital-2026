"""Dominio y tipo de dominio de las fuentes que citan los asistentes."""

from __future__ import annotations

import csv
from pathlib import Path
from urllib.parse import urlparse

from radar import config

REDIRECCIONES = ("vertexaisearch.cloud.google.com",)
TIPOS = {
    "gobierno",
    "medio",
    "blog",
    "agencia_viajes",
    "red_social",
    "enciclopedia",
    "otro",
}


def cargar_tipos(ruta: Path | None = None) -> dict[str, str]:
    ruta = ruta or config.ruta(config.REFERENCIA, "dominios.csv")
    with ruta.open(encoding="utf-8", newline="") as f:
        return {r["dominio"].strip().lower(): r["tipo"].strip() for r in csv.DictReader(f)}


def dominio_de(url: str, titulo: str = "", dominio: str = "") -> str:
    """Dominio de la cita. Las redirecciones de Gemini usan el dominio que informa el SDK."""
    anfitrion = (urlparse(url).hostname or "").lower().removeprefix("www.")
    if anfitrion in REDIRECCIONES or not anfitrion:
        candidato = (dominio or titulo).strip().lower().removeprefix("www.")
        return candidato if "." in candidato and " " not in candidato else ""
    return anfitrion


def tipo_de(dominio: str, tipos: dict[str, str]) -> str:
    """Tipo por coincidencia con el dominio o con alguno de sus sufijos."""
    if not dominio:
        return "otro"
    partes = dominio.split(".")
    for i in range(len(partes) - 1):
        candidato = ".".join(partes[i:])
        if candidato in tipos:
            return tipos[candidato]
    return "otro"
