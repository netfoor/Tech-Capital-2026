"""Recomendador de itinerarios inclusivos.

PROVISIONAL (spec 014): motor voraz por cercanía que respeta las restricciones duras. La spec 015
lo reemplaza con el motor real sin cambiar la interfaz:

    recomendar(solicitud: SolicitudRuta, pois: list[POICandidato]) -> RespuestaRuta
    recomendar_multidia(solicitud: SolicitudMultidia, pois: list[POICandidato],
                        alternativas: list[POICandidato]) -> RespuestaMultidia
"""

import math

from app.recommender.tipos import (
    ATRIBUTOS_CLAVE,
    DiaPlan,
    NoIncluido,
    Parada,
    POICandidato,
    RespuestaMultidia,
    RespuestaRuta,
    Restricciones,
    SolicitudMultidia,
    SolicitudRuta,
)

MOTOR = "provisional-voraz-cercania"
ORDEN_COSTO = {"gratis": 0, "bajo": 1, "medio": 2, "alto": 3}
ESTANCIA_MIN = {
    "museo": 60,
    "zona_arqueologica": 90,
    "restaurante": 75,
    "cafeteria": 30,
    "plaza": 30,
    "mercado": 45,
    "mirador": 30,
    "templo": 30,
}
RADIO_KM = 15.0
MAX_PARADAS = 8
MAX_NO_INCLUIDOS = 50
DESCANSO_MIN = 10

__all__ = ["MOTOR", "recomendar", "recomendar_multidia"]


def distancia_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = (
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    )
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def traslado_min(km: float) -> float:
    if km <= 2:
        return round(km / 4.0 * 60, 1)  # a pie, 4 km/h
    return round(km / 30.0 * 60 + 10, 1)  # vehículo, 30 km/h más 10 min de ascenso y espera


def _pos(poi: POICandidato) -> tuple[float, float]:
    return (poi.lat, poi.lon)


def motivo_exclusion(
    poi: POICandidato, r: Restricciones, presupuesto: str | None = None
) -> str | None:
    """Motivo por el que el POI incumple una restricción dura; None si la cumple."""
    for activa, atributo, etiqueta in (
        (r.sin_escalones, "acceso_sin_escalones", "sin escalones"),
        (r.banio_accesible, "banio_accesible", "baño accesible"),
    ):
        if not activa:
            continue
        dato = poi.accesibilidad.get(atributo)
        if dato is None or dato.valor is None:
            return f"No cumple «{etiqueta}»: dato sin verificar"
        if dato.valor != "si":
            return f"No cumple «{etiqueta}»: valor «{dato.valor}» ({dato.estado})"
    if r.pendiente_max_pct is not None:
        dato = poi.accesibilidad.get("pendiente_pct")
        if dato is None or dato.valor is None:
            return "No cumple «pendiente máxima»: dato sin verificar"
        try:
            if float(dato.valor) > r.pendiente_max_pct:
                return f"No cumple «pendiente máxima»: {dato.valor} % > {r.pendiente_max_pct} %"
        except ValueError:
            return "No cumple «pendiente máxima»: dato no numérico"
    if presupuesto is not None:
        if poi.costo_rango is None:
            return "Costo sin dato: no se puede asegurar el presupuesto"
        if ORDEN_COSTO[poi.costo_rango] > ORDEN_COSTO[presupuesto]:
            return f"Costo «{poi.costo_rango}» mayor al presupuesto «{presupuesto}»"
    return None


def _advertencias(poi: POICandidato) -> list[str]:
    avisos = []
    for atributo in ATRIBUTOS_CLAVE:
        dato = poi.accesibilidad.get(atributo)
        if dato is None or dato.valor is None:
            avisos.append(f"«{atributo}» sin verificar")
        elif dato.estado != "verificado":
            avisos.append(f"«{atributo}» = {dato.valor}, {dato.estado}")
    return avisos


def _costo(
    poi: POICandidato, actual: tuple[float, float] | None, intereses: set[str]
) -> tuple[int, float, str]:
    """Primero los intereses al arrancar sin punto de partida; después la distancia ponderada."""
    interesa = poi.categoria in intereses
    if actual is None:
        return (0 if interesa else 1, 0.0, poi.poi_id)
    km = distancia_km(actual, _pos(poi))
    return (0, km * (0.5 if interesa else 1.0), poi.poi_id)


