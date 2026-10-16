"""Catálogo público: lugares y destinos. No requiere cuenta ni toca el esquema private."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import Sesion
from app.models import Destination, PointOfInterest
from app.schemas.catalogo import (
    DestinoResumen,
    ListaDestinos,
    PaginaPOI,
    POIDetalle,
    RangoCosto,
)
from app.services import catalogo

router = APIRouter(tags=["catálogo"])


@router.get("/pois", response_model=PaginaPOI)
def listar_pois(
    s: Sesion,
    q: Annotated[str | None, Query(max_length=200)] = None,
    categoria: str | None = None,
    destino_id: str | None = None,
    corredor_id: str | None = None,
    costo_max: RangoCosto | None = None,
    sin_escalones: bool = False,
    banio_accesible: bool = False,
    solo_verificados: bool = False,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PaginaPOI:
    consulta = catalogo.consulta_pois(
        q=q,
        categoria=categoria,
        destino_id=destino_id,
        corredor_id=corredor_id,
        costo_max=costo_max,
        sin_escalones=sin_escalones,
        banio_accesible=banio_accesible,
        solo_verificados=solo_verificados,
    )
    pois, total = catalogo.buscar(s, consulta, limit, offset)
    return PaginaPOI(items=[catalogo.resumen(p) for p in pois], total=total)


@router.get("/pois/{poi_id}", response_model=POIDetalle)
def ficha_poi(poi_id: str, s: Sesion) -> POIDetalle:
    poi = s.get(PointOfInterest, poi_id)
    if poi is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lugar no encontrado")
    return catalogo.detalle(s, poi)


@router.get("/destinos", response_model=ListaDestinos)
def listar_destinos(s: Sesion) -> ListaDestinos:
    destinos = s.scalars(select(Destination).order_by(Destination.nombre)).all()
    return ListaDestinos(
        items=[
            DestinoResumen(
                destino_id=d.destino_id,
                nombre=d.nombre,
                pueblo_magico=d.pueblo_magico,
                lat=d.lat,
                lon=d.lon,
                zona=d.zona,
            )
            for d in destinos
        ]
    )
