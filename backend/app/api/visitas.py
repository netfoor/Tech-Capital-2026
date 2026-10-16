"""Confirmación de visitas y check-ins manuales. Los implementa la spec 017."""

from fastapi import APIRouter

router_visitas = APIRouter(prefix="/visits", tags=["recorridos"])
router_checkins = APIRouter(prefix="/checkins", tags=["recorridos"])
