"""Tipos del recomendador. Es la interfaz estable entre la API (spec 014) y el motor (spec 015).

El motor no conoce la base de datos ni la API: recibe candidatos ya leídos del catálogo y
devuelve identificadores de POI. La API los convierte a `POIResumen`.
"""

from dataclasses import dataclass, field
from datetime import date

ATRIBUTOS_CLAVE = ("acceso_sin_escalones", "banio_accesible")


@dataclass(frozen=True)
class AtributoAcceso:
    valor: str | None
    estado: str  # verificado | sin_verificar | reportado | en_moderacion
    origen: str | None = None
    confianza: float | None = None
    fecha: date | None = None


@dataclass(frozen=True)
class Restricciones:
    """Restricciones indispensables del visitante. Nunca se violan."""

    sin_escalones: bool = False
    banio_accesible: bool = False
    descansos_cada_min: int | None = None
    pendiente_max_pct: float | None = None


@dataclass(frozen=True)
class SolicitudRuta:
    horas_disponibles: float
    punto_partida: tuple[float, float] | None = None  # (lat, lon); nunca se guarda
    intereses: list[str] = field(default_factory=list)  # se compara con POICandidato.categoria
    presupuesto: str | None = None  # gratis | bajo | medio | alto
    restricciones: Restricciones = field(default_factory=Restricciones)
    incluir_alternativos: bool = False


@dataclass(frozen=True)
class POICandidato:
    poi_id: str
    nombre: str
    categoria: str
    destino_id: str
    corredor_id: str | None
    lat: float
    lon: float
    costo_rango: str | None
    # Los nueve atributos; los que no tienen dato llegan con estado «sin_verificar» y valor None.
    accesibilidad: dict[str, AtributoAcceso]
    horario_osm: str | None = None
    is_synthetic: bool = False


@dataclass(frozen=True)
class Parada:
    orden: int
    poi_id: str
    llegada_min: float  # minutos desde el inicio del día o del recorrido
    estancia_min: float
    traslado_min: float
    motivo: str
    advertencias: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NoIncluido:
    poi_id: str
    motivo: str


@dataclass(frozen=True)
class RespuestaRuta:
    paradas: list[Parada]
    no_incluidos: list[NoIncluido]
    alternativos: list[str]  # poi_id sugeridos, claramente marcados como sugerencia
    explicacion: str
    datos_desconocidos: list[str]
    motor: str = "desconocido"


@dataclass(frozen=True)
class SolicitudMultidia:
    dias: int
    horas_por_dia: float
    restricciones: Restricciones = field(default_factory=Restricciones)


@dataclass(frozen=True)
class DiaPlan:
    dia: int
    paradas: list[Parada]


@dataclass(frozen=True)
class RespuestaMultidia:
    dias: list[DiaPlan]
    no_incluidos: list[NoIncluido]
    alternativos: list[str]
    explicacion: str
    motor: str = "desconocido"
