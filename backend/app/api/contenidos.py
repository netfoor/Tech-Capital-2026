"""Reseñas por dimensiones y reportes de barrera. Requieren cuenta; son privados por defecto."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import Sesion
from app.config import ajustes
from app.models import (
    CommunityReport,
    MediaAsset,
    ModerationCase,
    PointOfInterest,
    Review,
    ReviewDimension,
)
from app.privacy import fotos
from app.schemas.cuenta import (
    RespuestaBarrera,
    RespuestaResena,
    SolicitudBarrera,
    SolicitudResena,
)
from app.services.auditoria import registrar
from app.services.moderacion import ATRIBUTO_POR_TIPO
from app.services.seguridad import Usuario

router = APIRouter(tags=["contenidos"])


def _poi_existe(s: Sesion, poi_id: str) -> None:
    if s.get(PointOfInterest, poi_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lugar no encontrado")


@router.post("/reviews", response_model=RespuestaResena, status_code=status.HTTP_201_CREATED)
def resenar(cuerpo: SolicitudResena, s: Sesion, usuario: Usuario) -> RespuestaResena:
    _poi_existe(s, cuerpo.poi_id)
    puntajes = {
        k: v for k, v in cuerpo.dimensiones.model_dump(by_alias=True).items() if v is not None
    }
    resena = Review(user_id=usuario.id, poi_id=cuerpo.poi_id, texto=cuerpo.texto)
    resena.dimensiones = [ReviewDimension(dimension=k, puntaje=v) for k, v in puntajes.items()]
    s.add(resena)
    s.flush()
    registrar(s, usuario.id, "crear", "review", resena.id, {"poi_id": cuerpo.poi_id})
    s.commit()
    return RespuestaResena(
        review_id=resena.id,
        poi_id=resena.poi_id,
        dimensiones=puntajes,
        texto=resena.texto,
        creado_en=resena.creado_en,
    )


@router.post(
    "/reports/barrier", response_model=RespuestaBarrera, status_code=status.HTTP_201_CREATED
)
def reportar_barrera(cuerpo: SolicitudBarrera, s: Sesion, usuario: Usuario) -> RespuestaBarrera:
    _poi_existe(s, cuerpo.poi_id)
    media_id = None
    if cuerpo.foto:
        try:
            limpia = fotos.limpiar(fotos.decodificar(cuerpo.foto, ajustes().foto_max_bytes))
        except fotos.FotoInvalida as error:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error
        ruta = fotos.guardar(limpia, ajustes().directorio_media)
        media = MediaAsset(
            user_id=usuario.id,
            ruta=str(ruta),
            tipo_mime=limpia.tipo_mime,
            bytes=len(limpia.contenido),
            sin_exif=True,
        )
        s.add(media)
        s.flush()
        media_id = media.id
    reporte = CommunityReport(
        user_id=usuario.id,
        poi_id=cuerpo.poi_id,
        tipo=cuerpo.tipo,
        descripcion=cuerpo.descripcion,
        media_asset_id=media_id,
    )
    s.add(reporte)
    s.flush()
    caso = ModerationCase(
        community_report_id=reporte.id,
        poi_id=cuerpo.poi_id,
        tipo=cuerpo.tipo,
        atributo=ATRIBUTO_POR_TIPO.get(cuerpo.tipo, (None, None))[0],
    )
    s.add(caso)
    s.flush()
    registrar(
        s,
        usuario.id,
        "reportar_barrera",
        "community_report",
        reporte.id,
        {"poi_id": cuerpo.poi_id, "tipo": cuerpo.tipo, "moderation_case_id": caso.id},
    )
    s.commit()
    return RespuestaBarrera(report_id=reporte.id, moderation_case_id=caso.id)
