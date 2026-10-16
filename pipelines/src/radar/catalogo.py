"""Contexto Catálogo territorial: destinos, claves INEGI, coordenadas y términos de búsqueda.

El catálogo (`data/referencia/destinos.csv`) es el núcleo compartido del dominio: todos los
demás contextos identifican un lugar con `destino_id`.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from radar import config
from radar.texto import normalizar

TIPOS = {"pueblo_magico", "ciudad"}


@dataclass(frozen=True)
class Destino:
    destino_id: str
    nombre: str
    tipo: str
    pueblo_magico: bool
    municipios_cvegeo: tuple[str, ...]
    cabecera_cvegeo: str
    cabecera: str
    lat: float
    lon: float
    altitud_m: int
    zona: str
    centro_ot: str
    terminos_es: tuple[str, ...]
    terminos_en: tuple[str, ...]
    hashtags: tuple[str, ...]

    def terminos(self) -> tuple[str, ...]:
        """Todos los nombres con que se puede mencionar el destino."""
        vistos: list[str] = []
        for t in (self.nombre, *self.terminos_es, *self.terminos_en):
            if t and t not in vistos:
                vistos.append(t)
        return tuple(vistos)


def _lista(valor: str, separador: str = "|") -> tuple[str, ...]:
    return tuple(v.strip() for v in valor.split(separador) if v.strip())


def cargar(ruta: Path | None = None) -> list[Destino]:
    ruta = ruta or config.ruta(config.REFERENCIA, "destinos.csv")
    with ruta.open(encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    return [
        Destino(
            destino_id=r["destino_id"],
            nombre=r["nombre"],
            tipo=r["tipo"],
            pueblo_magico=r["pueblo_magico"].strip().lower() == "true",
            municipios_cvegeo=_lista(r["municipios_cvegeo"], ";"),
            cabecera_cvegeo=r["cabecera_cvegeo"],
            cabecera=r["cabecera"],
            lat=float(r["lat"]),
            lon=float(r["lon"]),
            altitud_m=int(r["altitud_m"]),
            zona=r["zona"],
            centro_ot=r["centro_ot"],
            terminos_es=_lista(r["terminos_es"]),
            terminos_en=_lista(r["terminos_en"]),
            hashtags=_lista(r["hashtags"]),
        )
        for r in filas
    ]


def validar(destinos: list[Destino]) -> list[str]:
    """Devuelve la lista de problemas encontrados; vacía si el catálogo es válido."""
    problemas: list[str] = []
    ids = [d.destino_id for d in destinos]
    if len(ids) != len(set(ids)):
        problemas.append("Hay destino_id repetidos")
    pm = [d for d in destinos if d.pueblo_magico]
    if len(pm) != 12:
        problemas.append(f"Se esperaban 12 Pueblos Mágicos y hay {len(pm)}")
    for d in destinos:
        if d.tipo not in TIPOS:
            problemas.append(f"{d.destino_id}: tipo desconocido {d.tipo!r}")
        if not (17.8 <= d.lat <= 20.9 and -99.1 <= d.lon <= -96.7):
            problemas.append(f"{d.destino_id}: coordenadas fuera de Puebla")
        for clave in d.municipios_cvegeo:
            if not (len(clave) == 5 and clave.startswith("21") and clave.isdigit()):
                problemas.append(f"{d.destino_id}: clave municipal inválida {clave!r}")
        if not d.cabecera_cvegeo.startswith(d.municipios_cvegeo[0]):
            problemas.append(f"{d.destino_id}: la cabecera no pertenece al primer municipio")
    centros = [normalizar(d.centro_ot) for d in destinos]
    if len(centros) != len(set(centros)):
        problemas.append("Hay centro_ot repetidos")
    return problemas


def por_centro_ot(destinos: list[Destino]) -> dict[str, Destino]:
    return {normalizar(d.centro_ot): d for d in destinos}