def _secuenciar(
    candidatos: list[POICandidato],
    inicio: tuple[float, float] | None,
    minutos: float,
    restricciones: Restricciones,
    intereses: set[str],
) -> tuple[list[Parada], list[POICandidato]]:
    """Vecino más cercano con preferencia por intereses, dentro del tiempo disponible."""
    restantes = sorted(candidatos, key=lambda p: p.poi_id)
    paradas: list[Parada] = []
    reloj, desde_descanso = 0.0, 0.0
    actual = inicio
    while restantes and len(paradas) < MAX_PARADAS:
        elegido = min(restantes, key=lambda p, a=actual: _costo(p, a, intereses))
        km = distancia_km(actual, _pos(elegido)) if actual else 0.0
        viaje = traslado_min(km) if actual else 0.0
        estancia = float(ESTANCIA_MIN.get(elegido.categoria, 45))
        avisos = _advertencias(elegido)
        descanso = 0.0
        if restricciones.descansos_cada_min and desde_descanso >= restricciones.descansos_cada_min:
            descanso = DESCANSO_MIN
            avisos.append(f"Descanso de {DESCANSO_MIN} min antes de esta parada")
        if reloj + viaje + descanso + estancia > minutos:
            break
        llegada = reloj + viaje + descanso
        motivo = "Coincide con tus intereses" if elegido.categoria in intereses else "Cercanía"
        if km:
            motivo += f"; a {km:.1f} km de la parada anterior"
        paradas.append(
            Parada(
                orden=len(paradas) + 1,
                poi_id=elegido.poi_id,
                llegada_min=round(llegada, 1),
                estancia_min=estancia,
                traslado_min=viaje,
                motivo=motivo,
                advertencias=avisos,
            )
        )
        reloj = llegada + estancia
        desde_descanso = 0.0 if descanso else desde_descanso + viaje + estancia
        actual = _pos(elegido)
        restantes.remove(elegido)
    return paradas, restantes


def _desconocidos(paradas: list[Parada], indice: dict[str, POICandidato]) -> list[str]:
    salida = []
    for parada in paradas:
        poi = indice[parada.poi_id]
        for atributo in ATRIBUTOS_CLAVE:
            dato = poi.accesibilidad.get(atributo)
            if dato is None or dato.valor is None:
                salida.append(f"{atributo} en {poi.nombre}")
    return salida


def _alternativos(
    elegibles: list[POICandidato], excluir: set[str], destinos: set[str], centro, n: int = 2
) -> list[str]:
    opciones = [p for p in elegibles if p.poi_id not in excluir and p.destino_id not in destinos]
    if centro is not None:
        opciones.sort(key=lambda p: (distancia_km(centro, _pos(p)), p.poi_id))
    else:
        opciones.sort(key=lambda p: p.poi_id)
    return [p.poi_id for p in opciones[:n]]


