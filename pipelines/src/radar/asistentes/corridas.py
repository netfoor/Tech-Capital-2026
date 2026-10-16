"""Plan y ejecución reanudable de las corridas de asistentes (spec 006).

Cada corrida es un prompt, un proveedor y una repetición. Se recorren en orden aleatorio con
semilla fija, de modo que si la ejecución se corta la muestra queda balanceada. Cada respuesta
se agrega como una línea al JSONL del día, y volver a correr no repite lo ya hecho.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import re
import time
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from radar import config
from radar.asistentes.proveedores import Proveedor, RespuestaAsistente

BRAZO_CONTROLADO = "controlado"
SEMILLA_POR_DEFECTO = 2026
REPETICIONES_POR_DEFECTO = 10
PAUSA_ENTRE_LLAMADAS = (1.0, 2.0)
TOKENS_ESTIMADOS = (1500, 500)  # entrada y salida por corrida, para el plan; se ajusta con lo real


@dataclass(frozen=True)
class Prompt:
    prompt_id: str
    idioma: str
    mercado: str
    tono: str
    texto: str


@dataclass(frozen=True)
class Corrida:
    prompt: Prompt
    proveedor: str
    repeticion: int

    def clave(self, modelo: str) -> tuple[str, str, str, int]:
        return (self.prompt.prompt_id, self.proveedor, modelo, self.repeticion)


def cargar_prompts(ruta: Path | None = None) -> list[Prompt]:
    ruta = ruta or config.ruta(config.REFERENCIA, "prompts.csv")
    with ruta.open(encoding="utf-8", newline="") as f:
        return [
            Prompt(r["prompt_id"], r["idioma"], r["mercado"], r["tono"], r["texto"])
            for r in csv.DictReader(f)
            if r["revisado"].strip().lower() == "true"
        ]


def corrida_id(prompt_id: str, proveedor: str, modelo: str, repeticion: int, fecha: str) -> str:
    base = f"{prompt_id}|{proveedor}|{modelo}|{repeticion}|{fecha}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]


def hechas(carpeta: Path) -> set[tuple[str, str, str, int]]:
    """(prompt_id, proveedor, modelo, repetición) de todas las líneas ya guardadas."""
    claves: set[tuple[str, str, str, int]] = set()
    for ruta in sorted(carpeta.glob("*.jsonl")):
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if not linea.strip():
                continue
            r = json.loads(linea)
            claves.add((r["prompt_id"], r["proveedor"], r["modelo"], r["repeticion"]))
    return claves


def plan(
    prompts: Iterable[Prompt],
    proveedores: dict[str, Proveedor],
    repeticiones: int = REPETICIONES_POR_DEFECTO,
    semilla: int = SEMILLA_POR_DEFECTO,
    carpeta: Path | None = None,
    idiomas: set[str] | None = None,
) -> tuple[list[Corrida], int]:
    """Corridas pendientes en orden aleatorio y total del plan (con lo ya hecho)."""
    carpeta = carpeta or config.ruta(config.CRUDO, "asistentes")
    completas = [
        Corrida(p, nombre, k)
        for p in prompts
        if idiomas is None or p.idioma in idiomas
        for nombre in sorted(proveedores)
        for k in range(1, repeticiones + 1)
    ]
    random.Random(semilla).shuffle(completas)
    hecho = hechas(carpeta) if carpeta.exists() else set()
    pendientes = [c for c in completas if c.clave(proveedores[c.proveedor].modelo) not in hecho]
    return pendientes, len(completas)


def estimar_tokens(n_corridas: int) -> tuple[int, int]:
    return n_corridas * TOKENS_ESTIMADOS[0], n_corridas * TOKENS_ESTIMADOS[1]


def _es_reintentable(error: Exception) -> bool:
    """Límite de tasa (429) o error del servidor (5xx)."""
    return re.search(r"\b(429|5\d\d)\b", str(error)) is not None


def consultar_con_reintentos(
    proveedor: Proveedor,
    texto: str,
    reintentos: int = 3,
    espera_base: float = 5.0,
    dormir: Callable[[float], None] = time.sleep,
) -> RespuestaAsistente:
    for intento in range(reintentos + 1):
        try:
            return proveedor.consultar(texto)
        except Exception as error:
            if intento == reintentos or not _es_reintentable(error):
                raise
            dormir(espera_base * 2**intento)
    raise RuntimeError("inalcanzable")  # pragma: no cover


def registro(corrida: Corrida, proveedor: Proveedor, respuesta: RespuestaAsistente, fecha: str):
    """Línea del JSONL: metadatos de la corrida y la respuesta completa."""
    modelo = respuesta.modelo or proveedor.modelo
    return {
        "corrida_id": corrida_id(
            corrida.prompt.prompt_id, corrida.proveedor, modelo, corrida.repeticion, fecha
        ),
        "prompt_id": corrida.prompt.prompt_id,
        "brazo": BRAZO_CONTROLADO,
        "proveedor": corrida.proveedor,
        "modelo": proveedor.modelo,
        "modelo_servido": modelo,
        "idioma": corrida.prompt.idioma,
        "mercado": corrida.prompt.mercado,
        "tono": corrida.prompt.tono,
        "con_busqueda": True,
        "busco": respuesta.busco,
        "repeticion": corrida.repeticion,
        "fecha": fecha,
        "prompt": corrida.prompt.texto,
        "texto": respuesta.texto,
        "citas": [
            {"url": c.url, "titulo": c.titulo, "dominio": c.dominio} for c in respuesta.citas
        ],
        "tokens_entrada": respuesta.tokens_entrada,
        "tokens_salida": respuesta.tokens_salida,
        "sha256_respuesta": hashlib.sha256(respuesta.texto.encode("utf-8")).hexdigest(),
        "crudo": respuesta.crudo,
    }


def ejecutar(
    pendientes: list[Corrida],
    proveedores: dict[str, Proveedor],
    carpeta: Path | None = None,
    tope: int | None = None,
    pausa: tuple[float, float] = PAUSA_ENTRE_LLAMADAS,
    dormir: Callable[[float], None] = time.sleep,
    hoy: Callable[[], date] = date.today,
    semilla: int = SEMILLA_POR_DEFECTO,
) -> Iterator[dict]:
    """Ejecuta las corridas, agrega cada respuesta al JSONL del día y la entrega a quien itera."""
    carpeta = carpeta or config.ruta(config.CRUDO, "asistentes")
    carpeta.mkdir(parents=True, exist_ok=True)
    espera = random.Random(semilla + 1)
    for n, corrida in enumerate(pendientes):
        if tope is not None and n >= tope:
            return
        proveedor = proveedores[corrida.proveedor]
        respuesta = consultar_con_reintentos(proveedor, corrida.prompt.texto, dormir=dormir)
        fecha = hoy().isoformat()
        linea = registro(corrida, proveedor, respuesta, fecha)
        with (carpeta / f"{fecha}.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(linea, ensure_ascii=False) + "\n")
        yield linea
        dormir(espera.uniform(*pausa))
