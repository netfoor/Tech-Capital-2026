"""Rutas del repositorio y variables de entorno.

Las rutas se resuelven desde la raíz del repositorio (la carpeta que contiene `data/` y
`specs/`). Se puede forzar con la variable `RADAR_REPO`.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


@lru_cache(maxsize=1)
def raiz() -> Path:
    forzada = os.environ.get("RADAR_REPO")
    if forzada:
        return Path(forzada).resolve()
    actual = Path(__file__).resolve()
    for carpeta in actual.parents:
        if (carpeta / "data").is_dir() and (carpeta / "specs").is_dir():
            return carpeta
    raise RuntimeError(
        "No se encontró la raíz del repositorio. Define RADAR_REPO con la ruta del repositorio."
    )


def cargar_entorno() -> None:
    """Carga `.env` de la raíz si existe. Nunca falla si no hay archivo."""
    load_dotenv(raiz() / ".env", override=False)


def ruta(*partes: str) -> Path:
    return raiz().joinpath(*partes)


DATOS = "data"
FUENTES = "data/fuentes"
REFERENCIA = "data/referencia"
CURADO = "data/curado"
CRUDO = "data/crudo"
PRIVADO = "data/privado"
CONTRATOS = "contracts"
WEB_DATOS = "web/public/datos"
