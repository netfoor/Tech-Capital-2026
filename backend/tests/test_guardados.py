def test_guardar_y_listar(cliente, catalogo, ana):
    _, cabecera = ana
    r = cliente.post(
        "/saved-places",
        json={"poi_id": "demo-cholula-museo", "nota": "ir temprano"},
        headers=cabecera,
    )
    assert r.status_code == 201
    guardado = r.json()
    assert guardado["poi"]["poi_id"] == "demo-cholula-museo"
    assert guardado["nota"] == "ir temprano"
    # Guardar otra vez el mismo POI devuelve el existente
    otra = cliente.post("/saved-places", json={"poi_id": "demo-cholula-museo"}, headers=cabecera)
    assert otra.status_code == 200 and otra.json()["id"] == guardado["id"]
    propio = cliente.post(
        "/saved-places",
        json={
            "nombre_propio": "Café que vi en redes",
            "url_origen": "https://ejemplo.mx/p/1",
            "plataforma_origen": "web",
        },
        headers=cabecera,
    )
    assert propio.status_code == 201 and propio.json()["poi"] is None
    lista = cliente.get("/saved-places", headers=cabecera).json()
    assert lista["total"] == 2


def test_guardar_requiere_cuenta_y_datos(cliente, catalogo, ana):
    _, cabecera = ana
    assert cliente.post("/saved-places", json={"poi_id": "demo-cholula-museo"}).status_code == 401
    assert cliente.get("/saved-places").status_code == 401
    assert cliente.post("/saved-places", json={}, headers=cabecera).status_code == 422
    assert (
        cliente.post("/saved-places", json={"poi_id": "no-existe"}, headers=cabecera).status_code
        == 404
    )


def test_listas_y_elementos(cliente, catalogo, ana):
    _, cabecera = ana
    r = cliente.post(
        "/lists", json={"nombre": "Fin de semana", "etiquetas": ["familia"]}, headers=cabecera
    )
    assert r.status_code == 201
    lista = r.json()
    assert lista["items"] == [] and lista["etiquetas"] == ["familia"]
    por_poi = cliente.post(
        f"/lists/{lista['id']}/items", json={"poi_id": "demo-atlixco-zocalo"}, headers=cabecera
    )
    assert por_poi.status_code == 201
    elemento = por_poi.json()
    assert elemento["poi_id"] == "demo-atlixco-zocalo" and elemento["list_id"] == lista["id"]
    # Agregar por poi_id guarda el lugar
    assert cliente.get("/saved-places", headers=cabecera).json()["total"] == 1
    repetido = cliente.post(
        f"/lists/{lista['id']}/items",
        json={"saved_place_id": elemento["saved_place_id"]},
        headers=cabecera,
    )
    assert repetido.status_code == 200 and repetido.json()["id"] == elemento["id"]
    listas = cliente.get("/lists", headers=cabecera).json()["items"]
    assert len(listas) == 1 and listas[0]["items"][0]["poi_id"] == "demo-atlixco-zocalo"
    assert cliente.post(f"/lists/{lista['id']}/items", json={}, headers=cabecera).status_code == 422


def test_borrar_guardado(cliente, catalogo, ana):
    _, cabecera = ana
    guardado = cliente.post(
        "/saved-places", json={"poi_id": "demo-cholula-museo"}, headers=cabecera
    ).json()
    assert cliente.delete(f"/saved-places/{guardado['id']}", headers=cabecera).status_code == 204
    assert cliente.get("/saved-places", headers=cabecera).json()["total"] == 0


def test_autorizacion_horizontal(cliente, catalogo, ana, beto):
    _, de_ana = ana
    _, de_beto = beto
    guardado = cliente.post(
        "/saved-places",
        json={"poi_id": "demo-cholula-museo", "nota": "secreto de Ana"},
        headers=de_ana,
    ).json()
    lista = cliente.post("/lists", json={"nombre": "De Ana"}, headers=de_ana).json()

    # Beto no ve los guardados ni las listas de Ana
    assert cliente.get("/saved-places", headers=de_beto).json() == {"items": [], "total": 0}
    assert cliente.get("/lists", headers=de_beto).json() == {"items": []}
    # ni puede usarlos ni borrarlos
    assert (
        cliente.post(
            f"/lists/{lista['id']}/items", json={"poi_id": "demo-cholula-zocalo"}, headers=de_beto
        ).status_code
        == 404
    )
    propia = cliente.post("/lists", json={"nombre": "De Beto"}, headers=de_beto).json()
    assert (
        cliente.post(
            f"/lists/{propia['id']}/items", json={"saved_place_id": guardado["id"]}, headers=de_beto
        ).status_code
        == 404
    )
    assert cliente.delete(f"/saved-places/{guardado['id']}", headers=de_beto).status_code == 404
    assert cliente.get("/saved-places", headers=de_ana).json()["total"] == 1
