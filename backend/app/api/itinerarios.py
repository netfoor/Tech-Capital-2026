"""Itinerarios. No requieren cuenta; con token se asocian a la persona.

El punto de partida se usa para calcular y nunca se guarda (minimización, §14).
"""

from fastapi import APIRouter
from sqlalchemy import select

from app import recommender
from app.api.deps import Sesion
from app.models import (
    Itinerary,
    ItineraryDay,
    ItineraryStop,
    PointOfInterest,
    Recommendation,
)
from app.recommender import tipos
from app.schemas.itinerarios import (
    Dia,
    NoIncluido,
    Parada,
    RespuestaDesdeGuardados,
    RespuestaRecomendar,
    Restricciones,
    SolicitudDesdeGuardados,
    SolicitudRecomendar,
)
from app.services import catalogo
from app.services.seguridad import UsuarioOpcional

router = APIRouter(prefix="/itineraries", tags=["itinerarios"])


def _restricciones(r: Restricciones | None) -> tipos.Restricciones:
    if r is None:
        return tipos.Restricciones()
    return tipos.Restricciones(
        sin_escalones=bool(r.sin_escalones),
        banio_accesible=bool(r.banio_accesible),
        descansos_cada_min=r.descansos_cada_min,
        pendiente_max_pct=r.pendiente_max_pct,
    )


def _guardar(
    s: Sesion,
    usuario,
    modo: str,
    solicitud: dict,
    explicacion: str,
    motor: str,
    dias: list[tuple[int, list[tipos.Parada]]],
    no_incluidos: list[tipos.NoIncluido],
    alternativos: list[str],
) -> Itinerary:
    itinerario = Itinerary(
        user_id=usuario.id if usuario else None,
        modo=modo,
        solicitud=solicitud,
        explicacion=explicacion,
        motor=motor,
    )
    for numero, paradas in dias:
        dia = ItineraryDay(dia=numero)
        dia.paradas = [
            ItineraryStop(
                orden=p.orden,
                poi_id=p.poi_id,
                llegada_min=p.llegada_min,
                estancia_min=p.estancia_min,
                traslado_min=p.traslado_min,
                motivo=p.motivo,
                advertencias=list(p.advertencias),
            )
            for p in paradas
        ]
        itinerario.dias.append(dia)
    s.add(itinerario)
    s.flush()
    filas = [
        Recommendation(itinerary_id=itinerario.id, poi_id=p.poi_id, incluido=True, motivo=p.motivo)
        for _, paradas in dias
        for p in paradas
    ]
    filas += [
        Recommendation(itinerary_id=itinerario.id, poi_id=n.poi_id, incluido=False, motivo=n.motivo)
        for n in no_incluidos
        if s.get(PointOfInterest, n.poi_id) is not None
    ]
    filas += [
        Recommendation(itinerary_id=itinerario.id, poi_id=a, incluido=False, alternativo=True)
        for a in alternativos
    ]
    s.add_all(filas)
    s.commit()
    return itinerario


def _paradas(paradas: list[tipos.Parada], indice: dict[str, PointOfInterest]) -> list[Parada]:
    return [
        Parada(
            orden=p.orden,
            poi=catalogo.resumen(indice[p.poi_id]),
            llegada_min=p.llegada_min,
            estancia_min=p.estancia_min,
            traslado_min=p.traslado_min,
            motivo=p.motivo,
            advertencias=list(p.advertencias),
        )
        for p in paradas
    ]


@router.post("/recommend", response_model=RespuestaRecomendar)
def recomendar(
    cuerpo: SolicitudRecomendar, s: Sesion, usuario: UsuarioOpcional
) -> RespuestaRecomendar:
    pois = s.scalars(select(PointOfInterest).order_by(PointOfInterest.poi_id)).all()
    indice = {p.poi_id: p for p in pois}
    solicitud = tipos.SolicitudRuta(
        horas_disponibles=cuerpo.horas_disponibles,
        punto_partida=(
            (cuerpo.punto_partida.lat, cuerpo.punto_partida.lon) if cuerpo.punto_partida else None
        ),
        intereses=list(cuerpo.intereses),
        presupuesto=cuerpo.presupuesto,
        restricciones=_restricciones(cuerpo.restricciones),
        incluir_alternativos=cuerpo.incluir_alternativos,
    )
    respuesta = recommender.recomendar(solicitud, [catalogo.candidato(p) for p in pois])
    itinerario = _guardar(
        s,
        usuario,
        "recomendado",
        cuerpo.model_dump(mode="json", exclude={"punto_partida"}),
        respuesta.explicacion,
        respuesta.motor,
        [(1, respuesta.paradas)],
        respuesta.no_incluidos,
        respuesta.alternativos,
    )
    return RespuestaRecomendar(
        itinerario_id=itinerario.id,
        paradas=_paradas(respuesta.paradas, indice),
        no_incluidos=[NoIncluido(poi_id=n.poi_id, motivo=n.motivo) for n in respuesta.no_incluidos],
        alternativos=[catalogo.resumen(indice[a]) for a in respuesta.alternativos],
        explicacion=respuesta.explicacion,
        datos_desconocidos=list(respuesta.datos_desconocidos),
    )


@router.post("/from-saved", response_model=RespuestaDesdeGuardados)
def desde_guardados(
    cuerpo: SolicitudDesdeGuardados, s: Sesion, usuario: UsuarioOpcional
) -> RespuestaDesdeGuardados:
    pedidos = list(dict.fromkeys(cuerpo.poi_ids))
    elegidos = catalogo.obtener(s, pedidos)
    faltantes = [
        tipos.NoIncluido(poi_id=i, motivo="No existe en el catálogo")
        for i in pedidos
        if i not in elegidos
    ]
    catalogo_completo = s.scalars(select(PointOfInterest).order_by(PointOfInterest.poi_id)).all()
    indice = {p.poi_id: p for p in catalogo_completo}
    respuesta = recommender.recomendar_multidia(
        tipos.SolicitudMultidia(
            dias=cuerpo.dias,
            horas_por_dia=cuerpo.horas_por_dia,
            restricciones=_restricciones(cuerpo.restricciones),
        ),
        [catalogo.candidato(elegidos[i]) for i in pedidos if i in elegidos],
        [catalogo.candidato(p) for p in catalogo_completo if p.poi_id not in elegidos],
    )
    no_incluidos = list(respuesta.no_incluidos) + faltantes
    itinerario = _guardar(
        s,
        usuario,
        "desde_guardados",
        cuerpo.model_dump(mode="json"),
        respuesta.explicacion,
        respuesta.motor,
        [(d.dia, d.paradas) for d in respuesta.dias],
        no_incluidos,
        respuesta.alternativos,
    )
    return RespuestaDesdeGuardados(
        itinerario_id=itinerario.id,
        dias=[Dia(dia=d.dia, paradas=_paradas(d.paradas, indice)) for d in respuesta.dias],
        no_incluidos=[NoIncluido(poi_id=n.poi_id, motivo=n.motivo) for n in no_incluidos],
        alternativos=[catalogo.resumen(indice[a]) for a in respuesta.alternativos],
    )
