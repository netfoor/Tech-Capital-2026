"""Verificador independiente de restricciones.

Recalcula las violaciones a partir de la línea de tiempo de la respuesta y del
catálogo, sin reutilizar la lógica de elegibilidad ni del simulador: es la
fuente de verdad de las pruebas y de la evaluación offline. Sirve igual para
el motor y para las baselines.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import horarios
from .config import CONFIG_DEFECTO, ORDEN_PRESUPUESTO, Config
from .tipos import POICandidato, RespuestaRuta, SolicitudRuta

INDISPENSABLES = ("sin_escalones", "pendiente", "banio_accesible", "descansos")


@dataclass(frozen=True)
class Violacion:
    tipo: str
    poi_id: str | None
    detalle: str


def _si_confiable(poi: POICandidato, atributo: str, minimo: float) -> bool:
    a = poi.accesibilidad.get(atributo)
    if a is None or a.estado == "reportado":
        return False
    if a.valor.strip().lower() not in {"si", "sí", "yes", "true", "designated", "1"}:
        return False
    return a.estado == "verificado" or (a.estado == "sin_verificar" and a.confianza >= minimo)


def _pendiente_confiable(poi: POICandidato, maximo: float, minimo: float) -> bool:
    a = poi.accesibilidad.get("pendiente_pct")
    if a is None or a.estado == "reportado":
        return False
    try:
        valor = float(a.valor.strip().rstrip("%"))
    except ValueError:
        return False
    if valor > maximo:
        return False
    return a.estado == "verificado" or (a.estado == "sin_verificar" and a.confianza >= minimo)


def verificar(
    respuesta: RespuestaRuta,
    solicitud: SolicitudRuta,
    pois_por_id: dict[str, POICandidato],
    config: Config = CONFIG_DEFECTO,
) -> list[Violacion]:
    r = solicitud.restricciones
    v: list[Violacion] = []
    eventos = respuesta.metricas.get("linea_tiempo", [])
    limite = int(round(solicitud.horas_disponibles * 60))
    inicio = horarios.hora_a_minutos(solicitud.hora_inicio)
    minimo = config.confianza_minima

    lugares = [p.poi_id for p in respuesta.paradas if p.poi_id in pois_por_id]

    # Lugares: escalones, pendiente, presupuesto, duplicados.
    vistos: set[str] = set()
    for pid in lugares:
        poi = pois_por_id[pid]
        if r.sin_escalones and not _si_confiable(poi, "acceso_sin_escalones", minimo):
            v.append(Violacion("sin_escalones", pid, "acceso sin escalones no confiable"))
        if r.pendiente_max_pct is not None and not _pendiente_confiable(
            poi, r.pendiente_max_pct, minimo
        ):
            v.append(Violacion("pendiente", pid, "pendiente no confiable o mayor"))
        if solicitud.presupuesto is not None:
            costo = ORDEN_PRESUPUESTO.get((poi.costo_rango or "").lower())
            if costo is not None and costo > ORDEN_PRESUPUESTO[solicitud.presupuesto]:
                v.append(Violacion("presupuesto", pid, f"costo {poi.costo_rango}"))
        if pid in vistos and poi.categoria not in ("banio", "sanitario", "toilets"):
            v.append(Violacion("duplicado", pid, "lugar repetido"))
        vistos.add(pid)

    # Tiempo total.
    fin = max((e["fin"] for e in eventos), default=0)
    if fin > limite:
        v.append(Violacion("tiempo", None, f"{fin} min de {limite} disponibles"))

    # Horarios verificables.
    for e in eventos:
        if e["tipo"] not in ("visita", "banio") or e["poi_id"] not in pois_por_id:
            continue
        parseado = horarios.parsear(pois_por_id[e["poi_id"]].horario_osm)
        if parseado is None:
            continue
        ventanas = horarios.ventanas(parseado, solicitud.dia_semana)
        a, b = inicio + e["inicio"], inicio + e["fin"]
        if not any(ini <= a and b <= fin_v for ini, fin_v in ventanas):
            v.append(Violacion("horario", e["poi_id"], f"visita fuera de horario ({a}-{b})"))

    # Descansos.
    if r.descansos_cada_min:
        continuo = 0
        for e in sorted(eventos, key=lambda x: x["inicio"]):
            dur = e["fin"] - e["inicio"]
            if e["tipo"] == "descanso" and dur >= config.duracion_descanso_min:
                continuo = 0
                continue
            continuo += dur
            if continuo > r.descansos_cada_min:
                v.append(
                    Violacion("descansos", e["poi_id"], f"{continuo} min continuos sin descanso")
                )
                break

    # Baños accesibles.
    if r.banio_accesible:
        ultimo = 0
        peor = 0
        for e in sorted(eventos, key=lambda x: x["inicio"]):
            pid = e["poi_id"]
            if e["tipo"] not in ("visita", "banio") or pid not in pois_por_id:
                continue
            poi = pois_por_id[pid]
            ok = _si_confiable(poi, "banio_accesible", minimo)
            if ok and r.sin_escalones:
                ok = _si_confiable(poi, "acceso_sin_escalones", minimo)
            if ok and r.pendiente_max_pct is not None:
                ok = _pendiente_confiable(poi, r.pendiente_max_pct, minimo)
            if not ok:
                continue
            peor = max(peor, e["inicio"] - ultimo)
            ultimo = e["fin"]
        peor = max(peor, fin - ultimo)
        if peor > config.intervalo_banio_min:
            v.append(Violacion("banio_accesible", None, f"{peor} min sin baño accesible"))
    return v


def violaciones_indispensables(violaciones: list[Violacion]) -> list[Violacion]:
    return [x for x in violaciones if x.tipo in INDISPENSABLES]
