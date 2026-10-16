"""Registro de fuentes (`data/fuentes/fuentes.csv`) y verificación de huellas SHA-256."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

from radar import config


@dataclass(frozen=True)
class Fuente:
    fuente_id: str
    titulo: str
    institucion: str
    tipo: str
    url: str
    fecha_consulta: str
    archivo: str
    sha256: str
    uso_en_el_proyecto: str


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def cargar() -> dict[str, Fuente]:
    ruta = config.ruta(config.FUENTES, "fuentes.csv")
    with ruta.open(encoding="utf-8", newline="") as f:
        return {r["fuente_id"]: Fuente(**r) for r in csv.DictReader(f)}


def verificar() -> list[str]:
    """Comprueba que cada archivo registrado con huella exista y coincida."""
    problemas: list[str] = []
    for fuente in cargar().values():
        if not fuente.archivo or not fuente.sha256:
            continue
        archivo = config.ruta(fuente.archivo)
        if not archivo.exists():
            problemas.append(f"{fuente.fuente_id}: falta {fuente.archivo}")
            continue
        real = sha256(archivo)
        if real != fuente.sha256:
            problemas.append(f"{fuente.fuente_id}: la SHA-256 no coincide ({real[:12]}…)")
    return problemas


def archivo(fuente_id: str) -> Path:
    fuente = cargar()[fuente_id]
    if not fuente.archivo:
        raise ValueError(f"La fuente {fuente_id} no tiene archivo local")
    return config.ruta(fuente.archivo)
