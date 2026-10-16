"""Invariantes de §13.2 como restricciones de base de datos."""

from datetime import UTC, date, datetime

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app.models import (
    Base,
    ConfirmedVisit,
    POIAccessibilityAttribute,
    Review,
    ReviewDimension,
    SavedPlace,
)
from tests.utiles import crear_usuario


def _falla(sesion, objeto):
    sesion.add(objeto)
    with pytest.raises(IntegrityError):
        sesion.flush()
    sesion.rollback()


def test_cada_tabla_vive_en_su_esquema():
    esquemas = {t.schema for t in Base.metadata.tables.values()}
    assert esquemas == {"core", "private", "analytics", "audit"}
    privadas = {t.name for t in Base.metadata.tables.values() if t.schema == "private"}
    assert {"user_account", "location_sample", "saved_place", "review"} <= privadas


def test_nada_fuera_de_private_apunta_a_location_sample():
    for tabla in Base.metadata.tables.values():
        if tabla.schema == "private":
            continue
        for fk in tabla.foreign_keys:
            assert fk.column.table.name != "location_sample"


def test_core_no_apunta_a_private():
    for tabla in Base.metadata.tables.values():
        if tabla.schema == "core":
            assert all(fk.column.table.schema == "core" for fk in tabla.foreign_keys)


def test_tablas_con_datos_sinteticos_tienen_is_synthetic():
    sin_columna = {
        "data_source",
        "data_lineage",
        "metric_definition",
        "consent_grant",
        "privacy_preference",
        "user_accessibility_preference",
        "review_dimension",
        "place_list_item",
        "itinerary_day",
        "itinerary_stop",
        "recommendation",
        "recommendation_feedback",
        "audit_event",
    }
    for tabla in Base.metadata.tables.values():
        if tabla.name not in sin_columna:
            assert "is_synthetic" in tabla.c, tabla.name
            assert tabla.c.is_synthetic.nullable is False


def test_atributo_exige_estado_valido_y_confianza(sesion, catalogo):
    base = {
        "poi_id": "demo-cholula-cafe",
        "atributo": "elevador",
        "valor": "si",
        "origen": "osm",
        "fecha": date(2026, 10, 1),
        "confianza": 0.5,
        "estado": "verificado",
    }
    _falla(sesion, POIAccessibilityAttribute(**{**base, "estado": "accesible"}))
    _falla(sesion, POIAccessibilityAttribute(**{**base, "confianza": 1.5}))
    _falla(sesion, POIAccessibilityAttribute(**{**base, "atributo": "wifi"}))
    _falla(sesion, POIAccessibilityAttribute(**{**base, "fecha": None}))


def test_visita_con_gps_exige_precision(sesion, catalogo):
    usuario, _ = crear_usuario(sesion, "v@ejemplo.mx")
    visita = {
        "user_id": usuario.id,
        "poi_id": "demo-cholula-museo",
        "fecha": datetime.now(UTC),
        "confianza": 0.8,
        "confirmada": True,
    }
    _falla(sesion, ConfirmedVisit(**visita, fuente_evidencia="gps_confirmado", precision_m=None))
    sesion.add(ConfirmedVisit(**visita, fuente_evidencia="check_in", precision_m=None))
    sesion.commit()


def test_resena_puntaje_entre_1_y_5_y_guardado_con_destino(sesion, catalogo):
    usuario, _ = crear_usuario(sesion, "r@ejemplo.mx")
    resena = Review(user_id=usuario.id, poi_id="demo-cholula-museo")
    resena.dimensiones = [ReviewDimension(dimension="global", puntaje=6)]
    _falla(sesion, resena)
    _falla(sesion, SavedPlace(user_id=usuario.id))


def test_migracion_creo_indices_espaciales(sesion):
    indices = {i["name"] for i in inspect(sesion.bind).get_indexes("point_of_interest", "core")}
    assert "idx_point_of_interest_geom" in indices
