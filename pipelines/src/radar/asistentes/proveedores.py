"""Capa anticorrupción de los asistentes con búsqueda web (OpenAI y Gemini).

Cada proveedor devuelve una `RespuestaAsistente` con el mismo formato; el resto del contexto
no conoce los SDK. La extracción trabaja sobre el diccionario crudo de la respuesta, de modo
que se prueba con respuestas guardadas y sin red.
"""

from __future__ import annotations

import os
import threading
from dataclasses import dataclass, field
from typing import Any, Protocol

MODELO_OPENAI_POR_DEFECTO = "gpt-5-mini"
MODELO_GEMINI_POR_DEFECTO = "gemini-3.8-flash"


@dataclass(frozen=True)
class Cita:
    url: str
    titulo: str = ""
    dominio: str = ""


@dataclass(frozen=True)
class RespuestaAsistente:
    texto: str
    modelo: str
    busco: bool
    citas: tuple[Cita, ...] = ()
    tokens_entrada: int | None = None
    tokens_salida: int | None = None
    crudo: dict[str, Any] = field(default_factory=dict)


class Proveedor(Protocol):
    nombre: str
    modelo: str

    def consultar(self, texto: str) -> RespuestaAsistente: ...


def _sin_repetir(citas: list[Cita]) -> tuple[Cita, ...]:
    vistas: set[str] = set()
    unicas = []
    for c in citas:
        if c.url and c.url not in vistas:
            vistas.add(c.url)
            unicas.append(c)
    return tuple(unicas)


def extraer_openai(crudo: dict[str, Any]) -> RespuestaAsistente:
    """Respuesta de la Responses API con la herramienta `web_search`."""
    textos: list[str] = []
    citas: list[Cita] = []
    busco = False
    for item in crudo.get("output", []):
        if item.get("type") == "web_search_call":
            busco = True
        elif item.get("type") == "message":
            for parte in item.get("content", []):
                if parte.get("type") != "output_text":
                    continue
                textos.append(parte.get("text", ""))
                for nota in parte.get("annotations", []):
                    if nota.get("type") == "url_citation":
                        citas.append(Cita(nota.get("url", ""), nota.get("title") or ""))
    uso = crudo.get("usage") or {}
    return RespuestaAsistente(
        texto="\n".join(textos).strip(),
        modelo=crudo.get("model", ""),
        busco=busco,
        citas=_sin_repetir(citas),
        tokens_entrada=uso.get("input_tokens"),
        tokens_salida=uso.get("output_tokens"),
        crudo=crudo,
    )


def extraer_gemini(crudo: dict[str, Any], modelo: str = "") -> RespuestaAsistente:
    """Respuesta de `generate_content` con la herramienta `google_search`."""
    candidatos = crudo.get("candidates") or [{}]
    candidato = candidatos[0]
    partes = (candidato.get("content") or {}).get("parts") or []
    texto = "\n".join(p["text"] for p in partes if p.get("text") and not p.get("thought"))
    fundamento = candidato.get("grounding_metadata") or candidato.get("groundingMetadata") or {}
    consultas = fundamento.get("web_search_queries") or fundamento.get("webSearchQueries") or []
    fragmentos = fundamento.get("grounding_chunks") or fundamento.get("groundingChunks") or []
    citas = []
    for fragmento in fragmentos:
        web = fragmento.get("web") or {}
        if web.get("uri"):
            citas.append(Cita(web["uri"], web.get("title") or "", web.get("domain") or ""))
    uso = crudo.get("usage_metadata") or crudo.get("usageMetadata") or {}
    return RespuestaAsistente(
        texto=texto.strip(),
        modelo=crudo.get("model_version") or crudo.get("modelVersion") or modelo,
        busco=bool(consultas),
        citas=_sin_repetir(citas),
        tokens_entrada=uso.get("prompt_token_count") or uso.get("promptTokenCount"),
        tokens_salida=uso.get("candidates_token_count") or uso.get("candidatesTokenCount"),
        crudo=crudo,
    )


class OpenAIConBusqueda:
    nombre = "openai"

    def __init__(self, modelo: str | None = None, cliente: Any = None) -> None:
        self.modelo = modelo or os.environ.get("OPENAI_MODEL") or MODELO_OPENAI_POR_DEFECTO
        self._cliente = cliente
        self._candado = threading.Lock()

    def _cliente_real(self) -> Any:  # pragma: no cover - requiere llave y red
        with self._candado:  # un solo cliente compartido entre hilos
            if self._cliente is None:
                from openai import OpenAI

                self._cliente = OpenAI()
            return self._cliente

    def consultar(self, texto: str) -> RespuestaAsistente:
        respuesta = self._cliente_real().responses.create(
            model=self.modelo, input=texto, tools=[{"type": "web_search"}]
        )
        return extraer_openai(respuesta.model_dump(mode="json"))


class GeminiConBusqueda:
    nombre = "gemini"

    def __init__(self, modelo: str | None = None, cliente: Any = None) -> None:
        self.modelo = modelo or os.environ.get("GEMINI_MODEL") or MODELO_GEMINI_POR_DEFECTO
        self._cliente = cliente
        self._candado = threading.Lock()

    def _cliente_real(self) -> Any:  # pragma: no cover - requiere llave y red
        with self._candado:  # un solo cliente compartido entre hilos
            if self._cliente is None:
                from google import genai

                self._cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            return self._cliente

    def consultar(self, texto: str) -> RespuestaAsistente:
        from google.genai import types

        configuracion = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
        respuesta = self._cliente_real().models.generate_content(
            model=self.modelo, contents=texto, config=configuracion
        )
        return extraer_gemini(respuesta.model_dump(mode="json"), self.modelo)


def crear(nombre: str, modelo: str | None = None) -> Proveedor:
    if nombre == "openai":
        return OpenAIConBusqueda(modelo)
    if nombre == "gemini":
        return GeminiConBusqueda(modelo)
    raise ValueError(f"Proveedor desconocido: {nombre!r}")
