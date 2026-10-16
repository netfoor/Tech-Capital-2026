"""Esquema core: catálogo territorial y procedencia. Nunca apunta a private."""

from datetime import date, datetime, time

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from app.models.base import Base

ATRIBUTOS_ACCESIBILIDAD = (
    "acceso_sin_escalones",
    "rampa",
    "banio_accesible",
    "elevador",
    "superficie",
    "asientos",
    "estacionamiento_reservado",
    "pendiente_pct",
    "numero_escalones",
)
ESTADOS_ATRIBUTO = ("verificado", "sin_verificar", "reportado", "en_moderacion")
RANGOS_COSTO = ("gratis", "bajo", "medio", "alto")
PROCEDENCIAS = ("medido", "derivado")


def en(columna: str, valores: tuple[str, ...]) -> str:
    """Expresión SQL `columna IN (...)` para una restricción CHECK."""
    lista = ", ".join(f"'{v}'" for v in valores)
    return f"{columna} IN ({lista})"


def sintetico() -> Mapped[bool]:
    return mapped_column(Boolean, nullable=False, default=False, server_default="false")


class Destination(Base):
    __tablename__ = "destination"
    __table_args__ = {"schema": "core"}

    destino_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str | None] = mapped_column(String(40))
    pueblo_magico: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    municipios_cvegeo: Mapped[list[str]] = mapped_column(ARRAY(String(10)), nullable=False)
    cabecera_cvegeo: Mapped[str | None] = mapped_column(String(12))
    zona: Mapped[str | None] = mapped_column(String(100))
    centro_ot: Mapped[str | None] = mapped_column(String(100))
    altitud_m: Mapped[float | None] = mapped_column(Float)
    geom = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    is_synthetic: Mapped[bool] = sintetico()

    lat: Mapped[float] = column_property(func.ST_Y(geom))
    lon: Mapped[float] = column_property(func.ST_X(geom))


class Corridor(Base):
    __tablename__ = "corridor"
    __table_args__ = (
        CheckConstraint("lat_min <= lat_max AND lon_min <= lon_max", name="bbox_valida"),
        {"schema": "core"},
    )

    corredor_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    lat_min: Mapped[float] = mapped_column(Float, nullable=False)
    lon_min: Mapped[float] = mapped_column(Float, nullable=False)
    lat_max: Mapped[float] = mapped_column(Float, nullable=False)
    lon_max: Mapped[float] = mapped_column(Float, nullable=False)
    geom = mapped_column(Geometry("POLYGON", srid=4326))
    is_synthetic: Mapped[bool] = sintetico()


class DataSource(Base):
    __tablename__ = "data_source"
    __table_args__ = {"schema": "core"}

    fuente_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(300), nullable=False)
    institucion: Mapped[str | None] = mapped_column(String(300))
    tipo: Mapped[str | None] = mapped_column(String(60))
    url: Mapped[str | None] = mapped_column(Text)
    licencia: Mapped[str | None] = mapped_column(String(200))
    fecha_consulta: Mapped[date | None] = mapped_column(Date)
    sha256: Mapped[str | None] = mapped_column(String(64))


class PointOfInterest(Base):
    __tablename__ = "point_of_interest"
    __table_args__ = (
        CheckConstraint(
            f"costo_rango IS NULL OR {en('costo_rango', RANGOS_COSTO)}", name="costo_rango"
        ),
        CheckConstraint(
            "match_score IS NULL OR (match_score >= 0 AND match_score <= 1)", name="match_score"
        ),
        {"schema": "core"},
    )

    poi_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(300), nullable=False)
    categoria: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    subcategoria: Mapped[str | None] = mapped_column(String(120))
    destino_id: Mapped[str] = mapped_column(
        ForeignKey("core.destination.destino_id"), nullable=False, index=True
    )
    corredor_id: Mapped[str | None] = mapped_column(
        ForeignKey("core.corridor.corredor_id"), index=True
    )
    municipio_cvegeo: Mapped[str | None] = mapped_column(String(10))
    geom = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    direccion: Mapped[str | None] = mapped_column(Text)
    horario_osm: Mapped[str | None] = mapped_column(Text)
    costo_rango: Mapped[str | None] = mapped_column(String(10))
    descripcion: Mapped[str | None] = mapped_column(Text)
    fuentes: Mapped[list[str]] = mapped_column(
        ARRAY(String(80)), nullable=False, default=list, server_default="{}"
    )
    osm_id: Mapped[str | None] = mapped_column(String(40))
    denue_id: Mapped[str | None] = mapped_column(String(40))
    sic_id: Mapped[str | None] = mapped_column(String(40))
    match_score: Mapped[float | None] = mapped_column(Float)
    is_synthetic: Mapped[bool] = sintetico()

    lat: Mapped[float] = column_property(func.ST_Y(geom))
    lon: Mapped[float] = column_property(func.ST_X(geom))

    atributos: Mapped[list["POIAccessibilityAttribute"]] = relationship(
        back_populates="poi", cascade="all, delete-orphan", lazy="selectin"
    )


