from sqlalchemy import select

from app.models import Itinerary, Recommendation

CHOLULA = {"lat": 19.0633, "lon": -98.3036}


def test_recomendar_sin_cuenta_con_forma_del_contrato(cliente, catalogo, sesion):
    r = cliente.post(
        "/itineraries/recommend",
        json={"horas_disponibles": 4, "punto_partida": CHOLULA, "incluir_alternativos": True},
    )
    assert r.status_code == 200
    cuerpo = r.json()
    assert set(cuerpo) == {
        "itinerario_id",
        "paradas",
        "no_incluidos",
        "alternativos",
        "explicacion",
        "datos_desconocidos",
    }
    assert cuerpo["paradas"], "debe haber al menos una parada"
    parada = cuerpo["paradas"][0]
    assert set(parada) == {
        "orden",
        "poi",
        "llegada_min",
        "estancia_min",
        "traslado_min",
        "motivo",
        "advertencias",
    }
    assert parada["orden"] == 1 and parada["poi"]["poi_id"]
    fin = max(p["llegada_min"] + p["estancia_min"] for p in cuerpo["paradas"])
    assert fin <= 4 * 60
    # Sugerencias de otro destino, claramente separadas
    assert all(a["destino_id"] != "cholula" for a in cuerpo["alternativos"])
    itinerario = sesion.get(Itinerary, cuerpo["itinerario_id"])
    assert itinerario.user_id is None
    # El punto de partida nunca se guarda (§14)
    assert "punto_partida" not in itinerario.solicitud
    assert "19.0633" not in str(itinerario.solicitud)


def test_restriccion_dura_nunca_se_viola(cliente, catalogo):
    r = cliente.post(
        "/itineraries/recommend",
        json={
            "horas_disponibles": 8,
            "punto_partida": CHOLULA,
            "restricciones": {"sin_escalones": True},
        },
    ).json()
    for parada in r["paradas"]:
        assert parada["poi"]["accesibilidad"]["acceso_sin_escalones"]["valor"] == "si"
    excluidos = {n["poi_id"]: n["motivo"] for n in r["no_incluidos"]}
    assert "demo-cholula-piramide" in excluidos
    assert "sin verificar" in excluidos["demo-cholula-cafe"]
    assert "baño accesible" not in " ".join(excluidos.values())
    assert any("banio_accesible" in d for d in r["datos_desconocidos"])


def test_presupuesto_e_intereses(cliente, catalogo):
    r = cliente.post(
        "/itineraries/recommend",
        json={"horas_disponibles": 3, "presupuesto": "gratis", "intereses": ["plaza"]},
    ).json()
    assert r["paradas"][0]["poi"]["categoria"] == "plaza"
    assert all(p["poi"]["costo_rango"] == "gratis" for p in r["paradas"])


def test_con_cuenta_se_asocia(cliente, catalogo, ana, sesion):
    usuario, cabecera = ana
    r = cliente.post("/itineraries/recommend", json={"horas_disponibles": 2}, headers=cabecera)
    assert r.status_code == 200
    assert sesion.get(Itinerary, r.json()["itinerario_id"]).user_id == usuario.id


def test_validacion(cliente, catalogo):
    assert cliente.post("/itineraries/recommend", json={}).status_code == 422
    assert cliente.post("/itineraries/recommend", json={"horas_disponibles": 0}).status_code == 422
    malo = {"horas_disponibles": 2, "presupuesto": "lujo"}
    assert cliente.post("/itineraries/recommend", json=malo).status_code == 422


def test_desde_guardados_multidia(cliente, catalogo, sesion):
    r = cliente.post(
        "/itineraries/from-saved",
        json={
            "poi_ids": [
                "demo-cholula-museo",
                "demo-cholula-zocalo",
                "demo-cholula-piramide",
                "demo-atlixco-zocalo",
                "demo-atlixco-cerro",
                "no-existe",
            ],
            "dias": 2,
            "horas_por_dia": 3,
            "restricciones": {"sin_escalones": True},
        },
    )
    assert r.status_code == 200
    cuerpo = r.json()
    assert set(cuerpo) == {"itinerario_id", "dias", "no_incluidos", "alternativos"}
    incluidos = [p["poi"]["poi_id"] for d in cuerpo["dias"] for p in d["paradas"]]
    assert set(incluidos) == {"demo-cholula-museo", "demo-cholula-zocalo", "demo-atlixco-zocalo"}
    assert [d["dia"] for d in cuerpo["dias"]] == [1, 2]
    # Cada día agrupa un solo destino
    for dia in cuerpo["dias"]:
        assert len({p["poi"]["destino_id"] for p in dia["paradas"]}) == 1
    motivos = {n["poi_id"]: n["motivo"] for n in cuerpo["no_incluidos"]}
    assert motivos["no-existe"] == "No existe en el catálogo"
    assert "sin escalones" in motivos["demo-cholula-piramide"]
    assert "demo-atlixco-cerro" in motivos
    for alternativo in cuerpo["alternativos"]:
        assert alternativo["poi_id"] not in incluidos
        assert alternativo["accesibilidad"]["acceso_sin_escalones"]["valor"] == "si"
    filas = sesion.scalars(
        select(Recommendation).where(Recommendation.itinerary_id == cuerpo["itinerario_id"])
    ).all()
    assert {f.poi_id for f in filas if f.incluido} == set(incluidos)


def test_desde_guardados_no_cabe(cliente, catalogo):
    cuerpo = cliente.post(
        "/itineraries/from-saved",
        json={
            "poi_ids": ["demo-cholula-piramide", "demo-cholula-museo"],
            "dias": 1,
            "horas_por_dia": 1,
        },
    ).json()
    incluidos = [p["poi"]["poi_id"] for d in cuerpo["dias"] for p in d["paradas"]]
    assert incluidos == ["demo-cholula-museo"]
    assert "No cabe" in cuerpo["no_incluidos"][0]["motivo"]
