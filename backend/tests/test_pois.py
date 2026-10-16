from app.models.core import ATRIBUTOS_ACCESIBILIDAD


def ids(respuesta) -> list[str]:
    return [p["poi_id"] for p in respuesta.json()["items"]]


def test_lista_sin_cuenta_con_forma_del_contrato(cliente, catalogo):
    r = cliente.get("/pois")
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["total"] == 8
    poi = cuerpo["items"][0]
    assert set(poi) == {
        "poi_id",
        "nombre",
        "categoria",
        "destino_id",
        "corredor_id",
        "lat",
        "lon",
        "costo_rango",
        "accesibilidad",
        "cobertura_accesibilidad",
        "is_synthetic",
    }
    assert set(poi["accesibilidad"]) == set(ATRIBUTOS_ACCESIBILIDAD)
    assert poi["is_synthetic"] is True
    nombres = [p["nombre"] for p in cuerpo["items"]]
    assert nombres == sorted(nombres)


def test_sin_dato_es_sin_verificar_nunca_accesible(cliente, catalogo):
    r = cliente.get("/pois/demo-cholula-cafe")
    acc = r.json()["accesibilidad"]
    assert all(a["estado"] == "sin_verificar" and a["valor"] is None for a in acc.values())
    assert r.json()["cobertura_accesibilidad"] == "sin_verificar"


def test_cobertura(cliente, catalogo):
    cobertura = {
        p["poi_id"]: p["cobertura_accesibilidad"] for p in cliente.get("/pois").json()["items"]
    }
    assert cobertura["demo-cholula-zocalo"] == "verificada"
    assert cobertura["demo-cholula-museo"] == "parcial"
    assert cobertura["demo-cholula-mercado"] == "sin_verificar"


def test_filtros_de_accesibilidad(cliente, catalogo):
    sin_escalones = ids(cliente.get("/pois", params={"sin_escalones": True}))
    assert set(sin_escalones) == {
        "demo-cholula-zocalo",
        "demo-cholula-museo",
        "demo-cholula-mercado",
        "demo-atlixco-zocalo",
    }
    verificados = ids(
        cliente.get("/pois", params={"sin_escalones": True, "solo_verificados": True})
    )
    assert "demo-cholula-mercado" not in verificados and len(verificados) == 3
    banio = ids(cliente.get("/pois", params={"banio_accesible": True}))
    assert set(banio) == {"demo-cholula-zocalo", "demo-atlixco-zocalo", "demo-atlixco-restaurante"}
    banio_v = ids(cliente.get("/pois", params={"banio_accesible": True, "solo_verificados": True}))
    assert "demo-atlixco-restaurante" not in banio_v
    solo = ids(cliente.get("/pois", params={"solo_verificados": True}))
    assert "demo-cholula-cafe" not in solo and "demo-cholula-mercado" not in solo


def test_filtros_de_catalogo(cliente, catalogo):
    assert ids(cliente.get("/pois", params={"q": "MUSEO"})) == ["demo-cholula-museo"]
    assert ids(cliente.get("/pois", params={"q": "arqueologica"})) == ["demo-cholula-piramide"]
    assert ids(cliente.get("/pois", params={"q": "100%_"})) == []
    assert ids(cliente.get("/pois", params={"categoria": "plaza"})) == [
        "demo-atlixco-zocalo",
        "demo-cholula-zocalo",
    ]
    assert cliente.get("/pois", params={"destino_id": "atlixco"}).json()["total"] == 3
    assert cliente.get("/pois", params={"corredor_id": "demo-cholula-atlixco"}).json()["total"] == 8
    gratis = ids(cliente.get("/pois", params={"costo_max": "gratis"}))
    assert len(gratis) == 4
    assert "demo-atlixco-restaurante" not in ids(
        cliente.get("/pois", params={"costo_max": "medio"})
    )
    assert cliente.get("/pois", params={"costo_max": "carisimo"}).status_code == 422


def test_paginacion(cliente, catalogo):
    pagina = cliente.get("/pois", params={"limit": 3, "offset": 6}).json()
    assert pagina["total"] == 8 and len(pagina["items"]) == 2
    assert cliente.get("/pois", params={"limit": 0}).status_code == 422
    assert cliente.get("/pois", params={"limit": 501}).status_code == 422


def test_ficha_con_fuentes_y_404(cliente, catalogo):
    r = cliente.get("/pois/demo-cholula-museo")
    assert r.status_code == 200
    ficha = r.json()
    assert ficha["descripcion"] and ficha["direccion"] and ficha["horario_osm"]
    assert [f["id"] for f in ficha["fuentes"]] == ["osm-demo", "denue-demo"]
    assert ficha["barreras_reportadas"] == []
    museo = ficha["accesibilidad"]["acceso_sin_escalones"]
    assert museo == {
        "valor": "si",
        "estado": "verificado",
        "origen": "equipo_verificador",
        "confianza": 0.9,
        "fecha": "2026-10-10",
    }
    assert cliente.get("/pois/no-existe").status_code == 404


def test_destinos(cliente, catalogo):
    r = cliente.get("/destinos")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 18
    assert set(items[0]) == {"destino_id", "nombre", "pueblo_magico", "lat", "lon", "zona"}
    assert sum(d["pueblo_magico"] for d in items) == 12
