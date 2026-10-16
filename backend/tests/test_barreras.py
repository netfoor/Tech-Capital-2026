import base64
import io

from PIL import Image
from sqlalchemy import select

from app.models import (
    AccessibilityEvidence,
    AuditEvent,
    CommunityReport,
    MediaAsset,
    ModerationCase,
)


def _foto_con_exif() -> str:
    imagen = Image.new("RGB", (8, 8), "red")
    exif = Image.Exif()
    exif[0x010F] = "Fabricante"  # Make
    exif[0x8825] = {2: (19.0, 3.0, 50.0)}  # GPSInfo
    salida = io.BytesIO()
    imagen.save(salida, format="JPEG", exif=exif)
    return base64.b64encode(salida.getvalue()).decode()


def test_resena_por_dimensiones(cliente, catalogo, ana):
    _, cabecera = ana
    r = cliente.post(
        "/reviews",
        json={
            "poi_id": "demo-cholula-museo",
            "dimensiones": {
                "accesibilidad": 4,
                "limpieza": 5,
                "servicio": 4,
                "precio_percibido": 3,
                "senalizacion": 2,
                "comodidad": 4,
                "inclusion": 4,
                "global": 4,
            },
            "texto": "Bien señalizado por dentro",
        },
        headers=cabecera,
    )
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["dimensiones"]["global"] == 4 and len(cuerpo["dimensiones"]) == 8


def test_resena_validaciones(cliente, catalogo, ana):
    _, cabecera = ana
    base = {"poi_id": "demo-cholula-museo", "dimensiones": {"global": 4}}
    assert cliente.post("/reviews", json=base).status_code == 401
    assert cliente.post("/reviews", json=base, headers=cabecera).status_code == 201
    malas = [
        {**base, "dimensiones": {"global": 6}},
        {**base, "dimensiones": {"limpieza": 3}},
        {**base, "dimensiones": {"global": 3, "sabor": 2}},
    ]
    for mala in malas:
        assert cliente.post("/reviews", json=mala, headers=cabecera).status_code == 422
    sin_poi = {**base, "poi_id": "no-existe"}
    assert cliente.post("/reviews", json=sin_poi, headers=cabecera).status_code == 404


def test_reporte_crea_caso_y_foto_sin_exif(cliente, catalogo, ana, sesion):
    _, cabecera = ana
    r = cliente.post(
        "/reports/barrier",
        json={
            "poi_id": "demo-cholula-zocalo",
            "tipo": "escalones",
            "descripcion": "Hay dos escalones en la entrada norte",
            "foto": "data:image/jpeg;base64," + _foto_con_exif(),
        },
        headers=cabecera,
    )
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["estado"] == "en_moderacion"
    caso = sesion.get(ModerationCase, cuerpo["moderation_case_id"])
    assert caso.estado == "abierto" and caso.atributo == "acceso_sin_escalones"
    reporte = sesion.get(CommunityReport, cuerpo["report_id"])
    media = sesion.get(MediaAsset, reporte.media_asset_id)
    with Image.open(media.ruta) as guardada:
        assert not guardada.getexif()
    # La ficha muestra la barrera en moderación, sin quién la reportó
    ficha = cliente.get("/pois/demo-cholula-zocalo").json()
    assert ficha["barreras_reportadas"][0]["tipo"] == "escalones"
    assert ficha["barreras_reportadas"][0]["estado"] == "en_moderacion"
    assert set(ficha["barreras_reportadas"][0]) == {"tipo", "estado", "fecha"}


def test_reporte_validaciones(cliente, catalogo, ana):
    _, cabecera = ana
    base = {"poi_id": "demo-cholula-zocalo", "tipo": "escalones"}
    assert cliente.post("/reports/barrier", json=base).status_code == 401
    otro_tipo = {**base, "tipo": "ruido"}
    assert cliente.post("/reports/barrier", json=otro_tipo, headers=cabecera).status_code == 422
    foto_mala = {**base, "foto": base64.b64encode(b"no soy imagen").decode()}
    assert cliente.post("/reports/barrier", json=foto_mala, headers=cabecera).status_code == 422
    no_base64 = {**base, "foto": "%%%"}
    assert cliente.post("/reports/barrier", json=no_base64, headers=cabecera).status_code == 422


def _reportar(cliente, cabecera, tipo="escalones", poi="demo-cholula-zocalo") -> int:
    r = cliente.post("/reports/barrier", json={"poi_id": poi, "tipo": tipo}, headers=cabecera)
    return r.json()["moderation_case_id"]


