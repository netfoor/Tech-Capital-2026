"""Tablero institucional: autorización, supresión k, privacidad y separación sintético/real."""

import json
from datetime import UTC, datetime, timedelta

import pytest

from app.config import ajustes
from app.models import (
    AggregateMetric,
    ConfirmedVisit,
    PointOfInterest,
    Review,
    ReviewDimension,
    TripSession,
    User,
    VisitCandidate,
)
from app.services.seguridad import hash_contrasena
from tests.utiles import crear_usuario

PROHIBIDAS = {"lat", "lon", "geom", "user_id", "correo", "nombre_visible", "texto", "usuarios"}


@pytest.fixture
def k3(monkeypatch):
    monkeypatch.setattr(ajustes(), "k_minimo", 3)
    return 3


@pytest.fixture
def lector(sesion):
    return crear_usuario(sesion, "viewer@ejemplo.mx", "viewer")


def _personas(sesion, n, sintetico, prefijo):
    usuarios = [
        User(
            correo=f"{prefijo}{i}@ejemplo.mx",
            hash_contrasena=hash_contrasena("x" * 10),
            rol="visitante",
            is_synthetic=sintetico,
        )
        for i in range(n)
    ]
    sesion.add_all(usuarios)
    sesion.flush()
    return usuarios


def _visitas(sesion, usuarios, poi_id, sintetico, minutos=30.0):
    fecha = datetime(2026, 10, 10, 12, tzinfo=UTC)
    for u in usuarios:
        sesion.add(
            ConfirmedVisit(
                user_id=u.id,
                poi_id=poi_id,
                fecha=fecha,
                fuente_evidencia="check_in",
                confianza=0.8,
                confirmada=True,
                is_synthetic=sintetico,
            )
        )
        viaje = TripSession(user_id=u.id, version_consentimiento="2026-10", is_synthetic=sintetico)
        sesion.add(viaje)
        sesion.flush()
        sesion.add(
            VisitCandidate(
                session_id=viaje.id,
                poi_id=poi_id,
                inicio=fecha,
                fin=fecha + timedelta(minutes=minutos),
                duracion_min=minutos,
                estado="visita_probable",
                fuente_evidencia="gps",
                precision_m=15,
                confianza=0.7,
                is_synthetic=sintetico,
            )
        )
    sesion.commit()


def _poi_extra(sesion, destino_id="puebla"):
    sesion.add(
        PointOfInterest(
            poi_id="demo-puebla-plaza",
            nombre="Plaza demo de Puebla",
            categoria="plaza",
            destino_id=destino_id,
            geom="SRID=4326;POINT(-98.1975 19.0440)",
            is_synthetic=True,
        )
    )
    sesion.commit()


def _sin_prohibidas(objeto):
    if isinstance(objeto, dict):
        for clave, valor in objeto.items():
            assert clave not in PROHIBIDAS, f"campo prohibido «{clave}»"
            _sin_prohibidas(valor)
    elif isinstance(objeto, list):
        for valor in objeto:
            _sin_prohibidas(valor)


# ---------------------------------------------------------------------------
# Autorización


@pytest.mark.parametrize(
    "ruta",
    [
        "/b2b/supply-demand",
        "/b2b/accessibility-gaps",
        "/b2b/metrics?modulo=panorama",
        "/b2b/metrics?modulo=experiencia",
        "/metrics/hhi_llegadas/lineage",
    ],
)
def test_autorizacion(cliente, catalogo, ana, lector, analista, ruta):
    assert cliente.get(ruta).status_code == 401
    assert cliente.get(ruta, headers=ana[1]).status_code == 403
    assert cliente.get(ruta, headers=lector[1]).status_code == 200
    assert cliente.get(ruta, headers=analista[1]).status_code == 200


# ---------------------------------------------------------------------------
# Oferta–demanda con la serie cargada en la base


