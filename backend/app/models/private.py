"""Esquema private: datos personales, contenidos y trayectorias.

Nada de aquí sale en una respuesta pública. Todo lo que depende de una persona se borra en
cascada desde `user_account` (DELETE /me).
"""

import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.core import en, sintetico

ROLES = ("visitante", "viewer", "analista", "admin")
FINALIDADES = ("ubicacion_sesion", "resenas", "fotos", "analitica_agregada")
DIMENSIONES = (
    "accesibilidad",
    "limpieza",
    "servicio",
    "precio_percibido",
    "senalizacion",
    "comodidad",
    "inclusion",
    "global",
)
TIPOS_BARRERA = (
    "escalones",
    "rampa_bloqueada",
    "sin_banio_accesible",
    "superficie",
    "senalizacion",
    "otro",
)
ESTADOS_REPORTE = ("en_moderacion", "aceptado", "rechazado")
ESTADOS_SESION = ("activa", "pausada", "detenida")
ESTADOS_CANDIDATO = ("visita_probable", "paso_cercano", "desconocido")
FUENTES_VISITA = ("gps_confirmado", "check_in", "manual")
MODOS_ITINERARIO = ("recomendado", "desde_guardados")

S = {"schema": "private"}


def ahora() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


def del_usuario(nullable: bool = False) -> Mapped[uuid.UUID]:
    return mapped_column(
        ForeignKey("private.user_account.id", ondelete="CASCADE"), nullable=nullable, index=True
    )


def al_poi(nullable: bool = False) -> Mapped[str]:
    return mapped_column(
        ForeignKey("core.point_of_interest.poi_id", ondelete="CASCADE"),
        nullable=nullable,
        index=True,
    )


