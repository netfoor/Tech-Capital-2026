"""Esquemas públicos del catálogo (docs/api/contrato-p0.md)."""

from datetime import date
from typing import Literal

from pydantic import BaseModel

Cobertura = Literal["verificada", "parcial", "sin_verificar"]
RangoCosto = Literal["gratis", "bajo", "medio", "alto"]


class AtributoAcceso(BaseModel):
    valor: str | None = None
    estado: str = "sin_verificar"
    origen: str | None = None
    confianza: float | None = None
    fecha: date | None = None


class POIResumen(BaseModel):
    poi_id: str
    nombre: str
    categoria: str
    destino_id: str
    corredor_id: str | None
    lat: float
    lon: float
    costo_rango: RangoCosto | None
    accesibilidad: dict[str, AtributoAcceso]
    cobertura_accesibilidad: Cobertura
    is_synthetic: bool


class Fuente(BaseModel):
    id: str
    nombre: str
    url: str | None


class BarreraReportada(BaseModel):
    tipo: str
    estado: Literal["en_moderacion", "aceptado"]
    fecha: date


class POIDetalle(POIResumen):
    descripcion: str | None
    direccion: str | None
    horario_osm: str | None
    fuentes: list[Fuente]
    barreras_reportadas: list[BarreraReportada]


class PaginaPOI(BaseModel):
    items: list[POIResumen]
    total: int


class DestinoResumen(BaseModel):
    destino_id: str
    nombre: str
    pueblo_magico: bool
    lat: float
    lon: float
    zona: str | None


class ListaDestinos(BaseModel):
    items: list[DestinoResumen]
