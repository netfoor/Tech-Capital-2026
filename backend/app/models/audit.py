"""Esquema audit: bitácora de acciones y casos de moderación, sin datos personales."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.core import ATRIBUTOS_ACCESIBILIDAD, en, sintetico
from app.models.private import TIPOS_BARRERA

ESTADOS_CASO = ("abierto", "aceptado", "rechazado")


class AuditEvent(Base):
    __tablename__ = "audit_event"
    __table_args__ = {"schema": "audit"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    # Seudónimo sin llave foránea: el evento sobrevive al borrado de la cuenta.
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    accion: Mapped[str] = mapped_column(String(80), nullable=False)
    entidad: Mapped[str] = mapped_column(String(80), nullable=False)
    entidad_id: Mapped[str] = mapped_column(String(120), nullable=False)
    detalle: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class ModerationCase(Base):
    __tablename__ = "moderation_case"
    __table_args__ = (
        CheckConstraint(en("estado", ESTADOS_CASO), name="estado"),
        CheckConstraint(en("tipo", TIPOS_BARRERA), name="tipo"),
        CheckConstraint(
            f"atributo IS NULL OR {en('atributo', ATRIBUTOS_ACCESIBILIDAD)}", name="atributo"
        ),
        CheckConstraint(
            "estado = 'abierto' OR (decidido_en IS NOT NULL AND decision IS NOT NULL)",
            name="decision_completa",
        ),
        {"schema": "audit"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    community_report_id: Mapped[int | None] = mapped_column(
        ForeignKey("private.community_report.id", ondelete="SET NULL"), index=True
    )
    poi_id: Mapped[str] = mapped_column(
        ForeignKey("core.point_of_interest.poi_id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    atributo: Mapped[str | None] = mapped_column(String(40))
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="abierto")
    decision: Mapped[str | None] = mapped_column(String(20))
    nota: Mapped[str | None] = mapped_column(Text)
    decidido_por: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    decidido_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    is_synthetic: Mapped[bool] = sintetico()
