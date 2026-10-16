"""«Guardar en mi mapa» y listas propias. Todo es privado y solo lo ve su dueño."""

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import func, select

from app.api.deps import Sesion
from app.models import PlaceList, PlaceListItem, PointOfInterest, SavedPlace, User
from app.schemas.cuenta import (
    ElementoLista,
    ElementoListaResumen,
    Lista,
    Listas,
    LugarGuardado,
    PaginaGuardados,
    SolicitudElemento,
    SolicitudGuardar,
    SolicitudLista,
)
from app.services import catalogo
from app.services.seguridad import Usuario

router = APIRouter(tags=["guardados"])


def _lugar(g: SavedPlace, poi: PointOfInterest | None) -> LugarGuardado:
    return LugarGuardado(
        id=g.id,
        poi_id=g.poi_id,
        nombre_propio=g.nombre_propio,
        nota=g.nota,
        url_origen=g.url_origen,
        plataforma_origen=g.plataforma_origen,
        creado_en=g.creado_en,
        poi=catalogo.resumen(poi) if poi else None,
    )


def _lista(lista: PlaceList) -> Lista:
    return Lista(
        id=lista.id,
        nombre=lista.nombre,
        etiquetas=list(lista.etiquetas),
        items=[
            ElementoListaResumen(id=i.id, saved_place_id=i.saved_place_id, poi_id=i.guardado.poi_id)
            for i in lista.items
        ],
    )


def guardar_poi(s: Sesion, usuario: User, cuerpo: SolicitudGuardar) -> tuple[SavedPlace, bool]:
    """Devuelve (guardado, nuevo)."""
    if cuerpo.poi_id is not None:
        if s.get(PointOfInterest, cuerpo.poi_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Lugar no encontrado")
        existente = s.scalar(
            select(SavedPlace).where(
                SavedPlace.user_id == usuario.id, SavedPlace.poi_id == cuerpo.poi_id
            )
        )
        if existente is not None:
            return existente, False
    elif not cuerpo.nombre_propio:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Hace falta poi_id o nombre_propio"
        )
    guardado = SavedPlace(user_id=usuario.id, **cuerpo.model_dump())
    s.add(guardado)
    s.flush()
    return guardado, True


@router.post("/saved-places", response_model=LugarGuardado, status_code=status.HTTP_201_CREATED)
def guardar(
    cuerpo: SolicitudGuardar, s: Sesion, usuario: Usuario, respuesta: Response
) -> LugarGuardado:
    guardado, nuevo = guardar_poi(s, usuario, cuerpo)
    s.commit()
    if not nuevo:
        respuesta.status_code = status.HTTP_200_OK
    poi = s.get(PointOfInterest, guardado.poi_id) if guardado.poi_id else None
    return _lugar(guardado, poi)


@router.get("/saved-places", response_model=PaginaGuardados)
def mis_guardados(s: Sesion, usuario: Usuario) -> PaginaGuardados:
    guardados = s.scalars(
        select(SavedPlace)
        .where(SavedPlace.user_id == usuario.id)
        .order_by(SavedPlace.creado_en.desc(), SavedPlace.id.desc())
    ).all()
    pois = catalogo.obtener(s, [g.poi_id for g in guardados if g.poi_id])
    return PaginaGuardados(
        items=[_lugar(g, pois.get(g.poi_id)) for g in guardados], total=len(guardados)
    )


@router.delete("/saved-places/{guardado_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_guardado(guardado_id: int, s: Sesion, usuario: Usuario) -> Response:
    guardado = s.get(SavedPlace, guardado_id)
    if guardado is None or guardado.user_id != usuario.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Guardado no encontrado")
    s.delete(guardado)
    s.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/lists", response_model=Lista, status_code=status.HTTP_201_CREATED)
def crear_lista(cuerpo: SolicitudLista, s: Sesion, usuario: Usuario) -> Lista:
    lista = PlaceList(user_id=usuario.id, nombre=cuerpo.nombre, etiquetas=cuerpo.etiquetas)
    s.add(lista)
    s.commit()
    return _lista(lista)


@router.get("/lists", response_model=Listas)
def mis_listas(s: Sesion, usuario: Usuario) -> Listas:
    listas = s.scalars(
        select(PlaceList).where(PlaceList.user_id == usuario.id).order_by(PlaceList.id)
    ).all()
    return Listas(items=[_lista(lista) for lista in listas])


@router.post(
    "/lists/{lista_id}/items", response_model=ElementoLista, status_code=status.HTTP_201_CREATED
)
def agregar_a_lista(
    lista_id: int, cuerpo: SolicitudElemento, s: Sesion, usuario: Usuario, respuesta: Response
) -> ElementoLista:
    lista = s.get(PlaceList, lista_id)
    if lista is None or lista.user_id != usuario.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lista no encontrada")
    if cuerpo.saved_place_id is not None:
        guardado = s.get(SavedPlace, cuerpo.saved_place_id)
        if guardado is None or guardado.user_id != usuario.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Guardado no encontrado")
    elif cuerpo.poi_id is not None:
        guardado, _ = guardar_poi(s, usuario, SolicitudGuardar(poi_id=cuerpo.poi_id))
    else:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Hace falta saved_place_id o poi_id"
        )
    elemento = s.scalar(
        select(PlaceListItem).where(
            PlaceListItem.list_id == lista.id, PlaceListItem.saved_place_id == guardado.id
        )
    )
    if elemento is None:
        orden = s.scalar(
            select(func.coalesce(func.max(PlaceListItem.orden), 0)).where(
                PlaceListItem.list_id == lista.id
            )
        )
        elemento = PlaceListItem(list_id=lista.id, saved_place_id=guardado.id, orden=orden + 1)
        s.add(elemento)
    else:
        respuesta.status_code = status.HTTP_200_OK
    s.commit()
    return ElementoLista(
        id=elemento.id, list_id=lista.id, saved_place_id=guardado.id, poi_id=guardado.poi_id
    )
