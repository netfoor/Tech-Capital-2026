"""Consulta y serialización del catálogo. Solo lee los esquemas core y audit, nunca private."""

from collections.abc import Iterable

from sqlalchemy import Select, case, exists, func, or_, select
from sqlalchemy.orm import Session

from app.models import DataSource, ModerationCase, POIAccessibilityAttribute, PointOfInterest
from app.models.core import ATRIBUTOS_ACCESIBILIDAD, RANGOS_COSTO
from app.recommender import tipos
from app.schemas.catalogo import (
    AtributoAcceso,
    BarreraReportada,
    Fuente,
    POIDetalle,
    POIResumen,
)

ESTADO_BARRERA = {"abierto": "en_moderacion", "aceptado": "aceptado"}

# Orden por omisión de la lista: primero lo que más sirve para decidir una visita.
PRIORIDAD_CATEGORIA = (
    "museo",
    "zona_arqueologica",
    "sitio_historico",
    "templo",
    "centro_cultural",
    "mirador",
    "mercado",
    "artesanias",
    "parque",
    "cafe",
    "restaurante",
    "banio",
    "alojamiento",
    "otro",
)


def accesibilidad(poi: PointOfInterest) -> dict[str, AtributoAcceso]:
    """Los nueve atributos; sin dato = «sin_verificar» (constitución XIII)."""
    registrados = {a.atributo: a for a in poi.atributos}
    salida = {}
    for atributo in ATRIBUTOS_ACCESIBILIDAD:
        a = registrados.get(atributo)
        salida[atributo] = (
            AtributoAcceso(
                valor=a.valor,
                estado=a.estado,
                origen=a.origen,
                confianza=a.confianza,
                fecha=a.fecha,
            )
            if a
            else AtributoAcceso()
        )
    return salida


def cobertura(acc: dict[str, AtributoAcceso]) -> str:
    if all(acc[a].estado == "verificado" for a in tipos.ATRIBUTOS_CLAVE):
        return "verificada"
    if any(v.estado == "verificado" for v in acc.values()):
        return "parcial"
    return "sin_verificar"


def resumen(poi: PointOfInterest) -> POIResumen:
    acc = accesibilidad(poi)
    return POIResumen(
        poi_id=poi.poi_id,
        nombre=poi.nombre,
        categoria=poi.categoria,
        destino_id=poi.destino_id,
        corredor_id=poi.corredor_id,
        lat=poi.lat,
        lon=poi.lon,
        costo_rango=poi.costo_rango,
        accesibilidad=acc,
        cobertura_accesibilidad=cobertura(acc),
        is_synthetic=poi.is_synthetic,
    )


def candidato(poi: PointOfInterest) -> tipos.POICandidato:
    """ORM → tipo del recomendador."""
    return tipos.POICandidato(
        poi_id=poi.poi_id,
        nombre=poi.nombre,
        categoria=poi.categoria,
        destino_id=poi.destino_id,
        corredor_id=poi.corredor_id,
        lat=poi.lat,
        lon=poi.lon,
        costo_rango=poi.costo_rango,
        accesibilidad={
            k: tipos.AtributoAcceso(v.valor, v.estado, v.origen, v.confianza, v.fecha)
            for k, v in accesibilidad(poi).items()
        },
        horario_osm=poi.horario_osm,
        is_synthetic=poi.is_synthetic,
    )


def _escapar(texto: str) -> str:
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _tiene(atributo: str, solo_verificados: bool, valor: str | None = "si"):
    A = POIAccessibilityAttribute
    condiciones = [A.poi_id == PointOfInterest.poi_id, A.atributo == atributo]
    if valor is not None:
        condiciones.append(A.valor == valor)
    if solo_verificados:
        condiciones.append(A.estado == "verificado")
    return exists().where(*condiciones)


