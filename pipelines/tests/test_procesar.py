import pandas as pd

from radar import catalogo
from radar.asistentes import procesar


def linea(i, idioma="es", proveedor="openai", busco=True, texto="Visita Cuetzalan"):
    return {
        "corrida_id": f"c{i:02d}",
        "prompt_id": "ES-C01",
        "brazo": "controlado",
        "proveedor": proveedor,
        "modelo": "m",
        "modelo_servido": "m-2026",
        "idioma": idioma,
        "mercado": "MX",
        "tono": "casual",
        "con_busqueda": True,
        "busco": busco,
        "repeticion": i,
        "fecha": "2026-10-16",
        "prompt": "¿A dónde voy?",
        "texto": texto,
        "citas": [{"url": "https://www.puebla.gob.mx/a", "titulo": "t", "dominio": ""}],
        "tokens_entrada": 10,
        "tokens_salida": 5,
        "sha256_respuesta": "0" * 64,
        "archivo_crudo": "x.jsonl",
    }


def test_fragmento_corta_en_palabra_y_respeta_el_maximo():
    largo = "palabra " * 200
    f = procesar.fragmento(largo)
    assert len(f) <= 600 and f.endswith("…")
    assert procesar.fragmento("  corto   texto ") == "corto texto"


def test_cinco_tablas_con_sus_columnas():
    destinos = catalogo.cargar()
    corridas = [linea(1), linea(2, "en", texto="Try Zacatlan"), linea(3, "ko", "gemini", False)]
    cache = {"c03": {"destinos": ["atlixco"]}}
    t = procesar.procesar(
        corridas, destinos, catalogo.cargar_terminos_idiomas(), {"gob.mx": "gobierno"}, cache
    )
    assert set(t) == {
        "asistentes_corridas",
        "asistentes_menciones",
        "asistentes_citas",
        "asistentes_visibilidad",
        "asistentes_ejemplos",
    }
    assert t["asistentes_corridas"].modelo.tolist() == ["m-2026"] * 3
    m = t["asistentes_menciones"]
    assert set(m.metodo) == {"terminos", "extractor"}
    assert t["asistentes_citas"].tipo_dominio.tolist() == ["gobierno"] * 3
    v = t["asistentes_visibilidad"]
    assert len(v[v.segmento == "total"]) == len(destinos)
    ej = t["asistentes_ejemplos"]
    assert sorted(ej.idioma) == ["en", "es"]  # solo OpenAI con búsqueda
    assert (ej.fragmento.str.len() <= 600).all()


def test_ejemplos_son_reproducibles():
    cs = [linea(i) for i in range(10)]
    assert procesar.elegir_ejemplos(cs) == procesar.elegir_ejemplos(cs)


def test_leer_corridas_une_archivos_sin_duplicar(tmp_path):
    import json

    for nombre in ("a.jsonl", "b.jsonl"):
        (tmp_path / nombre).write_text(
            "\n".join(json.dumps(linea(i)) for i in (1, 2)) + "\n", encoding="utf-8"
        )
    assert len(procesar.leer_corridas(tmp_path)) == 2


def test_tipo_dominio_presente_en_el_90_por_ciento_de_las_citas_reales():
    from radar import config

    ruta = config.ruta(config.CURADO, "asistentes_citas.csv")
    if not ruta.exists():
        return
    c = pd.read_csv(ruta)
    assert c.tipo_dominio.notna().mean() >= 0.9
