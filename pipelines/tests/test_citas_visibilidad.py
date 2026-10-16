import pandas as pd
import pytest

from radar.asistentes import citas, visibilidad

TIPOS = {"gob.mx": "gobierno", "wikipedia.org": "enciclopedia", "tripadvisor.com": "agencia_viajes"}


def test_dominio_de_una_url_normal():
    assert citas.dominio_de("https://www.puebla.gob.mx/x?y=1") == "puebla.gob.mx"


def test_dominio_de_redireccion_de_gemini_usa_el_titulo_o_dominio():
    url = "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AAA"
    assert citas.dominio_de(url, "tripadvisor.com") == "tripadvisor.com"
    assert citas.dominio_de(url, "Un título con espacios", "wikipedia.org") == "wikipedia.org"
    assert citas.dominio_de(url, "Un título con espacios") == ""


def test_tipo_por_sufijo():
    assert citas.tipo_de("puebla.gob.mx", TIPOS) == "gobierno"
    assert citas.tipo_de("es.wikipedia.org", TIPOS) == "enciclopedia"
    assert citas.tipo_de("blog.desconocido.com", TIPOS) == "otro"
    assert citas.tipo_de("", TIPOS) == "otro"


def test_dominios_reales_tienen_al_menos_40_y_tipos_validos():
    tipos = citas.cargar_tipos()
    assert len(tipos) >= 40
    assert set(tipos.values()) <= citas.TIPOS


def corridas():
    base = {"proveedor": "openai", "brazo": "controlado", "tono": "casual"}
    return [
        {"corrida_id": "a", "idioma": "es", **base},
        {"corrida_id": "b", "idioma": "es", **base},
        {"corrida_id": "c", "idioma": "en", **base},
        {"corrida_id": "d", "idioma": "en", **base},
    ]


def test_visibilidad_cuenta_corridas_con_al_menos_una_mencion():
    menc = {"a": {"x"}, "b": {"x", "y"}, "c": {"y"}, "d": set()}
    v = visibilidad.calcular(corridas(), menc, ["x", "y"])
    total_x = v[(v.segmento == "total") & (v.destino_id == "x")].iloc[0]
    assert (total_x.n, total_x.k) == (4, 2)
    assert total_x.visibilidad_pct == pytest.approx(50.0)
    assert 0 < total_x.ic95_bajo < 50 < total_x.ic95_alto < 100
    es_y = v[(v.segmento == "idioma=es") & (v.destino_id == "y")].iloc[0]
    assert (es_y.n, es_y.k) == (2, 1)


def test_visibilidad_trae_los_segmentos_del_plan():
    v = visibilidad.calcular(corridas(), {}, ["x"])
    segs = set(v.segmento)
    assert {"total", "proveedor=openai", "idioma=es", "tono=casual", "brazo=controlado"} <= segs
    assert "proveedor=openai;idioma=en" in segs
    assert (v.k == 0).all()


def test_tablas_reales_tienen_los_12_pueblos_en_el_total():
    from radar import catalogo, config

    ruta = config.ruta(config.CURADO, "asistentes_visibilidad.csv")
    if not ruta.exists():
        pytest.skip("Ejecuta `uv run radar asistentes procesar` primero")
    v = pd.read_csv(ruta)
    pm = {d.destino_id for d in catalogo.cargar() if d.pueblo_magico}
    assert pm <= set(v[v.segmento == "total"].destino_id)
    assert (v.k <= v.n).all()
