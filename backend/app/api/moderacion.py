"""Moderación de reportes de barrera. Solo roles analista y admin."""

from typing import Literal

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import Sesion
from app.models import CommunityReport, ModerationCase
from app.schemas.cuenta import (
    AtributoActualizado,
    CasoModeracion,
    CasosModeracion,
    RespuestaDecision,
    SolicitudDecision,
)
from app.services import moderacion
from app.services.seguridad import Moderador

router = APIRouter(prefix="/moderation", tags=["moderación"])


@router.get("", response_model=CasosModeracion)
def casos(
    s: Sesion,
    _moderador: Moderador,
    estado: Literal["abierto", "aceptado", "rechazado"] = "abierto",
) -> CasosModeracion:
    filas = s.execute(
        select(ModerationCase, CommunityReport.descripcion)
        .outerjoin(CommunityReport, CommunityReport.id == ModerationCase.community_report_id)
        .where(ModerationCase.estado == estado)
        .order_by(ModerationCase.creado_en, ModerationCase.id)
    ).all()
    return CasosModeracion(
        items=[
            CasoModeracion(
                id=c.id,
                poi_id=c.poi_id,
                tipo=c.tipo,
                atributo=c.atributo,
                estado=c.estado,
                descripcion=descripcion,
                creado_en=c.creado_en,
            )
            for c, descripcion in filas
        ]
    )


@router.post("/{caso_id}/decision", response_model=RespuestaDecision)
def decidir(
    caso_id: int, cuerpo: SolicitudDecision, s: Sesion, moderador: Moderador
) -> RespuestaDecision:
    caso = s.get(ModerationCase, caso_id)
    if caso is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Caso no encontrado")
    try:
        atributo = moderacion.decidir(s, caso, cuerpo.decision, cuerpo.nota, moderador.id)
    except moderacion.YaDecidido as error:
        raise HTTPException(status.HTTP_409_CONFLICT, "El caso ya tiene una decisión") from error
    return RespuestaDecision(
        id=caso.id,
        estado=caso.estado,
        atributo_actualizado=(
            AtributoActualizado(
                atributo=atributo.atributo, valor=atributo.valor, estado=atributo.estado
            )
            if atributo
            else None
        ),
    )
