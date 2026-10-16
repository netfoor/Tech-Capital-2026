"""Etapa 1: elegibilidad dura.

Regla de oro (constitución, XIII): una restricción indispensable nunca se
viola y la falta de dato nunca se interpreta como «accesible».

Cada atributo se evalúa en tres estados:

- ``cumple``: ``valor`` compatible y estado ``verificado``, o ``sin_verificar``
  con confianza ≥ ``config.confianza_minima``.
- ``no_cumple``: ``valor`` incompatible (``no``, ``limitado``, pendiente mayor)
  o estado ``reportado`` (barrera reportada), sin importar la confianza.
- ``desconocido``: sin dato, valor no interpretable o confianza baja.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from . import horarios
from .config import (
    CATEGORIAS_BANIO,
    CATEGORIAS_SERVICIO,
    ORDEN_PRESUPUESTO,
    Config,
    estancia_tipica,
)
from .geo import minutos_caminando
from .tipos import AtributoAcc, POICandidato, Restricciones

CUMPLE = "cumple"
NO_CUMPLE = "no_cumple"
DESCONOCIDO = "desconocido"

ATR_SIN_ESCALONES = "acceso_sin_escalones"
ATR_BANIO = "banio_accesible"
ATR_PENDIENTE = "pendiente_pct"
ATR_ASIENTOS = "asientos_descanso"

_SI = {"si", "sí", "yes", "true", "designated", "1"}
_NO = {"no", "false", "0", "limitado", "limited"}

NOMBRE_ATRIBUTO = {
    ATR_SIN_ESCALONES: "acceso sin escalones",
    ATR_BANIO: "baño accesible",
    ATR_PENDIENTE: "pendiente del acceso",
}


def _booleano(valor: str) -> bool | None:
    v = (valor or "").strip().lower()
    if v in _SI:
        return True
    if v in _NO:
        return False
    return None


def _numero(valor: str) -> float | None:
    try:
        return float((valor or "").strip().rstrip("%"))
    except ValueError:
        return None


def evaluar_atributo(
    atributo: AtributoAcc | None,
    compatible: Callable[[str], bool | None],
    config: Config,
) -> tuple[str, str]:
    """Devuelve (estado, explicación breve)."""
    if atributo is None or atributo.valor is None or not str(atributo.valor).strip():
        if atributo is not None and atributo.estado == "reportado":
            return NO_CUMPLE, "barrera reportada por visitantes"
        return DESCONOCIDO, "sin dato"
    if atributo.estado == "reportado":
        return NO_CUMPLE, "barrera reportada por visitantes"
    ok = compatible(atributo.valor)
    if ok is False:
        return NO_CUMPLE, f"valor «{atributo.valor}»"
    if ok is None:
        return DESCONOCIDO, f"valor no interpretable «{atributo.valor}»"
    confianza = atributo.confianza or 0.0
    if atributo.estado == "verificado":
        return CUMPLE, f"verificado ({atributo.origen or 'origen sin dato'})"
    if atributo.estado == "sin_verificar" and confianza >= config.confianza_minima:
        return CUMPLE, f"confianza {confianza:.2f} ({atributo.origen})"
    if atributo.estado == "sin_verificar":
        return DESCONOCIDO, f"confianza baja ({confianza:.2f})"
    return DESCONOCIDO, f"estado «{atributo.estado}»"


def evaluar_sin_escalones(poi: POICandidato, config: Config) -> tuple[str, str]:
    return evaluar_atributo(poi.accesibilidad.get(ATR_SIN_ESCALONES), _booleano, config)


def evaluar_banio(poi: POICandidato, config: Config) -> tuple[str, str]:
    return evaluar_atributo(poi.accesibilidad.get(ATR_BANIO), _booleano, config)


def evaluar_pendiente(poi: POICandidato, maximo: float, config: Config) -> tuple[str, str]:
    def compatible(valor: str) -> bool | None:
        n = _numero(valor)
        return None if n is None else n <= maximo

    return evaluar_atributo(poi.accesibilidad.get(ATR_PENDIENTE), compatible, config)


def es_servicio(poi: POICandidato) -> bool:
    return (poi.categoria or "").lower() in CATEGORIAS_SERVICIO


def es_banio(poi: POICandidato) -> bool:
    return (poi.categoria or "").lower() in CATEGORIAS_BANIO


def cumple_restricciones_lugar(
    poi: POICandidato, restricciones: Restricciones, config: Config
) -> tuple[str, str]:
    """Combina las restricciones que dependen del lugar (escalones y pendiente)."""
    resultados: list[tuple[str, str, str]] = []
    if restricciones.sin_escalones:
        estado, detalle = evaluar_sin_escalones(poi, config)
        resultados.append((estado, ATR_SIN_ESCALONES, detalle))
    if restricciones.pendiente_max_pct is not None:
        estado, detalle = evaluar_pendiente(poi, restricciones.pendiente_max_pct, config)
        resultados.append((estado, ATR_PENDIENTE, detalle))
    for estado, atr, detalle in resultados:
        if estado == NO_CUMPLE:
            return NO_CUMPLE, f"No cumple «{NOMBRE_ATRIBUTO[atr]}»: {detalle}"
    for estado, atr, detalle in resultados:
        if estado == DESCONOCIDO:
            return DESCONOCIDO, f"{NOMBRE_ATRIBUTO[atr].capitalize()} sin verificar ({detalle})"
    return CUMPLE, ""


def ventanas_poi(poi: POICandidato, dia: int | None) -> list[tuple[int, int]] | None:
    """Ventanas verificables del día, o ``None`` si el horario no se interpreta."""
    parseado = horarios.parsear(poi.horario_osm)
    if parseado is None:
        return None
    return horarios.ventanas(parseado, dia)


def banio_confiable(poi: POICandidato, restricciones: Restricciones, config: Config) -> bool:
    """Un lugar cuenta como acceso a baño accesible si su baño es confiable y
    el propio lugar cumple las restricciones de acceso del visitante."""
    if evaluar_banio(poi, config)[0] != CUMPLE:
        return False
    return cumple_restricciones_lugar(poi, restricciones, config)[0] == CUMPLE


@dataclass
class Clasificacion:
    elegibles: list[POICandidato] = field(default_factory=list)
    sin_verificar: list[tuple[POICandidato, str]] = field(default_factory=list)
    excluidos: list[tuple[POICandidato, str]] = field(default_factory=list)
    advertencias: dict[str, list[str]] = field(default_factory=dict)
    banios: list[POICandidato] = field(default_factory=list)


def _cabe_en_horario(
    poi: POICandidato,
    dias: list[int | None],
    inicio_min: int,
    limite_min: int,
    estancia: int,
) -> tuple[bool | None, str]:
    parseado = horarios.parsear(poi.horario_osm)
    if parseado is None:
        return None, "Horario sin verificar"
    fin_jornada = inicio_min + limite_min
    for dia in dias:
        for ini, fin in horarios.ventanas(parseado, dia):
            if min(fin, fin_jornada) - max(ini, inicio_min) >= estancia:
                return True, ""
    if len(dias) == 1 and dias[0] is not None:
        return False, f"Cerrado o sin tiempo de visita el {horarios.NOMBRES_DIA[dias[0]]}"
    return False, "Cerrado en el horario de tu visita"


def clasificar(
    pois: list[POICandidato],
    restricciones: Restricciones,
    presupuesto: str | None,
    inicio_min: int,
    limite_min: int,
    dias: list[int | None],
    origen: tuple[float, float] | None,
    config: Config,
    aplicar_restricciones: bool = True,
) -> Clasificacion:
    """Separa atractivos elegibles, sin verificar y excluidos, y baños usables."""
    res = Clasificacion()
    efectivas = restricciones if aplicar_restricciones else Restricciones()
    tope = ORDEN_PRESUPUESTO.get(presupuesto or "alto", 3)
    for poi in sorted(pois, key=lambda p: p.poi_id):
        if es_servicio(poi):
            costo = ORDEN_PRESUPUESTO.get((poi.costo_rango or "").lower(), 0)
            if (
                es_banio(poi)
                and banio_confiable(poi, efectivas, config)
                and horarios.parsear(poi.horario_osm) is not None
                and costo <= tope
            ):
                res.banios.append(poi)
            continue
        avisos: list[str] = []
        estancia = estancia_tipica(poi.categoria)

        # Duración.
        if estancia > limite_min:
            res.excluidos.append(
                (poi, f"No cabe en tu tiempo: la visita típica dura {estancia} min")
            )
            continue
        if origen is not None:
            ida = minutos_caminando(origen, (poi.lat, poi.lon), config)
            if ida + estancia > limite_min:
                res.excluidos.append(
                    (poi, f"No cabe en tu tiempo: está a {ida} min caminando más la visita")
                )
                continue

        # Horario.
        ok, motivo = _cabe_en_horario(poi, dias, inicio_min, limite_min, estancia)
        if ok is False:
            res.excluidos.append((poi, motivo))
            continue
        if ok is None:
            avisos.append("Horario sin verificar: confirma antes de ir")
        else:
            parseado = horarios.parsear(poi.horario_osm)
            cerrados = horarios.dias_cerrados(parseado) if parseado else []
            if dias == [None] and cerrados:
                nombres = ", ".join(horarios.NOMBRES_DIA[d] for d in cerrados)
                avisos.append(f"Cierra: {nombres}")

        # Presupuesto.
        if presupuesto is not None:
            costo = ORDEN_PRESUPUESTO.get((poi.costo_rango or "").lower())
            if costo is None:
                avisos.append("Costo sin verificar")
            elif costo > ORDEN_PRESUPUESTO[presupuesto]:
                res.excluidos.append(
                    (poi, f"Costo «{poi.costo_rango}» mayor que tu presupuesto «{presupuesto}»")
                )
                continue

        # Restricciones indispensables que dependen del lugar.
        if aplicar_restricciones:
            estado, motivo = cumple_restricciones_lugar(poi, restricciones, config)
            if estado == NO_CUMPLE:
                res.excluidos.append((poi, motivo))
                continue
            if estado == DESCONOCIDO:
                res.sin_verificar.append((poi, motivo))
                continue

        res.elegibles.append(poi)
        res.advertencias[poi.poi_id] = avisos
    return res
