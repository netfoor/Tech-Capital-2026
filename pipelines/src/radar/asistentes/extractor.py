"""Extractor de menciones con un modelo (para ko y zh). Los resultados se guardan en caché."""

from __future__ import annotations

import json
import os
import threading
from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from radar import config
from radar.asistentes import menciones
from radar.asistentes.proveedores import MODELO_GEMINI_POR_DEFECTO
from radar.catalogo import Destino


def carpeta_cache() -> Path:
    return config.ruta(config.CRUDO, "asistentes-extractor")


def cargar_cache(carpeta: Path | None = None) -> dict[str, dict]:
    carpeta = carpeta or carpeta_cache()
    cache: dict[str, dict] = {}
    for ruta in sorted(carpeta.glob("*.jsonl")) if carpeta.exists() else []:
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if linea.strip():
                r = json.loads(linea)
                cache[r["corrida_id"]] = r
    return cache


def pendientes(corridas: list[dict], cache: dict[str, dict]) -> list[dict]:
    return [
        c
        for c in corridas
        if c["idioma"] in menciones.IDIOMAS_CON_EXTRACTOR and c["corrida_id"] not in cache
    ]


def llamar_gemini() -> Callable[[str], str]:  # pragma: no cover - requiere llave y red
    from google import genai

    cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    modelo = os.environ.get("GEMINI_MODEL") or MODELO_GEMINI_POR_DEFECTO

    def llamar(instruccion: str) -> str:
        return cliente.models.generate_content(model=modelo, contents=instruccion).text or ""

    return llamar


def ejecutar(
    corridas: list[dict],
    destinos: list[Destino],
    llamar: Callable[[str], str],
    carpeta: Path | None = None,
    concurrencia: int = 8,
    modelo: str = "",
) -> Iterator[dict]:
    """Anota las corridas sin caché y agrega cada resultado a la caché."""
    carpeta = carpeta or carpeta_cache()
    carpeta.mkdir(parents=True, exist_ok=True)
    por_hacer = pendientes(corridas, cargar_cache(carpeta))
    candado = threading.Lock()
    archivo = carpeta / "extraidos.jsonl"

    def uno(c: dict) -> dict:
        ids = menciones.extraer(c["texto"], destinos, llamar)
        r = {"corrida_id": c["corrida_id"], "destinos": ids, "modelo": modelo}
        with candado, archivo.open("a", encoding="utf-8") as f:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        return r

    with ThreadPoolExecutor(max_workers=concurrencia) as pool:
        yield from pool.map(uno, por_hacer)
