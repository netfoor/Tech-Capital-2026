import json
import logging
from datetime import UTC, datetime

from sqlalchemy import event, select, text

from app.api import b2b, sesiones, visitas
from app.db import motor
from app.models import (
    ConsentGrant,
    LocationSample,
    ModerationCase,
    TripSession,
    User,
)
from app.privacy.registros import ocultar_coordenadas

LAT, LON = 19.06331234, -98.30361234


def _datos_privados(cliente, sesion, cabecera, usuario):
    """Llena private con datos reconocibles de una persona."""
    cliente.post(
        "/saved-places",
        json={"poi_id": "demo-cholula-museo", "nota": "NOTA-PRIVADA-123"},
        headers=cabecera,
    )
    cliente.post("/lists", json={"nombre": "LISTA-PRIVADA"}, headers=cabecera)
    cliente.post(
        "/reviews",
        json={
            "poi_id": "demo-cholula-museo",
            "dimensiones": {"global": 2},
            "texto": "TEXTO-RESENA",
        },
        headers=cabecera,
    )
    cliente.post(
        "/reports/barrier",
        json={"poi_id": "demo-cholula-museo", "tipo": "escalones", "descripcion": "DESC-REPORTE"},
        headers=cabecera,
    )
    cliente.post(
        "/consents",
        json={"finalidad": "ubicacion_sesion", "otorgado": True, "version": "2026-10"},
        headers=cabecera,
    )
    viaje = TripSession(user_id=usuario.id, version_consentimiento="2026-10")
    sesion.add(viaje)
    sesion.flush()
    sesion.add(
        LocationSample(
            session_id=viaje.id,
            ts=datetime.now(UTC),
            geom=f"SRID=4326;POINT({LON} {LAT})",
            precision_m=12.0,
            version_consentimiento="2026-10",
        )
    )
    sesion.commit()


def test_consentimiento_nuevo_revoca_el_anterior(cliente, ana, sesion):
    _, cabecera = ana
    cuerpo = {"finalidad": "ubicacion_sesion", "otorgado": True, "version": "2026-10"}
    primero = cliente.post("/consents", json=cuerpo, headers=cabecera)
    assert primero.status_code == 201
    assert set(primero.json()) == {"id", "finalidad", "otorgado", "version", "fecha"}
    cliente.post("/consents", json={**cuerpo, "otorgado": False}, headers=cabecera)
    vigentes = sesion.scalars(select(ConsentGrant).where(ConsentGrant.revocado_en.is_(None))).all()
    assert len(vigentes) == 1 and vigentes[0].otorgado is False
    assert cliente.post("/consents", json=cuerpo).status_code == 401
    malo = {**cuerpo, "finalidad": "vender_datos"}
    assert cliente.post("/consents", json=malo, headers=cabecera).status_code == 422


def test_exportar_trae_todos_mis_datos(cliente, catalogo, ana, beto, sesion):
    usuario, cabecera = ana
    _datos_privados(cliente, sesion, cabecera, usuario)
    _, de_beto = beto
    cliente.post(
        "/saved-places", json={"poi_id": "demo-cholula-zocalo", "nota": "DE-BETO"}, headers=de_beto
    )
    r = cliente.get("/me/export", headers=cabecera)
    assert r.status_code == 200
    datos = r.json()
    assert datos["usuario"]["correo"] == "ana@ejemplo.mx"
    for llave in (
        "consentimientos",
        "preferencias_privacidad",
        "preferencias_accesibilidad",
        "guardados",
        "listas",
        "resenas",
        "reportes",
        "itinerarios",
        "visitas",
        "checkins",
        "sesiones",
    ):
        assert llave in datos
    texto = json.dumps(datos)
    for marca in ("NOTA-PRIVADA-123", "LISTA-PRIVADA", "TEXTO-RESENA", "DESC-REPORTE"):
        assert marca in texto
    assert "DE-BETO" not in texto
    assert "hash_contrasena" not in texto
    assert datos["muestras_ubicacion"][0]["lat"] == LAT
    assert cliente.get("/me/export").status_code == 401