def test_oferta_demanda_desde_la_base(cliente, sesion, catalogo, lector):
    ahora = datetime.now(UTC)
    filas = []
    for centro, destino, disp, ocup, lleg in (
        ("Atlixco", "atlixco", 100, 50, 60),
        ("Cholula", "cholula", 200, 40, 30),
    ):
        for indicador, valor in (
            ("cuartos_disponibles", disp),
            ("cuartos_ocupados", ocup),
            ("llegadas_turistas", lleg),
            ("turistas_noche", 2 * lleg),
            ("afluencia_visitantes", 2.222 * lleg),
        ):
            filas.append(
                AggregateMetric(
                    metric_id=indicador,
                    destino_id=destino,
                    centro_ot=centro,
                    nivel="destino",
                    periodo="2026-06",
                    valor=valor,
                    procedencia="derivado" if indicador == "afluencia_visitantes" else "medido",
                    version_formula="oficial-1",
                    calculado_en=ahora,
                    fuente_id="sectur-ot-2026-06",
                )
            )
    sesion.add_all(filas)
    sesion.commit()

    r = cliente.get("/b2b/supply-demand", headers=lector[1])
    assert r.status_code == 200
    cuerpo = r.json()
    _sin_prohibidas(cuerpo)
    d = {x["destino_id"]: x for x in cuerpo["destinos"]}
    assert d["atlixco"]["ocupacion_pct"] == pytest.approx(50.0)
    assert d["cholula"]["cuartos_libres_dia"] == pytest.approx(160 / 30)
    # HHI: 60/90 y 30/90 → 4444.44 + 1111.11.
    assert cuerpo["hhi"]["ventana_12m"] == pytest.approx(5555.5556, abs=1e-3)
    assert d["cholula"]["poi_catalogo"] == {"real": 0, "sintetico": 5}
    assert cuerpo["is_synthetic"] is False
    procedencias = {c["campo"]: c["procedencia"] for c in cuerpo["campos"]}
    assert procedencias["afluencia_estimada"] == "derivado"
    assert procedencias["ocupacion_pct"] == "medido"
    assert cuerpo["fuentes"][0]["sha256"]

    csv = cliente.get("/b2b/supply-demand?formato=csv", headers=lector[1])
    assert csv.headers["content-type"].startswith("text/csv")
    lineas = csv.text.splitlines()
    assert lineas[0] == "# modulo: oferta_demanda"
    assert any(linea.startswith("# fuentes: sectur-ot-2026-06") for linea in lineas)
    assert any(linea.startswith("destino_id,") for linea in lineas)


# ---------------------------------------------------------------------------
# Panorama


def test_panorama_supresion_k_y_complementaria(cliente, sesion, catalogo, lector, k3):
    _poi_extra(sesion)
    _visitas(sesion, _personas(sesion, 4, True, "a"), "demo-atlixco-zocalo", True, 40)
    _visitas(sesion, _personas(sesion, 3, True, "c"), "demo-cholula-museo", True, 20)
    _visitas(sesion, _personas(sesion, 1, True, "p"), "demo-puebla-plaza", True)
    cuerpo = cliente.get("/b2b/metrics?modulo=panorama", headers=lector[1]).json()
    g = {x["destino_id"]: x for x in cuerpo["grupos"]}
    assert cuerpo["k_minimo"] == 3
    # Puebla (1 persona) se suprime; Cholula (3, el menor visible) se suprime en complemento.
    assert g["puebla"]["suprimido"] and g["puebla"]["visitas_observadas"] is None
    assert g["puebla"]["personas"] is None
    assert g["cholula"]["suprimido"] and g["cholula"]["supresion_complementaria"]
    assert not g["atlixco"]["suprimido"]
    assert g["atlixco"]["visitas_observadas"] == 4 and g["atlixco"]["personas"] == 4
    assert g["atlixco"]["permanencia"]["mediana_min"] == pytest.approx(40)
    assert g["atlixco"]["cobertura_poi_pct"] == pytest.approx(100 / 3)
    assert g["puebla"]["permanencia"]["mediana_min"] is None


def test_panorama_no_mezcla_sintetico_y_real(cliente, sesion, catalogo, lector, k3):
    _visitas(sesion, _personas(sesion, 3, False, "r"), "demo-atlixco-zocalo", False, 10)
    _visitas(sesion, _personas(sesion, 5, True, "s"), "demo-atlixco-zocalo", True, 50)
    cuerpo = cliente.get("/b2b/metrics?modulo=panorama", headers=lector[1]).json()
    atlixco = [x for x in cuerpo["grupos"] if x["destino_id"] == "atlixco"]
    assert len(atlixco) == 2
    real = next(x for x in atlixco if not x["is_synthetic"])
    sint = next(x for x in atlixco if x["is_synthetic"])
    assert real["visitas_observadas"] == 3 and real["permanencia"]["mediana_min"] == 10
    assert sint["visitas_observadas"] == 5 and sint["permanencia"]["mediana_min"] == 50
    assert cuerpo["hay_reales"] and cuerpo["hay_sinteticos"]


