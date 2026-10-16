"""Itinerario multi-día desde guardados (§04.4 L3 y §10.1).

1. Etapa 1 igual que en una ruta: lo que no cumple o no se puede verificar
   sale en ``no_incluidos`` con su motivo.
2. Agrupamiento espacial con capacidad: k-means++ (semilla fija) con
   asignación por arrepentimiento (regret) respetando las horas por día.
3. Secuenciación por día con la misma etapa 3 (inserción + 2-opt) y los
   horarios del día de la semana correspondiente.
4. Reubicación: lo que no cupo en su día se intenta en los demás.
"""

from __future__ import annotations

import random
from dataclasses import replace

from .config import CONFIG_DEFECTO, Config, es_alternativo, estancia_tipica
from .elegibilidad import clasificar, es_banio, es_servicio
from .explicacion import motivo_parada
from .geo import haversine_m, minutos_caminando, segmentos_se_cruzan
from .horarios import hora_a_minutos
from .motor import crear_contexto
from .secuencia import Contexto, Plan, _dos_opt, construir_ruta, simular
from .tipos import DiaPlan, NoIncluido, POICandidato, RespuestaMultidia, SolicitudMultidia

HOLGURA_TRASLADO_MIN = 10


def _dias_distintos(dias: list[int | None]) -> list[int | None]:
    return sorted(set(dias), key=lambda d: -1 if d is None else d)


def _kmeans_capacidad(
    puntos: list[POICandidato], k: int, capacidad: float, semilla: int
) -> list[list[POICandidato]]:
    rng = random.Random(semilla)
    coords = {p.poi_id: (p.lat, p.lon) for p in puntos}
    demanda = {p.poi_id: estancia_tipica(p.categoria) + HOLGURA_TRASLADO_MIN for p in puntos}
    # k-means++ determinista.
    centros = [coords[puntos[rng.randrange(len(puntos))].poi_id]]
    while len(centros) < k:
        d2 = [min(haversine_m(coords[p.poi_id], c) ** 2 for c in centros) for p in puntos]
        total = sum(d2)
        if total == 0:
            centros.append(coords[puntos[len(centros)].poi_id])
            continue
        umbral = rng.random() * total
        acumulado = 0.0
        for p, d in zip(puntos, d2, strict=True):
            acumulado += d
            if acumulado >= umbral:
                centros.append(coords[p.poi_id])
                break
    asignacion: dict[str, int] = {}
    for _ in range(50):

        def arrepentimiento(p: POICandidato) -> tuple[float, str]:
            ds = sorted(haversine_m(coords[p.poi_id], c) for c in centros)
            return (-(ds[1] - ds[0]) if len(ds) > 1 else 0.0, p.poi_id)

        carga = [0.0] * k
        nueva: dict[str, int] = {}
        for p in sorted(puntos, key=arrepentimiento):
            orden = sorted(range(k), key=lambda i: (haversine_m(coords[p.poi_id], centros[i]), i))
            elegido = next(
                (i for i in orden if carga[i] + demanda[p.poi_id] <= capacidad), orden[0]
            )
            nueva[p.poi_id] = elegido
            carga[elegido] += demanda[p.poi_id]
        for i in range(k):
            miembros = [coords[pid] for pid, c in nueva.items() if c == i]
            if miembros:
                centros[i] = (
                    sum(m[0] for m in miembros) / len(miembros),
                    sum(m[1] for m in miembros) / len(miembros),
                )
        if nueva == asignacion:
            break
        asignacion = nueva
    grupos = [[p for p in puntos if asignacion[p.poi_id] == i] for i in range(k)]
    # Orden estable de los días: de oeste a este por centroide.
    return sorted(
        grupos,
        key=lambda g: (
            (sum(p.lon for p in g) / len(g), min(p.poi_id for p in g)) if g else (1e9, "")
        ),
    )


def _insertar(plan: Plan, poi: POICandidato, ctx: Contexto) -> Plan | None:
    mejor: Plan | None = None
    for pos in range(len(plan.secuencia) + 1):
        nueva = plan.secuencia[:pos] + [poi] + plan.secuencia[pos:]
        p = simular(nueva, ctx)
        if p is not None and (mejor is None or p.total_min < mejor.total_min):
            mejor = p
    return _dos_opt(mejor, ctx) if mejor else None


def _segmentos(plan: Plan) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    pts = [(p.lat, p.lon) for p in plan.secuencia]
    return list(zip(pts, pts[1:], strict=False))


