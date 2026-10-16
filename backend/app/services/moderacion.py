"""Decisión de moderación: aceptar un reporte actualiza la ficha (§06.8)."""

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    AccessibilityEvidence,
    CommunityReport,
    ModerationCase,
    POIAccessibilityAttribute,
)
from app.services.auditoria import registrar

# tipo de barrera → (atributo, valor que deja el reporte aceptado)
ATRIBUTO_POR_TIPO: dict[str, tuple[str, str]] = {
    "escalones": ("acceso_sin_escalones", "no"),
    "rampa_bloqueada": ("rampa", "no"),
    "sin_banio_accesible": ("banio_accesible", "no"),
    "superficie": ("superficie", "irregular"),
}
# Un reporte de la comunidad no certifica (§06.2): confianza moderada y estado «reportado».
CONFIANZA_COMUNIDAD = 0.6


class YaDecidido(Exception):
    pass


def decidir(
    s: Session, caso: ModerationCase, decision: str, nota: str | None, moderador_id: uuid.UUID
) -> POIAccessibilityAttribute | None:
    if caso.estado != "abierto":
        raise YaDecidido
    ahora = datetime.now(UTC)
    caso.estado = "aceptado" if decision == "aceptar" else "rechazado"
    caso.decision = decision
    caso.nota = nota
    caso.decidido_por = moderador_id
    caso.decidido_en = ahora
    if caso.community_report_id is not None:
        reporte = s.get(CommunityReport, caso.community_report_id)
        if reporte is not None:
            reporte.estado = caso.estado

    atributo = None
    if decision == "aceptar" and caso.tipo in ATRIBUTO_POR_TIPO:
        nombre, valor = ATRIBUTO_POR_TIPO[caso.tipo]
        atributo = s.scalar(
            select(POIAccessibilityAttribute).where(
                POIAccessibilityAttribute.poi_id == caso.poi_id,
                POIAccessibilityAttribute.atributo == nombre,
            )
        )
        if atributo is None:
            atributo = POIAccessibilityAttribute(poi_id=caso.poi_id, atributo=nombre)
            s.add(atributo)
        atributo.valor = valor
        atributo.estado = "reportado"
        atributo.origen = "comunidad"
        atributo.fecha = date.today()
        atributo.alcance = "poi"
        atributo.confianza = CONFIANZA_COMUNIDAD
        atributo.evidencia = f"Reporte de barrera aceptado (moderation_case:{caso.id})"
        atributo.actualizado_en = ahora
        atributo.is_synthetic = caso.is_synthetic
        s.flush()
        s.add(
            AccessibilityEvidence(
                attribute_id=atributo.id,
                poi_id=caso.poi_id,
                atributo=nombre,
                valor=valor,
                origen="comunidad",
                fecha=date.today(),
                confianza=CONFIANZA_COMUNIDAD,
                descripcion=f"Reporte de barrera «{caso.tipo}» aceptado en moderación",
                referencia=f"moderation_case:{caso.id}",
                is_synthetic=caso.is_synthetic,
            )
        )
    registrar(
        s,
        moderador_id,
        f"moderacion_{caso.estado}",
        "moderation_case",
        caso.id,
        {
            "poi_id": caso.poi_id,
            "tipo": caso.tipo,
            "atributo": atributo.atributo if atributo else None,
            "valor": atributo.valor if atributo else None,
        },
    )
    s.commit()
    return atributo