class User(Base):
    __tablename__ = "user_account"
    __table_args__ = (
        CheckConstraint(en("rol", ROLES), name="rol"),
        CheckConstraint("correo = lower(correo)", name="correo_minusculas"),
        S,
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    correo: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    hash_contrasena: Mapped[str] = mapped_column(String(200), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False, default="visitante")
    nombre_visible: Mapped[str | None] = mapped_column(String(120))
    creado_en: Mapped[datetime] = ahora()
    is_synthetic: Mapped[bool] = sintetico()


class ConsentGrant(Base):
    __tablename__ = "consent_grant"
    __table_args__ = (CheckConstraint(en("finalidad", FINALIDADES), name="finalidad"), S)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = del_usuario()
    finalidad: Mapped[str] = mapped_column(String(40), nullable=False)
    version: Mapped[str] = mapped_column(String(40), nullable=False)
    otorgado: Mapped[bool] = mapped_column(Boolean, nullable=False)
    fecha: Mapped[datetime] = ahora()
    revocado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class PrivacyPreference(Base):
    __tablename__ = "privacy_preference"
    __table_args__ = (
        CheckConstraint(en("precision_publicacion", ("lugar", "zona")), name="precision"),
        S,
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("private.user_account.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    perfil_publico: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    precision_publicacion: Mapped[str] = mapped_column(String(10), nullable=False, default="zona")
    retencion_dias: Mapped[int] = mapped_column(Integer, nullable=False, default=30)


class UserAccessibilityPreference(Base):
    __tablename__ = "user_accessibility_preference"
    __table_args__ = S

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("private.user_account.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    sin_escalones: Mapped[bool | None] = mapped_column(Boolean)
    banio_accesible: Mapped[bool | None] = mapped_column(Boolean)
    descansos_cada_min: Mapped[int | None] = mapped_column(Integer)
    pendiente_max_pct: Mapped[float | None] = mapped_column(Float)


class TripSession(Base):
    __tablename__ = "trip_session"
    __table_args__ = (CheckConstraint(en("estado", ESTADOS_SESION), name="estado"), S)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = del_usuario()
    consent_id: Mapped[int | None] = mapped_column(
        ForeignKey("private.consent_grant.id", ondelete="SET NULL")
    )
    version_consentimiento: Mapped[str] = mapped_column(String(40), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="activa")
    inicio: Mapped[datetime] = ahora()
    fin: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_synthetic: Mapped[bool] = sintetico()


class LocationSample(Base):
    __tablename__ = "location_sample"
    __table_args__ = (CheckConstraint("precision_m >= 0", name="precision"), S)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("private.trip_session.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    geom = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    precision_m: Mapped[float] = mapped_column(Float, nullable=False)
    version_consentimiento: Mapped[str] = mapped_column(String(40), nullable=False)
    is_synthetic: Mapped[bool] = sintetico()


class VisitCandidate(Base):
    __tablename__ = "visit_candidate"
    __table_args__ = (
        CheckConstraint(en("estado", ESTADOS_CANDIDATO), name="estado"),
        CheckConstraint("confianza >= 0 AND confianza <= 1", name="confianza"),
        CheckConstraint("precision_m >= 0", name="precision"),
        S,
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("private.trip_session.id", ondelete="CASCADE"), nullable=False, index=True
    )
    poi_id: Mapped[str | None] = al_poi(nullable=True)
    inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fin: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duracion_min: Mapped[float] = mapped_column(Float, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    fuente_evidencia: Mapped[str] = mapped_column(String(40), nullable=False)
    precision_m: Mapped[float] = mapped_column(Float, nullable=False)
    confianza: Mapped[float] = mapped_column(Float, nullable=False)
    confirmada: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_synthetic: Mapped[bool] = sintetico()


class ConfirmedVisit(Base):
    __tablename__ = "confirmed_visit"
    __table_args__ = (
        CheckConstraint(en("fuente_evidencia", FUENTES_VISITA), name="fuente_evidencia"),
        CheckConstraint("confianza >= 0 AND confianza <= 1", name="confianza"),
        CheckConstraint(
            "precision_m IS NOT NULL OR fuente_evidencia IN ('check_in', 'manual')",
            name="precision_con_gps",
        ),
        S,
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = del_usuario()
    poi_id: Mapped[str] = al_poi()
    candidate_id: Mapped[int | None] = mapped_column(
        ForeignKey("private.visit_candidate.id", ondelete="SET NULL")
    )
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fuente_evidencia: Mapped[str] = mapped_column(String(40), nullable=False)
    precision_m: Mapped[float | None] = mapped_column(Float)
    confianza: Mapped[float] = mapped_column(Float, nullable=False)
    confirmada: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_synthetic: Mapped[bool] = sintetico()


class CheckIn(Base):
    __tablename__ = "check_in"
    __table_args__ = S

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = del_usuario()
    poi_id: Mapped[str] = al_poi()
    fecha: Mapped[datetime] = ahora()
    nota: Mapped[str | None] = mapped_column(Text)
    is_synthetic: Mapped[bool] = sintetico()


class MediaAsset(Base):
    __tablename__ = "media_asset"
    __table_args__ = (CheckConstraint("sin_exif", name="sin_exif"), S)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = del_usuario()
    ruta: Mapped[str] = mapped_column(Text, nullable=False)
    tipo_mime: Mapped[str] = mapped_column(String(40), nullable=False)
    bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    texto_alternativo: Mapped[str | None] = mapped_column(Text)
    sin_exif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = ahora()
    is_synthetic: Mapped[bool] = sintetico()


class Review(Base):
    __tablename__ = "review"
    __table_args__ = S

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = del_usuario()
    poi_id: Mapped[str] = al_poi()
    texto: Mapped[str | None] = mapped_column(Text)
    publica: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    creado_en: Mapped[datetime] = ahora()
    is_synthetic: Mapped[bool] = sintetico()

    dimensiones: Mapped[list["ReviewDimension"]] = relationship(
        cascade="all, delete-orphan", lazy="selectin"
    )


class ReviewDimension(Base):
    __tablename__ = "review_dimension"
    __table_args__ = (
        CheckConstraint(en("dimension", DIMENSIONES), name="dimension"),
        CheckConstraint("puntaje >= 1 AND puntaje <= 5", name="puntaje"),
        UniqueConstraint("review_id", "dimension", name="uq_review_dimension_review_dimension"),
        S,
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(
        ForeignKey("private.review.id", ondelete="CASCADE"), nullable=False
    )
    dimension: Mapped[str] = mapped_column(String(30), nullable=False)
    puntaje: Mapped[int] = mapped_column(Integer, nullable=False)


class CommunityReport(Base):
    __tablename__ = "community_report"
    __table_args__ = (
        CheckConstraint(en("tipo", TIPOS_BARRERA), name="tipo"),
        CheckConstraint(en("estado", ESTADOS_REPORTE), name="estado"),
        S,
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = del_usuario()
    poi_id: Mapped[str] = al_poi()
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    media_asset_id: Mapped[int | None] = mapped_column(
        ForeignKey("private.media_asset.id", ondelete="SET NULL")
    )
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="en_moderacion")
    creado_en: Mapped[datetime] = ahora()
    is_synthetic: Mapped[bool] = sintetico()


class SavedPlace(Base):
    __tablename__ = "saved_place"
    __table_args__ = (
        CheckConstraint("poi_id IS NOT NULL OR nombre_propio IS NOT NULL", name="poi_o_propio"),
        UniqueConstraint("user_id", "poi_id", name="uq_saved_place_user_poi"),
        S,
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = del_usuario()
    poi_id: Mapped[str | None] = al_poi(nullable=True)
    nombre_propio: Mapped[str | None] = mapped_column(String(300))
    nota: Mapped[str | None] = mapped_column(Text)
    url_origen: Mapped[str | None] = mapped_column(Text)
    plataforma_origen: Mapped[str | None] = mapped_column(String(40))
    creado_en: Mapped[datetime] = ahora()
    is_synthetic: Mapped[bool] = sintetico()


class PlaceList(Base):
    __tablename__ = "place_list"
    __table_args__ = S

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = del_usuario()
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    etiquetas: Mapped[list[str]] = mapped_column(
        ARRAY(String(60)), nullable=False, default=list, server_default="{}"
    )
    creado_en: Mapped[datetime] = ahora()
    is_synthetic: Mapped[bool] = sintetico()

    items: Mapped[list["PlaceListItem"]] = relationship(
        cascade="all, delete-orphan", lazy="selectin", order_by="PlaceListItem.orden"
    )


class PlaceListItem(Base):
    __tablename__ = "place_list_item"
    __table_args__ = (
        UniqueConstraint("list_id", "saved_place_id", name="uq_place_list_item_list_saved"),
        S,
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    list_id: Mapped[int] = mapped_column(
        ForeignKey("private.place_list.id", ondelete="CASCADE"), nullable=False, index=True
    )
    saved_place_id: Mapped[int] = mapped_column(
        ForeignKey("private.saved_place.id", ondelete="CASCADE"), nullable=False
    )
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    guardado: Mapped[SavedPlace] = relationship(lazy="joined")


class Itinerary(Base):
    __tablename__ = "itinerary"
    __table_args__ = (CheckConstraint(en("modo", MODOS_ITINERARIO), name="modo"), S)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID | None] = del_usuario(nullable=True)
    modo: Mapped[str] = mapped_column(String(20), nullable=False)
    solicitud: Mapped[dict] = mapped_column(JSONB, nullable=False)
    explicacion: Mapped[str | None] = mapped_column(Text)
    motor: Mapped[str] = mapped_column(String(60), nullable=False)
    creado_en: Mapped[datetime] = ahora()
    is_synthetic: Mapped[bool] = sintetico()

    dias: Mapped[list["ItineraryDay"]] = relationship(
        cascade="all, delete-orphan", lazy="selectin", order_by="ItineraryDay.dia"
    )


class ItineraryDay(Base):
    __tablename__ = "itinerary_day"
    __table_args__ = (
        UniqueConstraint("itinerary_id", "dia", name="uq_itinerary_day_itinerary_dia"),
        CheckConstraint("dia >= 1", name="dia"),
        S,
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    itinerary_id: Mapped[int] = mapped_column(
        ForeignKey("private.itinerary.id", ondelete="CASCADE"), nullable=False
    )
    dia: Mapped[int] = mapped_column(Integer, nullable=False)

    paradas: Mapped[list["ItineraryStop"]] = relationship(
        cascade="all, delete-orphan", lazy="selectin", order_by="ItineraryStop.orden"
    )


class ItineraryStop(Base):
    __tablename__ = "itinerary_stop"
    __table_args__ = (
        CheckConstraint(
            "llegada_min >= 0 AND estancia_min >= 0 AND traslado_min >= 0", name="tiempos"
        ),
        S,
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day_id: Mapped[int] = mapped_column(
        ForeignKey("private.itinerary_day.id", ondelete="CASCADE"), nullable=False
    )
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    poi_id: Mapped[str] = al_poi()
    llegada_min: Mapped[float] = mapped_column(Float, nullable=False)
    estancia_min: Mapped[float] = mapped_column(Float, nullable=False)
    traslado_min: Mapped[float] = mapped_column(Float, nullable=False)
    motivo: Mapped[str | None] = mapped_column(Text)
    advertencias: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default="{}"
    )


class Recommendation(Base):
    __tablename__ = "recommendation"
    __table_args__ = S

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    itinerary_id: Mapped[int] = mapped_column(
        ForeignKey("private.itinerary.id", ondelete="CASCADE"), nullable=False, index=True
    )
    poi_id: Mapped[str] = al_poi()
    incluido: Mapped[bool] = mapped_column(Boolean, nullable=False)
    alternativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    motivo: Mapped[str | None] = mapped_column(Text)


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"
    __table_args__ = S

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recommendation_id: Mapped[int] = mapped_column(
        ForeignKey("private.recommendation.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID | None] = del_usuario(nullable=True)
    util: Mapped[bool | None] = mapped_column(Boolean)
    comentario: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = ahora()
