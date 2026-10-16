"""``recomendar()``: las cuatro etapas del recomendador inclusivo (§10.1)."""

from __future__ import annotations

from .config import CONFIG_DEFECTO, Config, es_alternativo, estancia_tipica
from .elegibilidad import (
    Clasificacion,
    banio_confiable,
    clasificar,
    es_servicio,
    ventanas_poi,
)
from .explicacion import (
    LIMITACION_TRAYECTOS,
    datos_desconocidos_poi,
    motivo_parada,
    resumen,
)
from .geo import haversine_m, zona
from .horarios import hora_a_minutos
from .ranking import IndiceTfidf, origen_de_referencia, puntuar
from .secuencia import Contexto, Plan, construir_ruta, utilidad_con_diversidad
from .tipos import (
    NoIncluido,
    Parada,
    POICandidato,
    RespuestaRuta,
    Restricciones,
    SolicitudRuta,
)

VERSION = "015-v1"


def crear_contexto(
    pois: list[POICandidato],
    banios: list[POICandidato],
    origen: tuple[float, float] | None,
    inicio_min: int,
    limite_min: int,
    dia: int | None,
    restricciones: Restricciones,
    config: Config,
    inteligente: bool = True,
) -> Contexto:
    todos = list(pois) + [b for b in banios if b not in pois]
    return Contexto(
        origen=origen,
        inicio_min=inicio_min,
        limite_min=limite_min,
        restricciones=restricciones,
        config=config,
        estancias={p.poi_id: estancia_tipica(p.categoria) for p in todos},
        ventanas={p.poi_id: ventanas_poi(p, dia) for p in todos},
        banios=list(banios) if inteligente else [],
        con_banio=frozenset(p.poi_id for p in todos if banio_confiable(p, restricciones, config)),
        inteligente=inteligente,
    )


def metricas_plan(plan: Plan, pois_por_id: dict[str, POICandidato], config: Config) -> dict:
    lugares = [
        pois_por_id[p.poi_id]
        for p in plan.paradas
        if p.poi_id in pois_por_id and pois_por_id[p.poi_id] in plan.secuencia
    ]
    n = len(lugares)
    return {
        "tiempo_usado_min": plan.total_min,
        "distancia_m": round(plan.distancia_m, 1),
        "n_paradas": n,
        "n_descansos": sum(1 for e in plan.eventos if e.tipo == "descanso"),
        "n_banios": sum(
            1
            for p in plan.paradas
            if p.poi_id in pois_por_id and pois_por_id[p.poi_id] not in plan.secuencia
        ),
        "zonas_distintas": len({zona(p.lat, p.lon, config) for p in lugares}),
        "destinos_distintos": len({p.destino_id for p in lugares if p.destino_id}),
        "cobertura_alternativos": (sum(1 for p in lugares if es_alternativo(p)) / n if n else 0.0),
        "linea_tiempo": [e.como_dict() for e in plan.eventos],
    }


