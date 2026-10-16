"""Contrato del recomendador inclusivo (spec 015).

Estos tipos son la interfaz que consume el endpoint de la spec 014. Los nombres
son estables: si un tipo provisional choca con estos, mandan estos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PRESUPUESTOS = ("gratis", "bajo", "medio", "alto")


@dataclass(frozen=True)
class AtributoAcc:
    """Un atributo de accesibilidad de un POI con su procedencia.

    - ``valor``: "si", "no", "limitado" o un número como texto (pendiente en %).
    - ``estado``: "verificado", "sin_verificar" o "reportado" (barrera reportada).
    - ``origen``: prestador, equipo, comunidad u osm.
    - ``confianza``: de 0 a 1.
    """

    valor: str
    estado: str
    origen: str = ""
    confianza: float = 0.0


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
    horario_osm: str | None
    accesibilidad: dict[str, AtributoAcc] = field(default_factory=dict)
    es_destino_alternativo: bool = False
    popularidad: float = 0.5
    subcategoria: str | None = None
    descripcion: str = ""
    is_synthetic: bool = False


@dataclass(frozen=True)
class SolicitudRuta:
    horas_disponibles: float
    punto_partida: tuple[float, float] | None = None
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
    llegada_min: int
    estancia_min: int
    traslado_min: int
    motivo: str
    advertencias: list[str] = field(default_factory=list)


@dataclass
class RespuestaRuta:
    paradas: list[Parada]
    no_incluidos: list[tuple[str, str]]
    alternativos: list[str]
    explicacion: str
    datos_desconocidos: list[str]
    metricas: dict[str, Any]


@dataclass(frozen=True)
class SolicitudMultidia:
    poi_ids: list[str]
    dias: int
    horas_por_dia: float
    restricciones: Restricciones = field(default_factory=Restricciones)
    hora_inicio: str = "10:00"
    dia_semana_inicio: int | None = None
    incluir_alternativos: bool = True


@dataclass
class RespuestaMultidia:
    dias: list[list[Parada]]
    no_incluidos: list[tuple[str, str]]
    alternativos: list[str]
    metricas: dict[str, Any]
