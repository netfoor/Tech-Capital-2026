"""Normalización de texto para comparar nombres de lugares sin depender de acentos o mayúsculas."""

from __future__ import annotations

import re
import unicodedata


def sin_acentos(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in descompuesto if not unicodedata.combining(c))


def normalizar(texto: str) -> str:
    """Minúsculas, sin acentos, sin puntuación y con espacios simples."""
    base = sin_acentos(texto).lower()
    base = re.sub(r"[^a-z0-9ñ]+", " ", base)
    return re.sub(r"\s+", " ", base).strip()
