import json
from pathlib import Path

import pytest

from radar.asistentes import proveedores

DATOS = Path(__file__).parent / "datos" / "asistentes"


def cargar(nombre):
    return json.loads((DATOS / f"{nombre}.json").read_text(encoding="utf-8"))


def test_openai_extrae_texto_busqueda_citas_y_tokens():
    r = proveedores.extraer_openai(cargar("openai_con_busqueda"))
    assert r.texto == "Te recomiendo Cuetzalan y Zacatlán, además de Cholula."
    assert r.busco is True
    assert r.modelo == "gpt-5-mini-2026-08-07"
    assert [c.url for c in r.citas] == [
        "https://www.puebla.gob.mx/cuetzalan",
        "https://es.wikipedia.org/wiki/Zacatl%C3%A1n",
    ]  # sin duplicados
    assert (r.tokens_entrada, r.tokens_salida) == (1520, 310)


def test_openai_sin_busqueda():
    r = proveedores.extraer_openai(cargar("openai_sin_busqueda"))
    assert r.busco is False
    assert r.citas == ()
    assert r.texto == "Visita Atlixco."


def test_gemini_extrae_texto_busqueda_citas_y_tokens():
    r = proveedores.extraer_gemini(cargar("gemini_con_busqueda"))
    assert r.texto == "Puedes visitar Chignahuapan y Huauchinango."
    assert r.busco is True
    assert [c.titulo for c in r.citas] == ["tripadvisor.com.mx", "mexicodesconocido.com.mx"]
    assert r.citas[0].dominio == "tripadvisor.com.mx"
    assert (r.tokens_entrada, r.tokens_salida) == (12, 40)
    assert r.modelo == "gemini-3.8-flash"


def test_gemini_decide_no_buscar():
    r = proveedores.extraer_gemini(cargar("gemini_sin_busqueda"))
    assert r.busco is False
    assert r.citas == ()
    assert r.texto == "Visita Cholula."


def test_gemini_acepta_nombres_en_camel_case():
    crudo = {
        "candidates": [
            {
                "content": {"parts": [{"text": "x"}]},
                "groundingMetadata": {
                    "webSearchQueries": ["q"],
                    "groundingChunks": [{"web": {"uri": "https://a.com/x", "title": "a.com"}}],
                },
            }
        ],
        "usageMetadata": {"promptTokenCount": 1, "candidatesTokenCount": 2},
    }
    r = proveedores.extraer_gemini(crudo, "m")
    assert r.busco and r.citas[0].url == "https://a.com/x"
    assert (r.tokens_entrada, r.tokens_salida, r.modelo) == (1, 2, "m")


def test_respuesta_vacia_no_rompe():
    assert proveedores.extraer_gemini({}).texto == ""
    assert proveedores.extraer_openai({}).texto == ""


class _Modelo:
    def __init__(self, datos):
        self._datos = datos

    def model_dump(self, mode="json"):
        return self._datos


class _ClienteOpenAI:
    def __init__(self):
        self.llamadas = []
        self.responses = self

    def create(self, **kwargs):
        self.llamadas.append(kwargs)
        return _Modelo(cargar("openai_con_busqueda"))


def test_openai_envia_la_herramienta_de_busqueda():
    cliente = _ClienteOpenAI()
    p = proveedores.OpenAIConBusqueda("modelo-x", cliente)
    r = p.consultar("hola")
    assert cliente.llamadas == [
        {"model": "modelo-x", "input": "hola", "tools": [{"type": "web_search"}]}
    ]
    assert r.busco


class _ClienteGemini:
    def __init__(self):
        self.llamadas = []
        self.models = self

    def generate_content(self, **kwargs):
        self.llamadas.append(kwargs)
        return _Modelo(cargar("gemini_con_busqueda"))


def test_gemini_envia_google_search():
    cliente = _ClienteGemini()
    p = proveedores.GeminiConBusqueda("modelo-g", cliente)
    r = p.consultar("hola")
    llamada = cliente.llamadas[0]
    assert llamada["model"] == "modelo-g" and llamada["contents"] == "hola"
    assert llamada["config"].tools[0].google_search is not None
    assert r.busco


def test_modelo_se_toma_del_entorno(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "mi-modelo")
    assert proveedores.OpenAIConBusqueda().modelo == "mi-modelo"
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    assert proveedores.GeminiConBusqueda().modelo == proveedores.MODELO_GEMINI_POR_DEFECTO


def test_crear_y_proveedor_desconocido():
    assert proveedores.crear("openai").nombre == "openai"
    assert proveedores.crear("gemini").nombre == "gemini"
    with pytest.raises(ValueError):
        proveedores.crear("otro")