def test_ninguna_respuesta_trae_coordenadas_ni_personas(cliente, sesion, catalogo, lector, k3):
    usuarios = _personas(sesion, 3, True, "z")
    _visitas(sesion, usuarios, "demo-atlixco-zocalo", True)
    for u in usuarios:
        resena = Review(
            user_id=u.id, poi_id="demo-atlixco-zocalo", texto="Secreto", is_synthetic=True
        )
        sesion.add(resena)
        sesion.flush()
        sesion.add(ReviewDimension(review_id=resena.id, dimension="global", puntaje=4))
    sesion.commit()
    for ruta in (
        "/b2b/supply-demand",
        "/b2b/accessibility-gaps",
        "/b2b/metrics?modulo=panorama",
        "/b2b/metrics?modulo=experiencia",
        "/metrics/permanencia_mediana_min/lineage",
    ):
        r = cliente.get(ruta, headers=lector[1])
        assert r.status_code == 200
        _sin_prohibidas(r.json())
        texto = r.text
        for u in usuarios:
            assert str(u.id) not in texto and u.correo not in texto
        assert "Secreto" not in texto
        assert "18.9088" not in texto and "-98.4342" not in texto


# ---------------------------------------------------------------------------
# Experiencia


def test_experiencia_media_intervalos_y_supresion(cliente, sesion, catalogo, lector, k3):
    puntajes = [5, 4, 4, 2]
    for u, p in zip(_personas(sesion, 4, True, "e"), puntajes, strict=True):
        resena = Review(user_id=u.id, poi_id="demo-cholula-museo", is_synthetic=True)
        sesion.add(resena)
        sesion.flush()
        sesion.add_all(
            [
                ReviewDimension(review_id=resena.id, dimension="global", puntaje=p),
                ReviewDimension(review_id=resena.id, dimension="senalizacion", puntaje=2),
            ]
        )
    u = _personas(sesion, 1, True, "solo")[0]
    resena = Review(user_id=u.id, poi_id="demo-atlixco-zocalo", is_synthetic=True)
    sesion.add(resena)
    sesion.flush()
    sesion.add(ReviewDimension(review_id=resena.id, dimension="global", puntaje=1))
    sesion.commit()

    cuerpo = cliente.get("/b2b/metrics?modulo=experiencia", headers=lector[1]).json()
    g = {(x["destino_id"], x["dimension"]): x for x in cuerpo["grupos"]}
    cholula = g[("cholula", "global")]
    # Atlixco (1 persona) se suprime y Cholula se suprime en complemento (dos destinos).
    assert g[("atlixco", "global")]["suprimido"]
    assert cholula["suprimido"] and cholula["supresion_complementaria"]
    # Señalización solo tiene Cholula, con 4 personas: visible.
    senal = g[("cholula", "senalizacion")]
    assert not senal["suprimido"] and senal["media"] == 2 and senal["proporcion_baja"] == 1
    # El total de todos los destinos: 5 personas, media (5+4+4+2+1)/5 = 3.2.
    total = g[(None, "global")]
    assert total["media"] == pytest.approx(3.2) and total["n"] == 5
    lo, hi = total["media_ic95"]
    assert lo <= 3.2 <= hi
    lo, hi = total["proporcion_baja_ic95"]
    assert lo < 0.4 < hi
    assert all(x["is_synthetic"] for x in cuerpo["grupos"])


# ---------------------------------------------------------------------------
# Inclusión y circuito de moderación


def test_brechas_de_accesibilidad(cliente, catalogo, lector):
    cuerpo = cliente.get(
        "/b2b/accessibility-gaps?corredor_id=demo-cholula-atlixco", headers=lector[1]
    ).json()
    d = {x["destino_id"]: x for x in cuerpo["por_destino"]}
    assert d["cholula"]["poi"] == 5 and d["cholula"]["con_informacion"] == 4
    assert (d["cholula"]["verificada"], d["cholula"]["parcial"], d["cholula"]["sin_verificar"]) == (
        1,
        2,
        2,
    )
    assert d["atlixco"]["con_informacion_pct"] == pytest.approx(100.0)
    a = {x["atributo"]: x for x in cuerpo["por_atributo"]}
    sin_escalones = a["acceso_sin_escalones"]
    assert (sin_escalones["poi"], sin_escalones["con_valor"], sin_escalones["verificado"]) == (
        8,
        6,
        5,
    )
    assert sin_escalones["sin_dato"] == 2 and sin_escalones["sin_verificar"] == 1
    assert cuerpo["hay_sinteticos"] and cuerpo["resumen"][0]["is_synthetic"]
    assert "no nivel de accesibilidad" in cuerpo["aviso"]
    assert any(p["tipo"] == "verificar_destino" for p in cuerpo["prioridades"])
    vacio = cliente.get("/b2b/accessibility-gaps?corredor_id=otro", headers=lector[1]).json()
    assert vacio["por_destino"] == [] and vacio["resumen"] == []


