"""Contrato del recomendador inclusivo (specs 014 y 015).

Es la interfaz estable entre la API (spec 014) y el motor (spec 015). El motor no
conoce la base de datos ni la API: recibe candidatos ya leídos del catálogo y
devuelve identificadores de POI.

Estos tipos son un superconjunto compatible de los provisionales de la spec 014:
los campos que consume el endpoint existen con el mismo nombre, y los que agrega
la spec 015 tienen valor por defecto.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, NamedTuple

PRESUPUESTOS = ("gratis", "bajo", "medio", "alto")
ATRIBUTOS_CLAVE = ("acceso_sin_escalones", "banio_accesible")


@dataclass(frozen=True)
class AtributoAcc:
    """Un atributo de accesibilidad de un POI con su procedencia.

    - ``valor``: "si", "no", "limitado", un número como texto (pendiente en %) o
      ``None`` si no hay dato.
    - ``estado``: "verificado", "sin_verificar", "reportado" (barrera reportada) o
      "en_moderacion".
    - ``origen``: prestador, equipo, comunidad u osm.
    - ``confianza``: de 0 a 1 (``None`` se trata como 0).
    """

    valor: str | None
    estado: str
    origen: str | None = ""
    confianza: float | None = 0.0
    fecha: date | None = None


# Nombre que usa la spec 014.
AtributoAcceso = AtributoAcc


@dataclass(frozen=True)
class Restricciones:
    """Necesidades funcionales del visitante. Todas son indispensables."""

    sin_escalones: bool = False
    banio_accesible: bool = False
    descansos_cada_min: int | None = None
    pendiente_max_pct: float | None = None

    def alguna(self) -> bool:
        return bool(
            self.sin_escalones
            or self.banio_accesible
            or self.descansos_cada_min
            or self.pendiente_max_pct is not None
        )


@dataclass(frozen=True)
class POICandidato:
    poi_id: str
    nombre: str
    categoria: str
    destino_id: str | None
    corredor_id: str | None
    lat: float
    lon: float
    costo_rango: str | None
    accesibilidad: dict[str, AtributoAcc] = field(default_factory=dict)
    horario_osm: str | None = None
    is_synthetic: bool = False
    # None = el catálogo no lo trae; el motor aplica la regla de polos saturados.
    es_destino_alternativo: bool | None = None
    popularidad: float | None = None
    subcategoria: str | None = None
    descripcion: str = ""


@dataclass(frozen=True)
class SolicitudRuta:
    horas_disponibles: float
    punto_partida: tuple[float, float] | None = None  # (lat, lon); nunca se guarda
    intereses: list[str] = field(default_factory=list)
    presupuesto: str | None = None
    restricciones: Restricciones = field(default_factory=Restricciones)
    incluir_alternativos: bool = True
    hora_inicio: str = "10:00"
    dia_semana: int | None = None  # 0 = lunes … 6 = domingo


@dataclass
class Parada:
    orden: int
    poi_id: str
    nombre: str
    llegada_min: int  # minutos desde el inicio del recorrido
    estancia_min: int
    traslado_min: int  # incluye los descansos programados en el trayecto
    motivo: str
    advertencias: list[str] = field(default_factory=list)


class NoIncluido(NamedTuple):
    """Lugar que no entra y por qué. Es una tupla ``(poi_id, motivo)`` con nombres."""

    poi_id: str
    motivo: str


@dataclass
class RespuestaRuta:
    paradas: list[Parada]
    no_incluidos: list[NoIncluido]
    alternativos: list[str]
    explicacion: str
    datos_desconocidos: list[str]
    metricas: dict[str, Any] = field(default_factory=dict)
    motor: str = "015-v1"


@dataclass(frozen=True)
class SolicitudMultidia:
    dias: int
    horas_por_dia: float
    restricciones: Restricciones = field(default_factory=Restricciones)
    poi_ids: list[str] = field(default_factory=list)
    hora_inicio: str = "10:00"
    dia_semana_inicio: int | None = None
    incluir_alternativos: bool = True


@dataclass
class DiaPlan:
    dia: int  # 1, 2, …
    paradas: list[Parada]


@dataclass
class RespuestaMultidia:
    dias: list[DiaPlan]
    no_incluidos: list[NoIncluido]
    alternativos: list[str]
    explicacion: str = ""
    metricas: dict[str, Any] = field(default_factory=dict)
    motor: str = "015-v1"
