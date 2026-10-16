"""Bitácora de auditoría. El detalle nunca lleva coordenadas ni texto de la persona."""

import uuid

from sqlalchemy.orm import Session

from app.models import AuditEvent


def registrar(
    s: Session,
    actor_id: uuid.UUID | None,
    accion: str,
    entidad: str,
    entidad_id: str | int,
    detalle: dict | None = None,
) -> AuditEvent:
    evento = AuditEvent(
        actor_id=actor_id,
        accion=accion,
        entidad=entidad,
        entidad_id=str(entidad_id),
        detalle=detalle or {},
    )
    s.add(evento)
    return evento
