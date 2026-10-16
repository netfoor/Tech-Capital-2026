"""Esquemas de cuenta, guardados, contenidos, moderación y privacidad."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.catalogo import POIResumen

# --- Cuenta


class SolicitudRegistro(BaseModel):
    correo: EmailStr
    contrasena: str = Field(min_length=8, max_length=200)
    nombre_visible: str | None = Field(default=None, max_length=120)


class SolicitudLogin(BaseModel):
    correo: EmailStr
    contrasena: str = Field(max_length=200)


class UsuarioPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    correo: str
    rol: str
    nombre_visible: str | None


class RespuestaToken(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    usuario: UsuarioPublico


# --- Guardados y listas


class SolicitudGuardar(BaseModel):
    poi_id: str | None = None
    nombre_propio: str | None = Field(default=None, max_length=300)
    nota: str | None = Field(default=None, max_length=2000)
    url_origen: str | None = Field(default=None, max_length=2000)
    plataforma_origen: str | None = Field(default=None, max_length=40)


class LugarGuardado(BaseModel):
    id: int
    poi_id: str | None
    nombre_propio: str | None
    nota: str | None
    url_origen: str | None
    plataforma_origen: str | None
    creado_en: datetime
    poi: POIResumen | None


class PaginaGuardados(BaseModel):
    items: list[LugarGuardado]
    total: int


class SolicitudLista(BaseModel):
    nombre: str = Field(min_length=1, max_length=200)
    etiquetas: list[str] = Field(default_factory=list, max_length=20)


class ElementoLista(BaseModel):
    id: int
    list_id: int
    saved_place_id: int
    poi_id: str | None


class ElementoListaResumen(BaseModel):
    id: int
    saved_place_id: int
    poi_id: str | None


class Lista(BaseModel):
    id: int
    nombre: str
    etiquetas: list[str]
    items: list[ElementoListaResumen]


class Listas(BaseModel):
    items: list[Lista]


class SolicitudElemento(BaseModel):
    saved_place_id: int | None = None
    poi_id: str | None = None


# --- Reseñas, barreras y moderación

Puntaje = int


class Dimensiones(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accesibilidad: int | None = Field(default=None, ge=1, le=5)
    limpieza: int | None = Field(default=None, ge=1, le=5)
    servicio: int | None = Field(default=None, ge=1, le=5)
    precio_percibido: int | None = Field(default=None, ge=1, le=5)
    senalizacion: int | None = Field(default=None, ge=1, le=5)
    comodidad: int | None = Field(default=None, ge=1, le=5)
    inclusion: int | None = Field(default=None, ge=1, le=5)
    global_: int = Field(alias="global", ge=1, le=5)


class SolicitudResena(BaseModel):
    poi_id: str
    dimensiones: Dimensiones
    texto: str | None = Field(default=None, max_length=4000)


class RespuestaResena(BaseModel):
    review_id: int
    poi_id: str
    dimensiones: dict[str, int]
    texto: str | None
    creado_en: datetime


TipoBarrera = Literal[
    "escalones", "rampa_bloqueada", "sin_banio_accesible", "superficie", "senalizacion", "otro"
]


class SolicitudBarrera(BaseModel):
    poi_id: str
    tipo: TipoBarrera
    descripcion: str | None = Field(default=None, max_length=2000)
    foto: str | None = Field(default=None, description="Imagen en base64 (JPEG, PNG o WebP)")


class RespuestaBarrera(BaseModel):
    report_id: int
    moderation_case_id: int
    estado: Literal["en_moderacion"] = "en_moderacion"


class CasoModeracion(BaseModel):
    id: int
    poi_id: str
    tipo: str
    atributo: str | None
    estado: str
    descripcion: str | None
    creado_en: datetime


class CasosModeracion(BaseModel):
    items: list[CasoModeracion]


class SolicitudDecision(BaseModel):
    decision: Literal["aceptar", "rechazar"]
    nota: str | None = Field(default=None, max_length=2000)


class AtributoActualizado(BaseModel):
    atributo: str
    valor: str | None
    estado: str


class RespuestaDecision(BaseModel):
    id: int
    estado: Literal["aceptado", "rechazado"]
    atributo_actualizado: AtributoActualizado | None


# --- Privacidad

Finalidad = Literal["ubicacion_sesion", "resenas", "fotos", "analitica_agregada"]


class SolicitudConsentimiento(BaseModel):
    finalidad: Finalidad
    otorgado: bool
    version: str = Field(min_length=1, max_length=40)


class Consentimiento(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    finalidad: str
    otorgado: bool
    version: str
    fecha: datetime