def test_circuito_moderacion_llega_al_tablero(cliente, catalogo, ana, analista, monkeypatch):
    monkeypatch.setattr(ajustes(), "k_minimo", 1)
    r = cliente.post(
        "/reports/barrier",
        json={"poi_id": "demo-cholula-zocalo", "tipo": "escalones", "descripcion": "Escalón"},
        headers=ana[1],
    )
    caso = r.json()["moderation_case_id"]
    antes = cliente.get("/b2b/accessibility-gaps", headers=analista[1]).json()
    assert antes["barreras"][0]["abiertos"] == 1
    cliente.post(f"/moderation/{caso}/decision", json={"decision": "aceptar"}, headers=analista[1])
    despues = cliente.get("/b2b/accessibility-gaps", headers=analista[1]).json()
    barreras = despues["barreras"][0]
    assert barreras["aceptados"] == 1 and barreras["abiertos"] == 0
    assert barreras["tasa_aceptacion"] == 1 and barreras["tiempo_moderacion_mediano_h"] >= 0
    assert any(
        p["tipo"] == "atender_barrera" and p["poi_id"] == "demo-cholula-zocalo"
        for p in despues["prioridades"]
    )
    # El reporte es de una persona real, pero sobre un lugar sintético: cuenta como sintético.
    assert barreras["is_synthetic"] is True
    assert len(despues["barreras"]) == 1
    _sin_prohibidas(despues)


def test_barreras_con_menos_de_k_se_suprimen(cliente, catalogo, ana, analista):
    cliente.post(
        "/reports/barrier",
        json={"poi_id": "demo-cholula-zocalo", "tipo": "escalones"},
        headers=ana[1],
    )
    barreras = cliente.get("/b2b/accessibility-gaps", headers=analista[1]).json()["barreras"][0]
    assert barreras["suprimido"] and barreras["casos"] is None and barreras["personas"] is None


# ---------------------------------------------------------------------------
# Linaje


def test_linaje(cliente, catalogo, lector):
    r = cliente.get("/metrics/hhi_llegadas/lineage", headers=lector[1])
    cuerpo = r.json()
    assert cuerpo["ficha"]["formula"].startswith("Σ (100 × sᵢ)²")
    assert cuerpo["definicion"]["version_formula"] == "1"
    fuente = cuerpo["fuentes"][0]
    assert fuente["fuente_id"] == "sectur-ot-2026-06" and fuente["url"].startswith("https://")
    assert fuente["sha256"]
    assert cliente.get("/metrics/no-existe/lineage", headers=lector[1]).status_code == 404


def test_csv_panorama_marca_sinteticos(cliente, sesion, catalogo, lector, k3):
    _visitas(sesion, _personas(sesion, 3, True, "v"), "demo-atlixco-zocalo", True)
    r = cliente.get("/b2b/metrics?modulo=panorama&formato=csv", headers=lector[1])
    assert "# is_synthetic: contiene filas sintéticas" in r.text
    encabezado = next(linea for linea in r.text.splitlines() if not linea.startswith("#"))
    assert "is_synthetic" in encabezado.split(",")
    assert json.dumps(r.text).count("user_id") == 0


# ---------------------------------------------------------------------------
# Semilla de demostración


def test_semilla_demo_idempotente_y_sintetica(cliente, sesion, catalogo, monkeypatch):
    from app.services import demo_tablero

    monkeypatch.setattr(ajustes(), "demo_analista_correo", "Analista.Demo@ejemplo.mx")
    monkeypatch.setattr(ajustes(), "demo_analista_contrasena", "contrasena-demo")
    for _ in range(2):
        demo_tablero.asegurar_analista(sesion)
        demo_tablero.borrar_conjunto(sesion)
        cuenta = demo_tablero.crear_conjunto(sesion)
        sesion.commit()
    assert sesion.query(ConfirmedVisit).count() == cuenta["visitas"] > 0
    assert sesion.query(ConfirmedVisit).filter(ConfirmedVisit.is_synthetic.is_(False)).count() == 0
    assert sesion.query(Review).filter(Review.is_synthetic.is_(False)).count() == 0
    r = cliente.post(
        "/auth/login", json={"correo": "analista.demo@ejemplo.mx", "contrasena": "contrasena-demo"}
    )
    cabecera = {"Authorization": f"Bearer {r.json()['access_token']}"}
    panorama = cliente.get("/b2b/metrics?modulo=panorama", headers=cabecera).json()
    visibles = [g for g in panorama["grupos"] if not g["suprimido"]]
    assert visibles and all(g["is_synthetic"] for g in panorama["grupos"])
    assert cliente.get("/moderation", headers=cabecera).json()["items"]


def test_semilla_demo_sin_credenciales(sesion, monkeypatch):
    from app.services import demo_tablero

    monkeypatch.setattr(ajustes(), "demo_analista_correo", "")
    with pytest.raises(demo_tablero.ErrorDemo):
        demo_tablero.asegurar_analista(sesion)
