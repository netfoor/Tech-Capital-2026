from fastapi.testclient import TestClient

from app.main import app


def test_health_responde_aunque_no_haya_base():
    respuesta = TestClient(app).get("/health")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "ok"
    assert cuerpo["base_de_datos"] in {"disponible", "no disponible"}
