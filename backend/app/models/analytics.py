"""Esquema analytics: agregados protegidos con tamaño de muestra y supresión."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.core import PROCEDENCIAS, en, sintetico


class AggregateMetric(Base):
    __tablename__ = "aggregate_metric"
    __table_args__ = (
        UniqueConstraint(
            "metric_id",
            "centro_ot",
            "nivel",
            "periodo",
            name="uq_aggregate_metric_metric_centro_nivel_periodo",
            postgresql_nulls_not_distinct=True,
        ),
        CheckConstraint(f"procedencia IS NULL OR {en('procedencia', PROCEDENCIAS)}", name="proc"),
        CheckConstraint("n IS NULL OR n >= 0", name="n"),
        CheckConstraint("NOT suprimido OR valor IS NULL", name="suprimido_sin_valor"),
        {"schema": "analytics"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metric_id: Mapped[str] = mapped_column(
        ForeignKey("core.metric_definition.metric_id"), nullable=False, index=True
    )
    destino_id: Mapped[str | None] = mapped_column(
        ForeignKey("core.destination.destino_id"), index=True
    )
    corredor_id: Mapped[str | None] = mapped_column(ForeignKey("core.corridor.corredor_id"))
    centro_ot: Mapped[str | None] = mapped_column(String(100))
    nivel: Mapped[str | None] = mapped_column(String(20))
    periodo: Mapped[str] = mapped_column(String(10), nullable=False)
    valor: Mapped[float | None] = mapped_column(Float)
    n: Mapped[int | None] = mapped_column(Integer)
    suprimido: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    procedencia: Mapped[str | None] = mapped_column(String(20))
    version_formula: Mapped[str] = mapped_column(String(40), nullable=False)
    calculado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fuente_id: Mapped[str | None] = mapped_column(ForeignKey("core.data_source.fuente_id"))
    is_synthetic: Mapped[bool] = sintetico()
