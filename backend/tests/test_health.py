from fastapi.testclient import TestClient

from app.main import app


def test_health_responde_aunque_no_haya_base():
    respuesta = TestClient(app).get("/health")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "ok"
    assert cuerpo["base_de_datos"] in {"disponible", "no disponible"}


def test_la_url_del_proveedor_usa_psycopg():
    from app.config import Ajustes

    for url in ("postgres://u:p@h/db?sslmode=require", "postgresql://u:p@h/db"):
        assert Ajustes(database_url=url).database_url.startswith("postgresql+psycopg://")
    local = "postgresql+psycopg://u:p@localhost:5433/db"
    assert Ajustes(database_url=local).database_url == local
