"""Tablas curadas de la auditoría de asistentes a partir de lo crudo (spec 006)."""

from __future__ import annotations

import json
import random
from pathlib import Path

import pandas as pd

from radar import config
from radar.asistentes import citas, extractor, menciones, visibilidad
from radar.catalogo import Destino

SEMILLA_EJEMPLOS = 2026
MAX_FRAGMENTO = 600


def leer_corridas(carpeta: Path | None = None) -> list[dict]:
    carpeta = carpeta or config.ruta(config.CRUDO, "asistentes")
    corridas: dict[str, dict] = {}
    for ruta in sorted(carpeta.glob("*.jsonl")):
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if linea.strip():
                r = json.loads(linea)
                r["archivo_crudo"] = ruta.name
                corridas[r["corrida_id"]] = r
    return sorted(corridas.values(), key=lambda r: r["corrida_id"])


def fragmento(texto: str, maximo: int = MAX_FRAGMENTO) -> str:
    plano = " ".join(texto.split())
    if len(plano) <= maximo:
        return plano
    corte = plano[: maximo - 1].rsplit(" ", 1)[0]
    return corte + "…"


def elegir_ejemplos(corridas: list[dict], semilla: int = SEMILLA_EJEMPLOS) -> list[dict]:
    """Una respuesta por idioma, de OpenAI con búsqueda, elegida con semilla fija."""
    azar = random.Random(semilla)
    elegidos = []
    for idioma in sorted({c["idioma"] for c in corridas}):
        candidatas = [
            c
            for c in corridas
            if c["idioma"] == idioma and c["proveedor"] == "openai" and c["busco"]
        ]
        if candidatas:
            elegidos.append(azar.choice(candidatas))
    return elegidos


def procesar(
    corridas: list[dict],
    destinos: list[Destino],
    terminos_idiomas: dict[tuple[str, str], tuple[str, ...]],
    tipos: dict[str, str],
    cache_extractor: dict[str, dict],
) -> dict[str, pd.DataFrame]:
    menc_filas = []
    por_corrida: dict[str, set[str]] = {}
    lista_menciones: dict[str, list[menciones.Mencion]] = {}
    for c in corridas:
        extraidos = cache_extractor.get(c["corrida_id"], {}).get("destinos")
        ms = menciones.menciones_de_respuesta(
            c["texto"], c["idioma"], destinos, terminos_idiomas, extraidos
        )
        lista_menciones[c["corrida_id"]] = ms
        por_corrida[c["corrida_id"]] = {m.destino_id for m in ms}
        menc_filas += [
            {
                "corrida_id": c["corrida_id"],
                "destino_id": m.destino_id,
                "orden": m.orden,
                "metodo": m.metodo,
            }
            for m in ms
        ]

    citas_filas = []
    dominios_por_corrida: dict[str, list[str]] = {}
    for c in corridas:
        vistos: list[str] = []
        for cita in c.get("citas", []):
            dom = citas.dominio_de(cita["url"], cita.get("titulo", ""), cita.get("dominio", ""))
            citas_filas.append(
                {
                    "corrida_id": c["corrida_id"],
                    "url": cita["url"],
                    "dominio": dom,
                    "tipo_dominio": citas.tipo_de(dom, tipos),
                }
            )
            if dom and dom not in vistos:
                vistos.append(dom)
        dominios_por_corrida[c["corrida_id"]] = vistos

    corridas_tabla = pd.DataFrame(
        [
            {
                "corrida_id": c["corrida_id"],
                "prompt_id": c["prompt_id"],
                "brazo": c["brazo"],
                "proveedor": c["proveedor"],
                "modelo": c.get("modelo_servido") or c["modelo"],
                "idioma": c["idioma"],
                "mercado": c["mercado"],
                "tono": c["tono"],
                "con_busqueda": c["con_busqueda"],
                "busco": c["busco"],
                "repeticion": c["repeticion"],
                "fecha": c["fecha"],
                "sha256_respuesta": c["sha256_respuesta"],
                "archivo_crudo": c["archivo_crudo"],
                "tokens_entrada": c["tokens_entrada"],
                "tokens_salida": c["tokens_salida"],
            }
            for c in corridas
        ]
    )

    ids = [d.destino_id for d in destinos]
    vis = visibilidad.calcular(corridas, por_corrida, ids)

    ejemplos = pd.DataFrame(
        [
            {
                "corrida_id": c["corrida_id"],
                "idioma": c["idioma"],
                "proveedor": c["proveedor"],
                "prompt": c["prompt"],
                "fragmento": fragmento(c["texto"]),
                "destinos_mencionados": "|".join(
                    m.destino_id for m in lista_menciones[c["corrida_id"]]
                ),
                "dominios": "|".join(dominios_por_corrida[c["corrida_id"]]),
            }
            for c in elegir_ejemplos(corridas)
        ]
    )
    return {
        "asistentes_corridas": corridas_tabla,
        "asistentes_menciones": pd.DataFrame(
            menc_filas, columns=["corrida_id", "destino_id", "orden", "metodo"]
        ),
        "asistentes_citas": pd.DataFrame(
            citas_filas, columns=["corrida_id", "url", "dominio", "tipo_dominio"]
        ),
        "asistentes_visibilidad": vis,
        "asistentes_ejemplos": ejemplos,
    }


def ejecutar_y_escribir(destinos: list[Destino]) -> dict[str, pd.DataFrame]:
    from radar import catalogo

    corridas = leer_corridas()
    tablas = procesar(
        corridas,
        destinos,
        catalogo.cargar_terminos_idiomas(),
        citas.cargar_tipos(),
        extractor.cargar_cache(),
    )
    salida = config.ruta(config.CURADO)
    salida.mkdir(parents=True, exist_ok=True)
    for nombre, tabla in tablas.items():
        tabla.to_csv(salida / f"{nombre}.csv", index=False, float_format="%.4f")
    return tablas
