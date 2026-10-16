"""Contexto Catálogo territorial: destinos, claves INEGI, coordenadas y términos de búsqueda.

El catálogo (`data/referencia/destinos.csv`) es el núcleo compartido del dominio: todos los
demás contextos identifican un lugar con `destino_id`.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from radar import config
from radar.texto import normalizar

TIPOS = {"pueblo_magico", "ciudad"}
IDIOMAS = ("es", "en", "fr", "ko", "zh")
IDIOMAS_NO_LATINOS = ("ko", "zh")


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


@dataclass(frozen=True)
class Mencion:
    """Un destino mencionado en un texto, con el término hallado y su posición."""

    destino_id: str
    termino: str
    posicion: int


def cargar_terminos_idiomas(ruta: Path | None = None) -> dict[tuple[str, str], tuple[str, ...]]:
    """Términos verificados por (destino_id, idioma); los no verificados no se usan."""
    ruta = ruta or config.ruta(config.REFERENCIA, "terminos_idiomas.csv")
    if not ruta.exists():
        return {}
    acumulado: dict[tuple[str, str], list[str]] = {}
    with ruta.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["verificado"].strip().lower() != "true":
                continue
            for t in _lista(r["termino"]):
                acumulado.setdefault((r["destino_id"], r["idioma"]), []).append(t)
    return {k: tuple(v) for k, v in acumulado.items()}


def _terminos_latinos(d: Destino, extra: dict[tuple[str, str], tuple[str, ...]]) -> list[str]:
    todos = [d.nombre, d.cabecera, *d.terminos_es, *d.terminos_en]
    for idioma in ("es", "en", "fr"):
        todos.extend(extra.get((d.destino_id, idioma), ()))
    # Un texto en ko o zh también puede escribir el nombre en alfabeto latino.
    return [t for t in todos if normalizar(t)]


def _sin_traslapes(
    candidatos: list[tuple[int, int, str, str]],
) -> list[tuple[int, int, str, str]]:
    aceptados: list[tuple[int, int, str, str]] = []
    for c in sorted(candidatos, key=lambda c: (-(c[1] - c[0]), c[0])):
        if all(c[1] <= a[0] or c[0] >= a[1] for a in aceptados):
            aceptados.append(c)
    return aceptados


def detectar(
    texto: str,
    idioma: str,
    destinos: list[Destino] | None = None,
    terminos_idiomas: dict[tuple[str, str], tuple[str, ...]] | None = None,
) -> list[Mencion]:
    """Destinos mencionados en `texto`, uno por destino y en orden de aparición.

    - Alfabeto latino: se normaliza, se busca con límites de palabra y, si un término
      contiene a otro en la misma posición, gana el más largo. «Puebla» sola no cuenta.
    - ko y zh: subcadena exacta de los términos verificados de ese idioma.
    """
    if idioma not in IDIOMAS:
        raise ValueError(f"Idioma no soportado: {idioma!r}")
    destinos = destinos if destinos is not None else cargar()
    extra = terminos_idiomas if terminos_idiomas is not None else cargar_terminos_idiomas()

    latinos: list[tuple[int, int, str, str]] = []  # (inicio, fin, destino_id, término)
    base = normalizar(texto)
    for d in destinos:
        for t in _terminos_latinos(d, extra):
            n = normalizar(t)
            patron = rf"(?<![a-z0-9ñ]){re.escape(n)}(?![a-z0-9ñ])"
            for m in re.finditer(patron, base):
                latinos.append((m.start(), m.end(), d.destino_id, t))

    no_latinos: list[tuple[int, int, str, str]] = []
    if idioma in IDIOMAS_NO_LATINOS:
        plano = unicodedata.normalize("NFKC", texto)
        for d in destinos:
            for t in extra.get((d.destino_id, idioma), ()):
                n = unicodedata.normalize("NFKC", t)
                inicio = plano.find(n)
                while inicio != -1:
                    no_latinos.append((inicio, inicio + len(n), d.destino_id, t))
                    inicio = plano.find(n, inicio + 1)

    # El más largo gana cuando dos términos se traslapan (cada alfabeto en su propio texto).
    aceptados = _sin_traslapes(latinos) + _sin_traslapes(no_latinos)

    vistos: set[str] = set()
    menciones: list[Mencion] = []
    for inicio, _fin, destino_id, termino in sorted(aceptados):
        if destino_id in vistos:
            continue
        vistos.add(destino_id)
        menciones.append(Mencion(destino_id, termino, inicio))
    return menciones