def _cruces(planes: list[Plan]) -> int:
    total = 0
    segs = [_segmentos(p) for p in planes]
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            for a in segs[i]:
                for b in segs[j]:
                    if segmentos_se_cruzan(a[0], a[1], b[0], b[1]):
                        total += 1
    return total


def _orden_ingenuo(
    seleccion: list[POICandidato], contextos: list[Contexto]
) -> tuple[list[Plan], int]:
    """Orden del usuario partido en días consecutivos, sin reordenar."""
    planes: list[Plan] = []
    dia = 0
    actual: list[POICandidato] = []
    no_asignados = 0
    for poi in seleccion:
        while dia < len(contextos):
            if simular(actual + [poi], contextos[dia]) is not None:
                actual.append(poi)
                break
            if not actual:
                no_asignados += 1  # no cabe ni solo en este día
                break
            planes.append(simular(actual, contextos[dia]))  # type: ignore[arg-type]
            actual = []
            dia += 1
        else:
            no_asignados += 1
    if actual and dia < len(contextos):
        planes.append(simular(actual, contextos[dia]))  # type: ignore[arg-type]
    return planes, no_asignados


def planear_multidia(
    solicitud: SolicitudMultidia,
    pois: list[POICandidato],
    config: Config = CONFIG_DEFECTO,
) -> RespuestaMultidia:
    if solicitud.dias < 1:
        raise ValueError("dias debe ser al menos 1")
    inicio = hora_a_minutos(solicitud.hora_inicio)
    limite = int(round(solicitud.horas_por_dia * 60))
    r = solicitud.restricciones
    por_id = {p.poi_id: p for p in pois}
    dias_semana: list[int | None] = (
        [(solicitud.dia_semana_inicio + d) % 7 for d in range(solicitud.dias)]
        if solicitud.dia_semana_inicio is not None
        else [None] * solicitud.dias
    )

    no_incluidos: list[NoIncluido] = []
    vistos: set[str] = set()
    seleccion_ids: list[str] = []
    for pid in solicitud.poi_ids:
        if pid in vistos:
            continue
        vistos.add(pid)
        if pid not in por_id:
            no_incluidos.append(NoIncluido(pid, "No está en el catálogo"))
        else:
            seleccion_ids.append(pid)
    seleccion = [por_id[pid] for pid in seleccion_ids]

    clas = clasificar(
        seleccion + [p for p in pois if p.poi_id not in vistos and es_banio(p)],
        r,
        None,
        inicio,
        limite,
        _dias_distintos(dias_semana),
        None,
        config,
    )
    no_incluidos += [NoIncluido(p.poi_id, m) for p, m in clas.excluidos]
    no_incluidos += [
        NoIncluido(p.poi_id, f"{m}. No se incluye: verifícalo antes de ir")
        for p, m in clas.sin_verificar
    ]
    elegibles_ids = {p.poi_id for p in clas.elegibles}
    elegibles = [p for p in seleccion if p.poi_id in elegibles_ids]

    contextos = [
        crear_contexto(elegibles, clas.banios, None, inicio, limite, dia, r, config)
        for dia in dias_semana
    ]
    planes: list[Plan] = [simular([], c) for c in contextos]  # type: ignore[misc]
    pendientes: list[POICandidato] = []
    if elegibles:
        k = min(solicitud.dias, len(elegibles))
        grupos = _kmeans_capacidad(elegibles, k, limite, config.semilla)
        for i, grupo in enumerate(grupos):
            plan, sobrantes = construir_ruta(grupo, lambda c, _r: 1.0, contextos[i])
            planes[i] = plan
            en_plan = {p.poi_id for p in plan.secuencia}
            pendientes += [p for p in grupo if p.poi_id not in en_plan]
        # Reubicación en otros días, del más cercano al más lejano.
        for poi in sorted(pendientes, key=lambda p: p.poi_id):

            def distancia_dia(i: int, poi: POICandidato = poi) -> float:
                seq = planes[i].secuencia
                if not seq:
                    return 0.0
                return min(haversine_m((poi.lat, poi.lon), (q.lat, q.lon)) for q in seq)

            colocado = False
            for i in sorted(range(len(planes)), key=lambda i: (distancia_dia(i), i)):
                nuevo = _insertar(planes[i], poi, contextos[i])
                if nuevo is not None:
                    planes[i] = nuevo
                    colocado = True
                    break
            if not colocado:
                no_incluidos.append(
                    NoIncluido(
                        poi.poi_id,
                        f"No cabe en {solicitud.dias} día(s) de {solicitud.horas_por_dia:g} h "
                        "por tiempo u horario",
                    )
                )

    dias: list[DiaPlan] = []
    for numero, plan in enumerate(planes, start=1):
        primera = True
        for parada in plan.paradas:
            poi = por_id.get(parada.poi_id)
            if poi is not None and poi in plan.secuencia:
                parada.motivo = "Lo guardaste. " + motivo_parada(
                    poi, None, parada.traslado_min, primera, r, config
                )
                parada.advertencias = clas.advertencias.get(poi.poi_id, []) + parada.advertencias
                primera = False
        dias.append(DiaPlan(dia=numero, paradas=plan.paradas))

    # Sugerencias territoriales: hasta 2 destinos alternativos cercanos.
    alternativos: list[str] = []
    if solicitud.incluir_alternativos and any(p.secuencia for p in planes):
        otros = [
            p for p in pois if p.poi_id not in vistos and es_alternativo(p) and not es_servicio(p)
        ]
        clas_otros = clasificar(
            otros,
            r,
            None,
            inicio,
            limite,
            _dias_distintos(dias_semana),
            None,
            config,
        )
        en_ruta = [q for plan in planes for q in plan.secuencia]

        def cercania(p: POICandidato) -> tuple[int, str]:
            return (
                min(minutos_caminando((p.lat, p.lon), (q.lat, q.lon), config) for q in en_ruta),
                p.poi_id,
            )

        cercanos = sorted((p for p in clas_otros.elegibles if cercania(p)[0] <= 20), key=cercania)
        alternativos = [p.poi_id for p in cercanos[:2]]

    ingenuo, no_asig_ingenuo = _orden_ingenuo(elegibles, contextos)
    asignados = [q.poi_id for plan in planes for q in plan.secuencia]
    metricas = {
        "version": "015-v1",
        "n_seleccionados": len(seleccion_ids),
        "n_asignados": len(asignados),
        "n_no_asignados": len(seleccion_ids) - len(asignados),
        "distancia_total_m": round(sum(p.distancia_m for p in planes), 1),
        "distancia_orden_ingenuo_m": round(sum(p.distancia_m for p in ingenuo), 1),
        "n_asignados_orden_ingenuo": sum(len(p.secuencia) for p in ingenuo),
        "n_no_asignados_orden_ingenuo": no_asig_ingenuo,
        "cruces_entre_dias": _cruces(planes),
        "cruces_entre_dias_orden_ingenuo": _cruces(ingenuo),
        "tiempo_por_dia_min": [p.total_min for p in planes],
        "tiempo_disponible_por_dia_min": limite,
        "linea_tiempo_por_dia": [[e.como_dict() for e in p.eventos] for p in planes],
        "dias_semana": dias_semana,
    }
    n_asig = len(asignados)
    explicacion = (
        f"Plan de {solicitud.dias} día(s) de {solicitud.horas_por_dia:g} h con {n_asig} de "
        f"{len(seleccion_ids)} lugar(es) guardado(s), agrupados por cercanía y horario."
    )
    if len(seleccion_ids) - n_asig:
        explicacion += (
            f" {len(seleccion_ids) - n_asig} quedaron fuera; cada uno dice por qué en "
            "«no incluidos»."
        )
    if r.alguna():
        explicacion += " No relajamos ninguna restricción indispensable."
    if alternativos:
        explicacion += " Sugerimos destinos alternativos cercanos, marcados como sugerencia."
    return RespuestaMultidia(
        dias=dias,
        no_incluidos=no_incluidos,
        alternativos=alternativos,
        explicacion=explicacion,
        metricas=metricas,
        motor="015-v1",
    )


def recomendar_multidia(
    solicitud: SolicitudMultidia,
    pois: list[POICandidato],
    alternativas: list[POICandidato] | None = None,
    config: Config = CONFIG_DEFECTO,
) -> RespuestaMultidia:
    """Firma que usa el endpoint de la spec 014: ``pois`` son los guardados elegidos y
    ``alternativas`` el resto del catálogo (fuente de baños y de sugerencias)."""
    if not solicitud.poi_ids:
        solicitud = replace(solicitud, poi_ids=[p.poi_id for p in pois])
    vistos = {p.poi_id for p in pois}
    catalogo = list(pois) + [p for p in (alternativas or []) if p.poi_id not in vistos]
    return planear_multidia(solicitud, catalogo, config)
