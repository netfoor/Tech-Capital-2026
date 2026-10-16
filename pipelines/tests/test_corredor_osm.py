from radar import geo
from radar.corredor import osm, sic, zonas


def _elemento(**etiquetas: str) -> osm.Elemento:
    return osm.Elemento("node", 1, 19.0433, -98.1981, dict(etiquetas), "2025-01-01")


def test_categorias_del_contrato():
    assert osm.categoria({"tourism": "museum"}) == ("museo", "museum")
    assert osm.categoria({"amenity": "place_of_worship"})[0] == "templo"
    assert osm.categoria({"historic": "archaeological_site"})[0] == "zona_arqueologica"
    assert osm.categoria({"tourism": "viewpoint"})[0] == "mirador"
    assert osm.categoria({"amenity": "toilets"})[0] == "banio"
    assert osm.categoria({"tourism": "hotel"})[0] == "alojamiento"
    assert osm.categoria({"shop": "craft"})[0] == "artesanias"
    assert osm.categoria({"historic": "monument"})[0] == "sitio_historico"
    assert osm.categoria({"tourism": "information", "information": "board"}) is None


def test_bancas_y_sin_nombre_no_son_poi():
    assert osm.es_poi(_elemento(amenity="bench")) is None
    assert osm.es_poi(_elemento(tourism="museum")) is None
    assert osm.es_poi(_elemento(amenity="toilets")) == ("banio", "toilets")


def test_wheelchair_se_mapea_sin_verificar():
    filas = osm.accesibilidad(_elemento(tourism="museum", name="M", wheelchair="yes"), "museo")
    assert len(filas) == 1
    f = filas[0]
    assert (f["atributo"], f["valor"], f["origen"]) == ("acceso_sin_escalones", "si", "osm")
    assert f["estado"] == "sin_verificar" and f["confianza"] == 0.6
    assert f["evidencia"] == "osm:node/1 wheelchair=yes"
    limitado = osm.accesibilidad(_elemento(wheelchair="limited"), "museo")[0]
    assert limitado["valor"] == "parcial"
    assert osm.accesibilidad(_elemento(wheelchair="no"), "museo")[0]["valor"] == "no"


def test_sin_etiqueta_no_hay_fila():
    assert osm.accesibilidad(_elemento(tourism="museum", name="M"), "museo") == []
    assert osm.accesibilidad(_elemento(wheelchair="unknown"), "museo") == []


def test_otras_etiquetas():
    e = _elemento(step_count="12", incline="8%", surface="sett", ramp="no", bench="yes")
    por_atributo = {f["atributo"]: f["valor"] for f in osm.accesibilidad(e, "templo")}
    assert por_atributo == {
        "numero_escalones": "12",
        "pendiente_pct": "8",
        "superficie": "sett",
        "rampa": "no",
        "asientos": "si",
    }
    assert osm.accesibilidad(_elemento(incline="up"), "templo") == []


def test_wheelchair_en_banio_es_banio_accesible():
    filas = osm.accesibilidad(_elemento(amenity="toilets", wheelchair="yes"), "banio")
    assert [(f["atributo"], f["valor"]) for f in filas] == [("banio_accesible", "si")]


def test_costo_solo_desde_fee():
    assert osm.costo({"fee": "no"}) == "gratis"
    assert osm.costo({"fee": "yes"}) == "desconocido"
    assert osm.costo({}) == "desconocido"


def test_compactar_quita_usuarios():
    datos = {"elements": [{"type": "node", "id": 2, "user": "x", "uid": 1, "changeset": 3}]}
    assert osm.compactar(datos, "q")["elements"] == [{"type": "node", "id": 2}]


def test_consultas_usan_las_zonas():
    q = osm.consulta_corredor(zonas.CORREDOR, zonas.centros_corredor())
    assert "(19.03,-98.315,19.072,-98.185)" in q and "around:1200" in q
    assert q.strip().endswith("out center meta;")
    assert len(zonas.centros_pueblos_magicos()) == 11


def test_geo_puebla():
    assert geo.en_puebla(19.0433, -98.1981)
    assert not geo.en_puebla(19.4326, -99.1332)  # Ciudad de México
    assert geo.municipio_de(19.0433, -98.1981) == "21114"
    assert 11_000 < geo.distancia_m(19.0433, -98.1981, 19.0625, -98.3075) < 12_000


def test_sic_quita_contacto_y_filtra_puebla():
    contenido = (
        b"museo_id,museo_nombre,estado_id,email,museo_telefono1\n"
        b"1,A,21,a@b.mx,222\n2,B,9,c@d.mx,555\n"
    )
    assert sic.filtrar_puebla(contenido).decode() == "museo_id,museo_nombre,estado_id\n1,A,21\n"