def consulta_pois(
    q: str | None = None,
    categoria: str | None = None,
    destino_id: str | None = None,
    corredor_id: str | None = None,
    costo_max: str | None = None,
    sin_escalones: bool = False,
    banio_accesible: bool = False,
    solo_verificados: bool = False,
) -> Select:
    P = PointOfInterest
    consulta = select(P)
    if q:
        patron = func.unaccent(f"%{_escapar(q.strip())}%")
        consulta = consulta.where(
            or_(
                func.unaccent(P.nombre).ilike(patron, escape="\\"),
                func.unaccent(func.coalesce(P.descripcion, "")).ilike(patron, escape="\\"),
            )
        )
    if categoria:
        consulta = consulta.where(P.categoria == categoria)
    if destino_id:
        consulta = consulta.where(P.destino_id == destino_id)
    if corredor_id:
        consulta = consulta.where(P.corredor_id == corredor_id)
    if costo_max:
        tope = RANGOS_COSTO.index(costo_max)
        consulta = consulta.where(P.costo_rango.in_(RANGOS_COSTO[: tope + 1]))
    if sin_escalones:
        consulta = consulta.where(_tiene("acceso_sin_escalones", solo_verificados))
    if banio_accesible:
        consulta = consulta.where(_tiene("banio_accesible", solo_verificados))
    if solo_verificados and not (sin_escalones or banio_accesible):
        A = POIAccessibilityAttribute
        consulta = consulta.where(exists().where(A.poi_id == P.poi_id, A.estado == "verificado"))
    return consulta


def buscar(
    s: Session, consulta: Select, limit: int, offset: int
) -> tuple[list[PointOfInterest], int]:
    total = s.scalar(select(func.count()).select_from(consulta.order_by(None).subquery()))
    P = PointOfInterest
    con_dato = exists().where(POIAccessibilityAttribute.poi_id == P.poi_id)
    prioridad = case(
        {c: i for i, c in enumerate(PRIORIDAD_CATEGORIA)},
        value=P.categoria,
        else_=len(PRIORIDAD_CATEGORIA),
    )
    # Los nombres que empiezan con un número suelen ser registros incompletos.
    nombre_numerico = P.nombre.op("~")("^[0-9]")
    pagina = s.scalars(
        consulta.order_by(con_dato.desc(), prioridad, nombre_numerico, P.nombre, P.poi_id)
        .limit(limit)
        .offset(offset)
    ).all()
    return list(pagina), int(total or 0)


def obtener(s: Session, poi_ids: Iterable[str]) -> dict[str, PointOfInterest]:
    ids = list(dict.fromkeys(poi_ids))
    if not ids:
        return {}
    filas = s.scalars(select(PointOfInterest).where(PointOfInterest.poi_id.in_(ids))).all()
    return {p.poi_id: p for p in filas}


def detalle(s: Session, poi: PointOfInterest) -> POIDetalle:
    registradas = {
        f.fuente_id: f
        for f in s.scalars(select(DataSource).where(DataSource.fuente_id.in_(poi.fuentes or [])))
    }
    fuentes = [
        Fuente(
            id=i,
            nombre=registradas[i].nombre if i in registradas else i,
            url=registradas[i].url if i in registradas else None,
        )
        for i in poi.fuentes or []
    ]
    casos = s.scalars(
        select(ModerationCase)
        .where(ModerationCase.poi_id == poi.poi_id, ModerationCase.estado.in_(ESTADO_BARRERA))
        .order_by(ModerationCase.creado_en.desc(), ModerationCase.id.desc())
    ).all()
    barreras = [
        BarreraReportada(tipo=c.tipo, estado=ESTADO_BARRERA[c.estado], fecha=c.creado_en.date())
        for c in casos
    ]
    return POIDetalle(
        **resumen(poi).model_dump(),
        descripcion=poi.descripcion,
        direccion=poi.direccion,
        horario_osm=poi.horario_osm,
        fuentes=fuentes,
        barreras_reportadas=barreras,
    )
