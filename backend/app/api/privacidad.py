"""Consentimientos y derechos ARCO: exportar y borrar los datos de la persona (§14)."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Response, status
from sqlalchemy import select, update

from app.api.deps import Sesion
from app.models import (
    CheckIn,
    CommunityReport,
    ConfirmedVisit,
    ConsentGrant,
    Itinerary,
    LocationSample,
    MediaAsset,
    PlaceList,
    PrivacyPreference,
    Review,
    SavedPlace,
    TripSession,
    UserAccessibilityPreference,
)
from app.schemas.cuenta import Consentimiento, SolicitudConsentimiento
from app.services.auditoria import registrar
from app.services.seguridad import Usuario

router = APIRouter(tags=["privacidad"])


@router.post("/consents", response_model=Consentimiento, status_code=status.HTTP_201_CREATED)
def consentir(cuerpo: SolicitudConsentimiento, s: Sesion, usuario: Usuario) -> Consentimiento:
    ahora = datetime.now(UTC)
    # Un consentimiento nuevo de la misma finalidad revoca el anterior.
    s.execute(
        update(ConsentGrant)
        .where(
            ConsentGrant.user_id == usuario.id,
            ConsentGrant.finalidad == cuerpo.finalidad,
            ConsentGrant.revocado_en.is_(None),
        )
        .values(revocado_en=ahora)
    )
    consentimiento = ConsentGrant(
        user_id=usuario.id,
        finalidad=cuerpo.finalidad,
        otorgado=cuerpo.otorgado,
        version=cuerpo.version,
        fecha=ahora,
    )
    s.add(consentimiento)
    s.flush()
    registrar(
        s,
        usuario.id,
        "consentimiento",
        "consent_grant",
        consentimiento.id,
        {"finalidad": cuerpo.finalidad, "otorgado": cuerpo.otorgado, "version": cuerpo.version},
    )
    s.commit()
    return Consentimiento.model_validate(consentimiento)


def _filas(s: Sesion, modelo, condicion, excluir: set[str] = frozenset()) -> list[dict[str, Any]]:
    salida = []
    for fila in s.scalars(select(modelo).where(condicion).order_by(modelo.id)):
        salida.append(
            {
                c.key: getattr(fila, c.key)
                for c in modelo.__table__.columns
                if c.key not in excluir and c.key != "geom"
            }
        )
    return salida


@router.get("/me/export")
def exportar(s: Sesion, usuario: Usuario) -> dict[str, Any]:
    uid = usuario.id
    sesiones = _filas(s, TripSession, TripSession.user_id == uid)
    ids_sesion = [x["id"] for x in sesiones]
    muestras = (
        [
            {
                "session_id": m.session_id,
                "ts": m.ts,
                "lat": m.lat,
                "lon": m.lon,
                "precision_m": m.precision_m,
            }
            for m in s.execute(
                select(
                    LocationSample.session_id,
                    LocationSample.ts,
                    LocationSample.geom.ST_Y().label("lat"),
                    LocationSample.geom.ST_X().label("lon"),
                    LocationSample.precision_m,
                )
                .where(LocationSample.session_id.in_(ids_sesion))
                .order_by(LocationSample.ts)
            )
        ]
        if ids_sesion
        else []
    )
    resenas = []
    for r in s.scalars(select(Review).where(Review.user_id == uid).order_by(Review.id)):
        resenas.append(
            {
                "id": r.id,
                "poi_id": r.poi_id,
                "texto": r.texto,
                "publica": r.publica,
                "creado_en": r.creado_en,
                "dimensiones": {d.dimension: d.puntaje for d in r.dimensiones},
            }
        )
    listas = [
        {
            "id": lista.id,
            "nombre": lista.nombre,
            "etiquetas": list(lista.etiquetas),
            "saved_place_ids": [i.saved_place_id for i in lista.items],
        }
        for lista in s.scalars(
            select(PlaceList).where(PlaceList.user_id == uid).order_by(PlaceList.id)
        )
    ]
    itinerarios = [
        {
            "id": i.id,
            "modo": i.modo,
            "solicitud": i.solicitud,
            "creado_en": i.creado_en,
            "dias": [{"dia": d.dia, "poi_ids": [p.poi_id for p in d.paradas]} for d in i.dias],
        }
        for i in s.scalars(select(Itinerary).where(Itinerary.user_id == uid).order_by(Itinerary.id))
    ]
    return {
        "generado_en": datetime.now(UTC),
        "usuario": {
            "id": usuario.id,
            "correo": usuario.correo,
            "rol": usuario.rol,
            "nombre_visible": usuario.nombre_visible,
            "creado_en": usuario.creado_en,
        },
        "consentimientos": _filas(s, ConsentGrant, ConsentGrant.user_id == uid),
        "preferencias_privacidad": _filas(s, PrivacyPreference, PrivacyPreference.user_id == uid),
        "preferencias_accesibilidad": _filas(
            s, UserAccessibilityPreference, UserAccessibilityPreference.user_id == uid
        ),
        "guardados": _filas(s, SavedPlace, SavedPlace.user_id == uid),
        "listas": listas,
        "resenas": resenas,
        "reportes": _filas(s, CommunityReport, CommunityReport.user_id == uid),
        "fotos": _filas(s, MediaAsset, MediaAsset.user_id == uid, {"ruta"}),
        "itinerarios": itinerarios,
        "visitas": _filas(s, ConfirmedVisit, ConfirmedVisit.user_id == uid),
        "checkins": _filas(s, CheckIn, CheckIn.user_id == uid),
        "sesiones": sesiones,
        "muestras_ubicacion": muestras,
    }


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def borrar_cuenta(s: Sesion, usuario: Usuario) -> Response:
    rutas = [
        Path(r) for r in s.scalars(select(MediaAsset.ruta).where(MediaAsset.user_id == usuario.id))
    ]
    uid = usuario.id
    # Las tablas de private dependen de user_account con ON DELETE CASCADE.
    s.delete(usuario)
    registrar(s, None, "borrar_cuenta", "user_account", uid)
    s.commit()
    for ruta in rutas:
        ruta.unlink(missing_ok=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
