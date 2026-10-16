"""Punto de entrada de la API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ajustes
from app.db import base_disponible

app = FastAPI(
    title="Puebla Viva 360",
    version="0.1.0",
    description="Catálogo turístico inclusivo, recomendador y tablero institucional.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ajustes().origenes_permitidos,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["sistema"])
def salud() -> dict[str, str]:
    return {
        "estado": "ok",
        "base_de_datos": "disponible" if base_disponible() else "no disponible",
    }