class POIAccessibilityAttribute(Base):
    __tablename__ = "poi_accessibility_attribute"
    __table_args__ = (
        UniqueConstraint("poi_id", "atributo", name="uq_poi_accessibility_attribute_poi_atributo"),
        CheckConstraint(en("atributo", ATRIBUTOS_ACCESIBILIDAD), name="atributo"),
        CheckConstraint(en("estado", ESTADOS_ATRIBUTO), name="estado"),
        CheckConstraint("confianza >= 0 AND confianza <= 1", name="confianza"),
        {"schema": "core"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    poi_id: Mapped[str] = mapped_column(
        ForeignKey("core.point_of_interest.poi_id", ondelete="CASCADE"), nullable=False
    )
    atributo: Mapped[str] = mapped_column(String(40), nullable=False)
    valor: Mapped[str | None] = mapped_column(String(80))
    origen: Mapped[str] = mapped_column(String(40), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    alcance: Mapped[str] = mapped_column(String(80), nullable=False, server_default="poi")
    confianza: Mapped[float] = mapped_column(Float, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    evidencia: Mapped[str | None] = mapped_column(Text)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    is_synthetic: Mapped[bool] = sintetico()

    poi: Mapped[PointOfInterest] = relationship(back_populates="atributos")


class AccessibilityEvidence(Base):
    __tablename__ = "accessibility_evidence"
    __table_args__ = (
        CheckConstraint(en("atributo", ATRIBUTOS_ACCESIBILIDAD), name="atributo"),
        CheckConstraint("confianza >= 0 AND confianza <= 1", name="confianza"),
        {"schema": "core"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attribute_id: Mapped[int | None] = mapped_column(
        ForeignKey("core.poi_accessibility_attribute.id", ondelete="SET NULL")
    )
    poi_id: Mapped[str] = mapped_column(
        ForeignKey("core.point_of_interest.poi_id", ondelete="CASCADE"), nullable=False, index=True
    )
    atributo: Mapped[str] = mapped_column(String(40), nullable=False)
    valor: Mapped[str | None] = mapped_column(String(80))
    origen: Mapped[str] = mapped_column(String(40), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    confianza: Mapped[float] = mapped_column(Float, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    referencia: Mapped[str | None] = mapped_column(String(120))
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    is_synthetic: Mapped[bool] = sintetico()


class OpeningHours(Base):
    __tablename__ = "opening_hours"
    __table_args__ = (
        CheckConstraint(
            "dia_semana IS NULL OR (dia_semana >= 0 AND dia_semana <= 6)", name="dia_semana"
        ),
        {"schema": "core"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    poi_id: Mapped[str] = mapped_column(
        ForeignKey("core.point_of_interest.poi_id", ondelete="CASCADE"), nullable=False, index=True
    )
    dia_semana: Mapped[int | None] = mapped_column(Integer)
    abre: Mapped[time | None] = mapped_column(Time)
    cierra: Mapped[time | None] = mapped_column(Time)
    texto_osm: Mapped[str | None] = mapped_column(Text)
    origen: Mapped[str] = mapped_column(String(40), nullable=False)
    fecha: Mapped[date | None] = mapped_column(Date)
    is_synthetic: Mapped[bool] = sintetico()


class Provider(Base):
    __tablename__ = "provider"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(300), nullable=False)
    tipo: Mapped[str | None] = mapped_column(String(80))
    poi_id: Mapped[str | None] = mapped_column(
        ForeignKey("core.point_of_interest.poi_id", ondelete="SET NULL")
    )
    denue_id: Mapped[str | None] = mapped_column(String(40))
    is_synthetic: Mapped[bool] = sintetico()


class DataLineage(Base):
    __tablename__ = "data_lineage"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entidad: Mapped[str] = mapped_column(String(80), nullable=False)
    entidad_id: Mapped[str] = mapped_column(String(120), nullable=False)
    fuente_id: Mapped[str] = mapped_column(ForeignKey("core.data_source.fuente_id"), nullable=False)
    campo: Mapped[str | None] = mapped_column(String(80))
    metodo: Mapped[str | None] = mapped_column(Text)
    fecha: Mapped[date | None] = mapped_column(Date)


class MetricDefinition(Base):
    __tablename__ = "metric_definition"
    __table_args__ = (
        CheckConstraint(
            f"procedencia IS NULL OR {en('procedencia', PROCEDENCIAS)}", name="procedencia"
        ),
        {"schema": "core"},
    )

    metric_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    formula: Mapped[str | None] = mapped_column(Text)
    version_formula: Mapped[str] = mapped_column(String(40), nullable=False)
    unidad: Mapped[str | None] = mapped_column(String(80))
    denominador: Mapped[str | None] = mapped_column(Text)
    procedencia: Mapped[str | None] = mapped_column(String(20))
    fuente_id: Mapped[str | None] = mapped_column(ForeignKey("core.data_source.fuente_id"))
    k_minimo: Mapped[int | None] = mapped_column(Integer)
