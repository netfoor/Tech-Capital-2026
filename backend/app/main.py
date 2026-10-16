"""Punto de entrada de la API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth,
    b2b,
    catalogo,
    contenidos,
    guardados,
    itinerarios,
    moderacion,
    privacidad,
    sesiones,
    visitas,
)
from app.config import ajustes
from app.db import base_disponible
from app.privacy import registros

registros.configurar()

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
app.middleware("http")(registros.registrar_peticion)

for router in (
    catalogo.router,
    itinerarios.router,
    auth.router,
    guardados.router,
    contenidos.router,
    moderacion.router,
    privacidad.router,
    # Reservados: specs 017 (recorridos y visitas) y 019 (tablero).
    sesiones.router,
    visitas.router_visitas,
    visitas.router_checkins,
    b2b.router,
    b2b.router_metricas,
):
    app.include_router(router)


@app.get("/health", tags=["sistema"])
def salud() -> dict[str, str]:
    return {
        "estado": "ok",
        "base_de_datos": "disponible" if base_disponible() else "no disponible",
    }
