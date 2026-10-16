"""Líneas base para la evaluación (§10.1).

Usan la misma secuenciación (inserción voraz + 2-opt, horarios y tiempo
total), pero no tienen restricciones inteligentes: no filtran por
accesibilidad (salvo la variante «filtro ingenuo»), no insertan descansos ni
baños. Pueden violar restricciones indispensables: eso es lo que se mide.

- ``popularidad``: utilidad = popularidad del lugar.
- ``cercania``: utilidad = 1 / (1 + minutos desde el origen).
- ``popularidad_filtro_ingenuo``: popularidad, y excluye solo los lugares con
  ``valor=no`` explícito; la falta de dato se trata como «accesible», que es
  el error que la constitución (XIII) prohíbe.
"""

from __future__ import annotations

from .config import CONFIG_DEFECTO, Config, popularidad
from .elegibilidad import ATR_SIN_ESCALONES, clasificar
from .geo import minutos_caminando
from .horarios import hora_a_minutos
from .motor import crear_contexto, metricas_plan
from .ranking import IndiceTfidf, origen_de_referencia
from .secuencia import construir_ruta
from .tipos import POICandidato, RespuestaRuta, SolicitudRuta


def _baseline(
    solicitud: SolicitudRuta,
    pois: list[POICandidato],
    nombre: str,
    config: Config,
) -> RespuestaRuta:
    inicio = hora_a_minutos(solicitud.hora_inicio)
    limite = int(round(solicitud.horas_disponibles * 60))
    clas = clasificar(
        pois,
        solicitud.restricciones,
        solicitud.presupuesto,
        inicio,
        limite,
        [solicitud.dia_semana],
        solicitud.punto_partida,
        config,
        aplicar_restricciones=False,
    )
    candidatos = list(clas.elegibles)
    if nombre == "popularidad_filtro_ingenuo" and solicitud.restricciones.sin_escalones:
        candidatos = [
            p
            for p in candidatos
            if not (
                (a := p.accesibilidad.get(ATR_SIN_ESCALONES))
                and (a.valor or "").strip().lower() in {"no", "limitado", "limited"}
            )
        ]
    origen = solicitud.punto_partida or origen_de_referencia(
        candidatos, solicitud.intereses, IndiceTfidf.construir(candidatos)
    )
    if nombre == "cercania":
        base = {
            p.poi_id: 1 / (1 + (minutos_caminando(origen, (p.lat, p.lon), config) if origen else 0))
            for p in candidatos
        }
    else:
        base = {p.poi_id: popularidad(p) for p in candidatos}
    candidatos = sorted(candidatos, key=lambda p: (-base[p.poi_id], p.poi_id))
    candidatos = candidatos[: config.max_candidatos]
    ctx = crear_contexto(
        candidatos,
        [],
        solicitud.punto_partida,
        inicio,
        limite,
        solicitud.dia_semana,
        solicitud.restricciones,
        config,
        inteligente=False,
    )
    plan, _ = construir_ruta(candidatos, lambda c, _r: base[c.poi_id], ctx)
    por_id = {p.poi_id: p for p in pois}
    metricas = metricas_plan(plan, por_id, config)
    metricas.update({"version": f"baseline-{nombre}", "tiempo_disponible_min": limite})
    for parada in plan.paradas:
        parada.motivo = f"Baseline {nombre}."
    return RespuestaRuta(
        paradas=plan.paradas,
        no_incluidos=[],
        alternativos=[],
        explicacion=f"Ruta de la línea base «{nombre}».",
        datos_desconocidos=[],
        metricas=metricas,
        motor=f"baseline-{nombre}",
    )


def recomendar_popularidad(
    solicitud: SolicitudRuta, pois: list[POICandidato], config: Config = CONFIG_DEFECTO
) -> RespuestaRuta:
    return _baseline(solicitud, pois, "popularidad", config)


def recomendar_cercania(
    solicitud: SolicitudRuta, pois: list[POICandidato], config: Config = CONFIG_DEFECTO
) -> RespuestaRuta:
    return _baseline(solicitud, pois, "cercania", config)


def recomendar_popularidad_filtro_ingenuo(
    solicitud: SolicitudRuta, pois: list[POICandidato], config: Config = CONFIG_DEFECTO
) -> RespuestaRuta:
    return _baseline(solicitud, pois, "popularidad_filtro_ingenuo", config)


BASELINES = {
    "popularidad": recomendar_popularidad,
    "cercania": recomendar_cercania,
    "popularidad_filtro_ingenuo": recomendar_popularidad_filtro_ingenuo,
}