def recomendar(solicitud: SolicitudRuta, pois: list[POICandidato]) -> RespuestaRuta:
    r = solicitud.restricciones
    indice = {p.poi_id: p for p in pois}
    elegibles, no_incluidos = [], []
    for poi in pois:
        motivo = motivo_exclusion(poi, r, solicitud.presupuesto)
        if motivo:
            no_incluidos.append((poi, motivo))
        else:
            elegibles.append(poi)

    intereses = set(solicitud.intereses)
    inicio = solicitud.punto_partida
    if inicio is not None:
        zona = [p for p in elegibles if distancia_km(inicio, _pos(p)) <= RADIO_KM]
        cerca = lambda p: distancia_km(inicio, _pos(p)) <= RADIO_KM  # noqa: E731
    else:
        semilla = min(
            elegibles, key=lambda p: (p.categoria not in intereses, p.poi_id), default=None
        )
        destino = semilla.destino_id if semilla else None
        zona = [p for p in elegibles if p.destino_id == destino]
        cerca = lambda p: p.destino_id == destino  # noqa: E731

    paradas, _ = _secuenciar(zona, inicio, solicitud.horas_disponibles * 60, r, intereses)
    incluidos = {p.poi_id for p in paradas}
    excluidos = [
        NoIncluido(p.poi_id, m)
        for p, m in sorted(no_incluidos, key=lambda x: x[0].poi_id)
        if cerca(p)
    ][:MAX_NO_INCLUIDOS]

    alternativos: list[str] = []
    if solicitud.incluir_alternativos and paradas:
        destinos = {indice[p.poi_id].destino_id for p in paradas}
        ultimo = _pos(indice[paradas[-1].poi_id])
        alternativos = _alternativos(elegibles, incluidos, destinos, ultimo)

    explicacion = (
        f"Itinerario de {len(paradas)} paradas en {solicitud.horas_disponibles:g} h, "
        "ordenado por cercanía y tus intereses. Solo se incluyen lugares que cumplen tus "
        "restricciones con un dato registrado; los tramos sin verificar se marcan en cada parada."
    )
    if not paradas:
        explicacion = "Ningún lugar cumple tus restricciones con datos registrados en esta zona."
    return RespuestaRuta(
        paradas=paradas,
        no_incluidos=excluidos,
        alternativos=alternativos,
        explicacion=explicacion,
        datos_desconocidos=_desconocidos(paradas, indice),
        motor=MOTOR,
    )


def recomendar_multidia(
    solicitud: SolicitudMultidia,
    pois: list[POICandidato],
    alternativas: list[POICandidato] | None = None,
) -> RespuestaMultidia:
    r = solicitud.restricciones
    no_incluidos: list[NoIncluido] = []
    elegibles = []
    for poi in sorted(pois, key=lambda p: (p.destino_id, p.poi_id)):
        motivo = motivo_exclusion(poi, r)
        if motivo:
            no_incluidos.append(NoIncluido(poi.poi_id, motivo))
        else:
            elegibles.append(poi)

    dias: list[DiaPlan] = []
    restantes = elegibles
    for dia in range(1, solicitud.dias + 1):
        if not restantes:
            break
        # Cada día empieza en el destino con más lugares pendientes: agrupa por cercanía.
        conteo: dict[str, int] = {}
        for p in restantes:
            conteo[p.destino_id] = conteo.get(p.destino_id, 0) + 1
        destino = min(conteo, key=lambda d: (-conteo[d], d))
        del_destino = [p for p in restantes if p.destino_id == destino]
        otros = [p for p in restantes if p.destino_id != destino]
        paradas, sobrantes = _secuenciar(del_destino, None, solicitud.horas_por_dia * 60, r, set())
        if not paradas:
            no_incluidos += [
                NoIncluido(p.poi_id, "Su estancia no cabe en las horas del día")
                for p in del_destino
            ]
            restantes = otros
            continue
        dias.append(DiaPlan(dia=dia, paradas=paradas))
        restantes = sobrantes + otros
    no_incluidos += [
        NoIncluido(p.poi_id, f"No cabe en {solicitud.dias} día(s) de {solicitud.horas_por_dia:g} h")
        for p in sorted(restantes, key=lambda p: p.poi_id)
    ]

    incluidos = {p.poi_id for d in dias for p in d.paradas}
    alternativos: list[str] = []
    if alternativas and dias:
        indice = {p.poi_id: p for p in pois}
        destinos = {indice[i].destino_id for i in incluidos}
        lat = sum(indice[i].lat for i in incluidos) / len(incluidos)
        lon = sum(indice[i].lon for i in incluidos) / len(incluidos)
        candidatas = [p for p in alternativas if motivo_exclusion(p, r) is None]
        alternativos = _alternativos(candidatas, incluidos, destinos, (lat, lon))
    return RespuestaMultidia(
        dias=dias,
        no_incluidos=no_incluidos,
        alternativos=alternativos,
        explicacion=(
            f"Plan de {len(dias)} día(s) agrupado por destino y cercanía. Los lugares que no "
            "cumplen tus restricciones o no caben se listan con su motivo."
        ),
        motor=MOTOR,
    )
