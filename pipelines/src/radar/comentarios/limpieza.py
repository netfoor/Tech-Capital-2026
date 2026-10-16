"""Limpieza previa al envío a un modelo: quita menciones, URLs, correos y teléfonos (FR-007-03)."""

from __future__ import annotations

import re

_PATRONES = [
    (re.compile(r"https?://\S+|www\.\S+", re.I), "[enlace]"),
    (re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[correo]"),
    (re.compile(r"(?<!\w)@[\w.]+"), "[usuario]"),
    (re.compile(r"(?<!\d)(?:\+?\d[\s().-]?){8,15}(?!\d)"), "[teléfono]"),
]
LARGO_MAXIMO = 600


def limpiar(texto: str) -> str:
    for patron, reemplazo in _PATRONES:
        texto = patron.sub(reemplazo, texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto[:LARGO_MAXIMO]