def test_borrar_cuenta_no_deja_nada_en_private(cliente, catalogo, ana, beto, sesion):
    usuario, cabecera = ana
    uid = usuario.id
    _datos_privados(cliente, sesion, cabecera, usuario)
    _, de_beto = beto
    cliente.post("/saved-places", json={"poi_id": "demo-cholula-zocalo"}, headers=de_beto)

    assert cliente.delete("/me", headers=cabecera).status_code == 204

    with motor.connect() as conexion:
        tablas = conexion.scalars(
            text(
                "SELECT c.table_name FROM information_schema.columns c "
                "WHERE c.table_schema = 'private' AND c.column_name = 'user_id'"
            )
        ).all()
        assert tablas
        for tabla in tablas:
            restantes = conexion.scalar(
                text(f'SELECT count(*) FROM private."{tabla}" WHERE user_id = :u'),
                {"u": uid},
            )
            assert restantes == 0, tabla
        assert conexion.scalar(text("SELECT count(*) FROM private.location_sample")) == 0
    sesion.expire_all()
    assert sesion.get(User, uid) is None
    # Los datos de Beto siguen; el caso de moderación queda sin vínculo a la persona
    assert cliente.get("/saved-places", headers=de_beto).json()["total"] == 1
    caso = sesion.scalars(select(ModerationCase)).one()
    assert caso.community_report_id is None
    # El token de la cuenta borrada ya no sirve
    assert cliente.get("/me", headers=cabecera).status_code == 401


def test_respuestas_publicas_no_tocan_private(cliente, catalogo, ana, sesion):
    usuario, cabecera = ana
    _datos_privados(cliente, sesion, cabecera, usuario)
    sentencias: list[str] = []

    def capturar(conexion, cursor, sentencia, parametros, contexto, ejecutar_muchos):
        sentencias.append(sentencia)

    event.listen(motor, "before_cursor_execute", capturar)
    try:
        respuestas = [
            cliente.get("/pois"),
            cliente.get("/pois", params={"q": "museo", "sin_escalones": True}),
            cliente.get("/pois/demo-cholula-museo"),
            cliente.get("/destinos"),
        ]
    finally:
        event.remove(motor, "before_cursor_execute", capturar)

    assert sentencias
    assert not [s for s in sentencias if "private." in s]
    texto = " ".join(r.text for r in respuestas)
    prohibidos = [
        "ana@ejemplo.mx",
        str(usuario.id),
        "NOTA-PRIVADA-123",
        "TEXTO-RESENA",
        "DESC-REPORTE",
        "user_id",
        "correo",
        str(LAT),
        str(LON),
    ]
    for dato in prohibidos:
        assert dato not in texto, dato


def test_registros_sin_coordenadas(cliente, catalogo, caplog):
    with caplog.at_level(logging.INFO, logger="puebla_viva"):
        r = cliente.post(
            "/itineraries/recommend",
            json={"horas_disponibles": 2, "punto_partida": {"lat": LAT, "lon": LON}},
        )
        cliente.get("/pois", params={"q": f"{LAT},{LON}"})
        logging.getLogger("puebla_viva.api").info("prueba %s %s", LAT, LON)
    assert r.status_code == 200
    registro = caplog.text
    assert "/itineraries/recommend" in registro
    assert str(LAT) not in registro and str(LON) not in registro
    assert "19.0633" not in registro
    assert ocultar_coordenadas("en 19.063312,-98.303612") == (
        "en [coordenada oculta],[coordenada oculta]"
    )


def test_routers_reservados_registrados():
    assert sesiones.router.prefix == "/sessions"
    assert visitas.router_visitas.prefix == "/visits"
    assert visitas.router_checkins.prefix == "/checkins"
    assert b2b.router.prefix == "/b2b"


def test_fixture_sintetico_se_marca_en_la_api(cliente, catalogo):
    items = cliente.get("/pois").json()["items"]
    assert items and all(p["is_synthetic"] for p in items)
