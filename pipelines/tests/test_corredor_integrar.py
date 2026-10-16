import hashlib
from pathlib import Path

import pandas as pd
import pytest

from radar.corredor import calidad, integrar

DATOS = Path(__file__).parent / "datos" / "corredor"


@pytest.fixture(scope="module")
def resultado() -> integrar.Resultado:
    return integrar.construir(DATOS)


def _poi(r: integrar.Resultado, poi_id: str) -> pd.Series:
    return r.poi.set_index("poi_id").loc[poi_id]


def test_contrato_de_columnas(resultado):
    assert list(resultado.poi.columns) == integrar.COLUMNAS_POI
    assert list(resultado.accesibilidad.columns) == integrar.COLUMNAS_ACCESIBILIDAD
    assert list(resultado.corredores.columns) == integrar.COLUMNAS_CORREDORES
    assert set(resultado.poi["categoria"]) <= integrar.CATEGORIAS
    assert set(resultado.accesibilidad["atributo"]) <= integrar.ATRIBUTOS
    assert (resultado.poi["is_synthetic"] == "false").all()
    assert resultado.poi["poi_id"].is_unique


def test_enlace_sic_y_denue_a_menos_de_75_m(resultado):
    amparo = _poi(resultado, "osm-n101")
    assert amparo["sic_id"] == "museo-9001"
    assert amparo["denue_id"] == "5001"
    assert amparo["fuentes"] == "osm-overpass|sic-cultura|inegi-denue"
    assert amparo["match_score"] == pytest.approx(1.0)
    assert amparo["corredor_id"] == "puebla-cholula" and amparo["destino_id"] == "puebla"
    assert _poi(resultado, "osm-n103")["denue_id"] == "5003"


def test_mas_de_75_m_no_se_enlaza(resultado):
    assert _poi(resultado, "osm-n108")["sic_id"] == ""
    assert "sic-centro_cultural-9101" in set(resultado.poi["poi_id"])


def test_registros_propios_y_descartes(resultado):
    ids = set(resultado.poi["poi_id"])
    assert "sic-museo-9003" in ids  # sin par en OSM
    assert "sic-museo-9002" not in ids  # sin coordenadas
    assert "denue-5002" in ids  # alojamiento sin par
    assert "denue-5004" not in ids  # alimentos: solo se enlazan
    assert "denue-5005" not in ids  # agencias: solo se cuentan
    assert "osm-n105" not in ids and "osm-n106" not in ids  # banca y tablero
    assert resultado.estadisticas["sic_sin_coordenadas_validas"] == 1
    assert _poi(resultado, "denue-5002")["nombre"] == "Hotel Colonial de Puebla"


def test_duplicado_de_osm_se_funde(resultado):
    ids = set(resultado.poi["poi_id"])
    assert "osm-n102" in ids and "osm-w201" not in ids
    acc = resultado.accesibilidad
    catedral = dict(acc[acc["poi_id"] == "osm-n102"][["atributo", "valor"]].values)
    assert catedral == {"acceso_sin_escalones": "parcial", "numero_escalones": "5", "rampa": "si"}
    assert _poi(resultado, "osm-n102")["costo_rango"] == "gratis"


def test_sin_etiqueta_sin_fila_de_accesibilidad(resultado):
    assert "osm-n103" not in set(resultado.accesibilidad["poi_id"])
    banio = resultado.accesibilidad[resultado.accesibilidad["poi_id"] == "osm-n104"]
    assert banio[["atributo", "valor"]].values.tolist() == [["banio_accesible", "no"]]


def test_cholula_en_el_corredor(resultado):
    zona = _poi(resultado, "osm-n107")
    assert zona["destino_id"] == "cholula" and zona["municipio_cvegeo"] == "21119"
    acc = resultado.accesibilidad
    assert set(acc[acc["poi_id"] == "osm-n107"]["atributo"]) == {"pendiente_pct", "superficie"}


def test_oferta_por_municipio(resultado):
    oferta = resultado.oferta.set_index(["municipio_cvegeo", "scian_prefijo"])["establecimientos"]
    assert oferta[("21114", "7225")] == 2
    assert oferta[("21043", "7211")] == 1


def test_determinista(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    integrar.ejecutar(DATOS, a)
    integrar.ejecutar(DATOS, b)
    for nombre in ("poi.csv", "poi_accesibilidad.csv", "corredores.csv"):
        ha = hashlib.sha256((a / nombre).read_bytes()).hexdigest()
        hb = hashlib.sha256((b / nombre).read_bytes()).hexdigest()
        assert ha == hb


COLUMNAS_CATALOGO = (
    "id,nombre,propietario,url,licencia,url_licencia,fecha_consulta,fecha_actualizacion_fuente,"
    "alcance_espacial,alcance_temporal,granularidad,formato,campos_usados,calidad_observada,"
    "faltantes,sesgos,terminos_uso,transformaciones,script_ingesta,responsable,estado"
).split(",")


def test_catalogo_de_fuentes(resultado):
    from radar import config

    catalogo = pd.read_csv(config.ruta("data", "catalog", "data_catalog.csv"), dtype=str)
    assert list(catalogo.columns) == COLUMNAS_CATALOGO
    assert catalogo["id"].is_unique
    assert set(catalogo["estado"]) <= {"verificada", "pendiente", "descartada"}
    usadas = {f for fs in resultado.poi["fuentes"] for f in fs.split("|")}
    assert usadas <= set(catalogo["id"])


def test_reporte_de_calidad(resultado):
    texto = calidad.reporte(resultado)
    assert "Cobertura de información de accesibilidad" in texto
    assert "`poi_id` repetidos: 0" in texto
    assert texto == calidad.reporte(resultado)