def recomendar(
    solicitud: SolicitudRuta,
    pois: list[POICandidato],
    config: Config = CONFIG_DEFECTO,
) -> RespuestaRuta:
    inicio = hora_a_minutos(solicitud.hora_inicio)
    limite = int(round(solicitud.horas_disponibles * 60))
    r = solicitud.restricciones
    if solicitud.presupuesto is not None and solicitud.presupuesto not in (
        "gratis",
        "bajo",
        "medio",
        "alto",
    ):
        raise ValueError(f"Presupuesto no válido: {solicitud.presupuesto!r}")

    # Etapa 1: elegibilidad dura.
    clas: Clasificacion = clasificar(
        pois,
        r,
        solicitud.presupuesto,
        inicio,
        limite,
        [solicitud.dia_semana],
        solicitud.punto_partida,
        config,
    )

    # Etapa 2: ranking.
    atractivos = clas.elegibles + [p for p, _ in clas.sin_verificar]
    indice = IndiceTfidf.construir(atractivos or clas.elegibles)
    origen = solicitud.punto_partida or origen_de_referencia(
        clas.elegibles, solicitud.intereses, indice
    )
    puntajes = puntuar(atractivos, solicitud.intereses, origen, limite, config, indice)
    candidatos = sorted(clas.elegibles, key=lambda p: (-puntajes[p.poi_id].total, p.poi_id))
    candidatos = candidatos[: config.max_candidatos]

    # Etapa 3: secuenciación.
    ctx = crear_contexto(
        candidatos,
        clas.banios,
        solicitud.punto_partida,
        inicio,
        limite,
        solicitud.dia_semana,
        r,
        config,
    )
    base = {p.poi_id: puntajes[p.poi_id].total for p in candidatos}
    plan, sin_lugar = construir_ruta(candidatos, utilidad_con_diversidad(base, ctx), ctx)

    # Etapa 4: explicación.
    por_id = {p.poi_id: p for p in pois}
    en_ruta = {p.poi_id for p in plan.secuencia}
    paradas: list[Parada] = []
    previas = 0
    for parada in plan.paradas:
        poi = por_id.get(parada.poi_id)
        if poi is not None and poi.poi_id in en_ruta:
            parada.motivo = motivo_parada(
                poi, puntajes.get(poi.poi_id), parada.traslado_min, previas == 0, r, config
            )
            parada.advertencias = clas.advertencias.get(poi.poi_id, []) + parada.advertencias
            previas += 1
        paradas.append(parada)

    no_incluidos: list[NoIncluido] = [NoIncluido(p.poi_id, m) for p, m in clas.excluidos]
    descartados = {p.poi_id for p in sin_lugar}
    for p in sorted(clas.elegibles, key=lambda p: p.poi_id):
        if p.poi_id in en_ruta:
            continue
        if p.poi_id in descartados:
            no_incluidos.append(NoIncluido(p.poi_id, "No cabe en tu tiempo o en su horario"))
        else:
            no_incluidos.append(
                NoIncluido(p.poi_id, "Elegible, pero otros lugares aprovechan mejor tu tiempo")
            )

    sin_verificar = sorted(
        clas.sin_verificar, key=lambda t: (-puntajes[t[0].poi_id].total, t[0].poi_id)
    )
    alternativos: list[str] = []
    detalle_alt: list[dict] = []
    datos_desconocidos: list[str] = []
    if solicitud.incluir_alternativos:
        for p, motivo in sin_verificar[: config.max_alternativos]:
            alternativos.append(p.poi_id)
            detalle_alt.append(
                {"poi_id": p.poi_id, "nombre": p.nombre, "motivo": motivo, "sin_verificar": True}
            )
            datos_desconocidos.append(f"{p.nombre}: {motivo}. Solo se ofrece como alternativa.")
        territoriales = [p for p in candidatos if es_alternativo(p) and p.poi_id not in en_ruta][:2]
        for p in territoriales:
            alternativos.append(p.poi_id)
            detalle_alt.append(
                {
                    "poi_id": p.poi_id,
                    "nombre": p.nombre,
                    "motivo": "Destino alternativo que cumple tus necesidades",
                    "sin_verificar": False,
                }
            )
    else:
        for p, motivo in sin_verificar:
            no_incluidos.append(NoIncluido(p.poi_id, motivo))

    n_no_incluidos_total = len(no_incluidos)
    if len(no_incluidos) > config.max_no_incluidos and origen is not None:
        # Se conservan los más cercanos: son los que la persona reconocería.
        def distancia(n: NoIncluido) -> tuple[float, str]:
            p = por_id.get(n.poi_id)
            d = haversine_m(origen, (p.lat, p.lon)) if p else float("inf")
            return (d, n.poi_id)

        no_incluidos = sorted(no_incluidos, key=distancia)[: config.max_no_incluidos]
    else:
        no_incluidos = no_incluidos[: config.max_no_incluidos]

    for p in plan.secuencia:
        datos_desconocidos.extend(datos_desconocidos_poi(p, r))
    datos_desconocidos.append(LIMITACION_TRAYECTOS)

    metricas = metricas_plan(plan, por_id, config)
    metricas.update(
        {
            "version": VERSION,
            "tiempo_disponible_min": limite,
            "n_candidatos": len([p for p in pois if not es_servicio(p)]),
            "n_elegibles": len(clas.elegibles),
            "n_excluidos": len(clas.excluidos),
            "n_sin_verificar": len(clas.sin_verificar),
            "n_no_incluidos_total": n_no_incluidos_total,
            "alternativos_detalle": detalle_alt,
            "puntajes": {
                pid: {
                    "total": round(puntajes[pid].total, 4),
                    "pertinencia": round(puntajes[pid].pertinencia, 4),
                    "cercania": round(puntajes[pid].cercania, 4),
                    "diversidad": round(puntajes[pid].diversidad, 4),
                    "calidad": round(puntajes[pid].calidad, 4),
                    "esfuerzo": round(puntajes[pid].esfuerzo, 4),
                }
                for pid in sorted(en_ruta)
            },
            "pesos": config.pesos.__dict__,
        }
    )
    explicacion = resumen(
        metricas["n_paradas"],
        plan.total_min,
        limite,
        metricas["zonas_distintas"],
        r,
        len(clas.sin_verificar),
        metricas["n_descansos"],
        metricas["n_banios"],
    )
    return RespuestaRuta(
        paradas=paradas,
        no_incluidos=no_incluidos,
        alternativos=alternativos,
        explicacion=explicacion,
        datos_desconocidos=datos_desconocidos,
        metricas=metricas,
        motor=VERSION,
    )
