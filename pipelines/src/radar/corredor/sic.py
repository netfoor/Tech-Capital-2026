"""Sistema de Información Cultural (SIC) de la Secretaría de Cultura: directorios abiertos.

Crédito sugerido por el SIC: «"Directorio de <tabla>", publicado por el Sistema de
Información Cultural/Secretaría de Cultura. Consultado en <url> el <fecha>».
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass

FUENTE_ID = "sic-cultura"
URL = "https://sic.cultura.gob.mx/opendata/d/0_{tabla}_directorio.csv"
ESTADO_PUEBLA = "21"

# tabla del SIC → (categoria, subcategoria) del contrato
TABLAS = {
    "museo": ("museo", "museo"),
    "zona_arqueologica": ("zona_arqueologica", "zona_arqueologica"),
    "centro_cultural": ("centro_cultural", "centro_cultural"),
    "teatro": ("centro_cultural", "teatro"),
    "galeria": ("centro_cultural", "galeria"),
    "casa_artesania": ("artesanias", "casa_artesania"),
}


@dataclass(frozen=True)
class Recinto:
    tabla: str
    id: str
    nombre: str
    municipio_cvegeo: str
    lat: float | None
    lon: float | None
    direccion: str
    descripcion: str

    @property
    def sic_id(self) -> str:
        return f"{self.tabla}-{self.id}"

    @property
    def poi_id(self) -> str:
        return f"sic-{self.sic_id}"


def decodificar(contenido: bytes) -> str:
    try:
        return contenido.decode("utf-8-sig")
    except UnicodeDecodeError:
        return contenido.decode("latin-1")


CONTACTO = ("telefono", "telfono", "email", "facebook", "twitter", "instagram")


def filtrar_puebla(contenido: bytes) -> bytes:
    """Filas con `estado_id=21`, con el texto de la fuente y sin columnas de contacto."""
    texto = decodificar(contenido)
    lector = csv.reader(io.StringIO(texto))
    encabezado = next(lector)
    i = encabezado.index("estado_id")
    conservar = [j for j, c in enumerate(encabezado) if not any(x in c for x in CONTACTO)]
    salida = io.StringIO()
    escritor = csv.writer(salida, lineterminator="\n")
    escritor.writerow([encabezado[j] for j in conservar])
    for fila in lector:
        if len(fila) > i and fila[i].strip() == ESTADO_PUEBLA:
            escritor.writerow([fila[j] if j < len(fila) else "" for j in conservar])
    return salida.getvalue().encode("utf-8")


def _limpio(valor: str) -> str:
    return " ".join(valor.replace("<br>", " ").replace("<br/>", " ").split())


def _coordenada(valor: str) -> float | None:
    try:
        x = float(valor)
    except (TypeError, ValueError):
        return None
    return x if x != 0 else None


def leer(tabla: str, texto: str) -> list[Recinto]:
    recintos = []
    for r in csv.DictReader(io.StringIO(texto)):
        if r.get("estado_id", "").strip() != ESTADO_PUEBLA:
            continue
        mun = r.get("municipio_id", "").strip()
        calle = _limpio(r.get(f"{tabla}_calle_numero", ""))
        colonia = _limpio(r.get(f"{tabla}_colonia", ""))
        tematica = _limpio(r.get(f"{tabla}_tematica_n1", ""))
        recintos.append(
            Recinto(
                tabla=tabla,
                id=r[f"{tabla}_id"].strip(),
                nombre=_limpio(r[f"{tabla}_nombre"]),
                municipio_cvegeo=f"21{int(mun):03d}" if mun.isdigit() else "",
                lat=_coordenada(r.get("gmaps_latitud", "")),
                lon=_coordenada(r.get("gmaps_longitud", "")),
                direccion=", ".join(p for p in (calle, colonia) if p),
                descripcion=f"Temática: {tematica}" if tematica else "",
            )
        )
    return recintos
