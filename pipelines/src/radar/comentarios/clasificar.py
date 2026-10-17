"""Clasificador reanudable con caché. El modelo se inyecta como función (sin red en pruebas)."""

from __future__ import annotations

import hashlib
import json
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import jsonschema

from radar.comentarios import limpieza, taxonomia

PROMPT = (Path(__file__).parent / "prompt_v2.md").read_text(encoding="utf-8")
VERSION = "v2"


def clave(c: dict) -> str:
    base = f"{c['video_id']}|{c['destino_id']}|{c['texto']}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]


def cargar_cache(ruta: Path) -> dict[str, dict]:
    if not ruta.exists():
        return {}
    filas = [json.loads(x) for x in ruta.read_text(encoding="utf-8").splitlines() if x.strip()]
    return {f["clave"]: f for f in filas if f.get("version") == VERSION}


def _analizar(salida: str, ids: set[int]) -> dict[int, dict]:
    inicio, fin = salida.find("["), salida.rfind("]")
    if inicio < 0 or fin < 0:
        return {}
    try:
        datos = json.loads(salida[inicio : fin + 1])
    except json.JSONDecodeError:
        return {}
    validos: dict[int, dict] = {}
    for d in datos:
        try:
            jsonschema.validate(d, taxonomia.ESQUEMA_SALIDA)
        except jsonschema.ValidationError:
            continue
        if d["id"] in ids:
            validos[d["id"]] = d
    return validos


def clasificar(
    comentarios: list[dict],
    llamar: Callable[[str], str],
    ruta_cache: Path,
    lote: int = 20,
    modelo: str = "",
    concurrencia: int = 6,
) -> dict[str, dict]:
    """Clasifica los comentarios sin caché por lotes; devuelve la caché completa."""
    cache = cargar_cache(ruta_cache)
    ruta_cache.parent.mkdir(parents=True, exist_ok=True)
    pendientes = [c for c in comentarios if clave(c) not in cache]
    candado = threading.Lock()

    def procesar(bloque: list[dict]) -> None:
        lineas = [f"{n} | {limpieza.limpiar(c['texto'])}" for n, c in enumerate(bloque)]
        respuesta = _analizar(llamar(PROMPT + "\n\n" + "\n".join(lineas)), set(range(len(bloque))))
        with candado, ruta_cache.open("a", encoding="utf-8") as f:
            for n, c in enumerate(bloque):
                r = respuesta.get(n)
                if r is None:
                    continue  # se reintenta en la siguiente corrida
                fila = {
                    "clave": clave(c),
                    "destino_id": c["destino_id"],
                    "categoria": r["categoria"],
                    "friccion": r.get("friccion") if r["categoria"] == "friccion" else None,
                    "version": VERSION,
                    "modelo": modelo,
                }
                cache[fila["clave"]] = fila
                f.write(json.dumps(fila, ensure_ascii=False) + "\n")

    bloques = [pendientes[i : i + lote] for i in range(0, len(pendientes), lote)]
    with ThreadPoolExecutor(max_workers=concurrencia) as pool:
        list(pool.map(procesar, bloques))
    return cache


def llamar_openai() -> Callable[[str], str]:  # pragma: no cover - requiere llave y red
    """Modelo de OpenAI sin búsqueda web, para clasificar texto (alternativa a Gemini)."""
    import os

    from openai import OpenAI

    cliente = OpenAI()
    modelo = os.environ.get("OPENAI_MODEL") or "gpt-5-mini"

    def llamar(instruccion: str) -> str:
        return cliente.responses.create(model=modelo, input=instruccion).output_text or ""

    return llamar
