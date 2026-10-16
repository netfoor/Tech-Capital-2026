"""Esquemas de itinerarios (docs/api/contrato-p0.md)."""

from pydantic import BaseModel, Field

from app.schemas.catalogo import POIResumen, RangoCosto


class Punto(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class Restricciones(BaseModel):
    sin_escalones: bool | None = None
    banio_accesible: bool | None = None
    descansos_cada_min: int | None = Field(default=None, gt=0, le=600)
    pendiente_max_pct: float | None = Field(default=None, ge=0, le=100)


class SolicitudRecomendar(BaseModel):
    horas_disponibles: float = Field(gt=0, le=24)
    punto_partida: Punto | None = None
    intereses: list[str] = Field(default_factory=list, max_length=20)
    presupuesto: RangoCosto | None = None
    restricciones: Restricciones | None = None
    incluir_alternativos: bool = False


class SolicitudDesdeGuardados(BaseModel):
    poi_ids: list[str] = Field(min_length=1, max_length=200)
    dias: int = Field(ge=1, le=14)
    horas_por_dia: float = Field(gt=0, le=24)
    restricciones: Restricciones | None = None


class Parada(BaseModel):
    orden: int
    poi: POIResumen
    llegada_min: float
    estancia_min: float
    traslado_min: float
    motivo: str
    advertencias: list[str]


class NoIncluido(BaseModel):
    poi_id: str
    motivo: str


class RespuestaRecomendar(BaseModel):
    itinerario_id: int
    paradas: list[Parada]
    no_incluidos: list[NoIncluido]
    alternativos: list[POIResumen]
    explicacion: str
    datos_desconocidos: list[str]


class Dia(BaseModel):
    dia: int
    paradas: list[Parada]


class RespuestaDesdeGuardados(BaseModel):
    itinerario_id: int
    dias: list[Dia]
    no_incluidos: list[NoIncluido]
    alternativos: list[POIResumen]