def test_autorizacion_vertical(cliente, catalogo, ana, sesion):
    _, cabecera = ana
    caso = _reportar(cliente, cabecera)
    decision = {"decision": "aceptar"}
    assert cliente.post(f"/moderation/{caso}/decision", json=decision).status_code == 401
    r = cliente.post(f"/moderation/{caso}/decision", json=decision, headers=cabecera)
    assert r.status_code == 403
    assert cliente.get("/moderation", headers=cabecera).status_code == 403
    from tests.utiles import crear_usuario

    _, viewer = crear_usuario(sesion, "viewer@ejemplo.mx", "viewer")
    r = cliente.post(f"/moderation/{caso}/decision", json=decision, headers=viewer)
    assert r.status_code == 403
    assert sesion.get(ModerationCase, caso).estado == "abierto"


def test_circuito_de_la_escena_de_valor(cliente, catalogo, ana, analista, sesion):
    """§06.8: reporte → moderación → la ficha cambia → la siguiente recomendación lo considera."""
    _, de_ana = ana
    _, de_analista = analista
    solicitud = {
        "horas_disponibles": 4,
        "punto_partida": {"lat": 19.0633, "lon": -98.3036},
        "restricciones": {"sin_escalones": True},
    }
    antes = cliente.post("/itineraries/recommend", json=solicitud).json()
    assert "demo-cholula-zocalo" in [p["poi"]["poi_id"] for p in antes["paradas"]]

    caso = _reportar(cliente, de_ana)
    abiertos = cliente.get("/moderation", headers=de_analista).json()["items"]
    assert [c["id"] for c in abiertos] == [caso]
    r = cliente.post(
        f"/moderation/{caso}/decision",
        json={"decision": "aceptar", "nota": "Confirmado con foto"},
        headers=de_analista,
    )
    assert r.status_code == 200
    assert r.json() == {
        "id": caso,
        "estado": "aceptado",
        "atributo_actualizado": {
            "atributo": "acceso_sin_escalones",
            "valor": "no",
            "estado": "reportado",
        },
    }
    ficha = cliente.get("/pois/demo-cholula-zocalo").json()
    atributo = ficha["accesibilidad"]["acceso_sin_escalones"]
    assert (atributo["valor"], atributo["estado"], atributo["origen"]) == (
        "no",
        "reportado",
        "comunidad",
    )
    assert ficha["barreras_reportadas"][0]["estado"] == "aceptado"
    assert (
        sesion.scalars(select(AccessibilityEvidence)).one().referencia == f"moderation_case:{caso}"
    )
    acciones = sesion.scalars(select(AuditEvent.accion)).all()
    assert "moderacion_aceptado" in acciones

    despues = cliente.post("/itineraries/recommend", json=solicitud).json()
    assert "demo-cholula-zocalo" not in [p["poi"]["poi_id"] for p in despues["paradas"]]
    assert "demo-cholula-zocalo" in [n["poi_id"] for n in despues["no_incluidos"]]
    assert "demo-cholula-zocalo" not in [
        p["poi_id"] for p in cliente.get("/pois", params={"sin_escalones": True}).json()["items"]
    ]

    # Una decisión no se repite
    otra = cliente.post(
        f"/moderation/{caso}/decision", json={"decision": "rechazar"}, headers=de_analista
    )
    assert otra.status_code == 409


def test_rechazo_no_cambia_la_ficha(cliente, catalogo, ana, analista, sesion):
    _, de_ana = ana
    _, de_analista = analista
    caso = _reportar(cliente, de_ana, tipo="sin_banio_accesible")
    r = cliente.post(
        f"/moderation/{caso}/decision", json={"decision": "rechazar"}, headers=de_analista
    )
    assert r.status_code == 200 and r.json()["atributo_actualizado"] is None
    ficha = cliente.get("/pois/demo-cholula-zocalo").json()
    assert ficha["accesibilidad"]["banio_accesible"]["estado"] == "verificado"
    assert ficha["barreras_reportadas"] == []
    sesion.expire_all()
    reporte_id = sesion.get(ModerationCase, caso).community_report_id
    assert sesion.get(CommunityReport, reporte_id).estado == "rechazado"
    assert (
        cliente.post(
            "/moderation/999/decision", json={"decision": "aceptar"}, headers=de_analista
        ).status_code
        == 404
    )


def test_aceptar_crea_atributo_si_no_existia(cliente, catalogo, ana, analista):
    _, de_ana = ana
    _, de_analista = analista
    caso = _reportar(cliente, de_ana, tipo="superficie", poi="demo-cholula-cafe")
    cliente.post(f"/moderation/{caso}/decision", json={"decision": "aceptar"}, headers=de_analista)
    superficie = cliente.get("/pois/demo-cholula-cafe").json()["accesibilidad"]["superficie"]
    assert superficie["valor"] == "irregular" and superficie["estado"] == "reportado"
