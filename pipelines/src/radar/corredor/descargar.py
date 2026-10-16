"""Etapa con red: Overpass, SIC y DENUE.

Lo crudo se guarda en `data/crudo/corredor/AAAA-MM-DD/` (no se versiona). Los extractos que
consume `integrar` van a `data/fuentes/corredor/<fuente>/` con un `manifiesto.csv` por fuente
(archivo, URL, fecha, SHA-256 del extracto y del original). El manifiesto se registra en
`data/fuentes/fuentes.csv`.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

from radar import config, fuentes
from radar.corredor import denue, osm, sic, zonas

CAMPOS_MANIFIESTO = ["archivo", "url", "fecha_consulta", "sha256", "bytes", "sha256_original"]
PAUSA_OVERPASS_S = 10.0


@dataclass(frozen=True)
class Entrada:
    archivo: str  # relativo a la raíz del repositorio
    url: str
    fecha_consulta: str
    sha256: str
    bytes: int
    sha256_original: str


def hoy() -> str:
    return dt.date.today().isoformat()


def carpeta_crudo(fecha: str) -> Path:
    return config.ruta(config.CRUDO, "corredor", fecha)


def carpeta_extractos(fuente: str) -> Path:
    return config.ruta(config.FUENTES, "corredor", fuente)


def _relativa(ruta: Path) -> str:
    return ruta.resolve().relative_to(config.raiz()).as_posix()


def _entrada(extracto: Path, url: str, fecha: str, original: Path | None = None) -> Entrada:
    return Entrada(
        archivo=_relativa(extracto),
        url=url,
        fecha_consulta=fecha,
        sha256=fuentes.sha256(extracto),
        bytes=extracto.stat().st_size,
        sha256_original=fuentes.sha256(original) if original else fuentes.sha256(extracto),
    )


def leer_manifiesto(fuente: str) -> dict[str, Entrada]:
    ruta = carpeta_extractos(fuente) / "manifiesto.csv"
    if not ruta.exists():
        return {}
    with ruta.open(encoding="utf-8", newline="") as f:
        return {r["archivo"]: Entrada(**{**r, "bytes": int(r["bytes"])}) for r in csv.DictReader(f)}


def escribir_manifiesto(fuente: str, entradas: dict[str, Entrada]) -> Path:
    ruta = carpeta_extractos(fuente) / "manifiesto.csv"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_MANIFIESTO, lineterminator="\n")
        w.writeheader()
        for clave in sorted(entradas):
            w.writerow(asdict(entradas[clave]))
    return ruta


def verificar_manifiesto(fuente: str) -> list[str]:
    problemas = []
    for e in leer_manifiesto(fuente).values():
        ruta = config.ruta(e.archivo)
        if not ruta.exists():
            problemas.append(f"{fuente}: falta {e.archivo}")
        elif fuentes.sha256(ruta) != e.sha256:
            problemas.append(f"{fuente}: la SHA-256 de {e.archivo} no coincide")
    return problemas


def registrar_fuente(fuente_id: str, titulo: str, institucion: str, url: str, uso: str) -> None:
    """Agrega o actualiza la fila de la fuente en `fuentes.csv` con la huella del manifiesto."""
    nombre = {"osm-overpass": "osm", "sic-cultura": "sic", "inegi-denue": "denue"}[fuente_id]
    manifiesto = carpeta_extractos(nombre) / "manifiesto.csv"
    ruta = config.ruta(config.FUENTES, "fuentes.csv")
    with ruta.open(encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        campos = list(lector.fieldnames or [])
        filas = list(lector)
    nueva = {
        "fuente_id": fuente_id,
        "titulo": titulo,
        "institucion": institucion,
        "tipo": "oficial" if fuente_id != "osm-overpass" else "abierta",
        "url": url,
        "fecha_consulta": hoy(),
        "archivo": _relativa(manifiesto),
        "sha256": fuentes.sha256(manifiesto),
        "uso_en_el_proyecto": uso,
    }
    filas = [r for r in filas if r["fuente_id"] != fuente_id] + [nueva]
    with ruta.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, lineterminator="\n")
        w.writeheader()
        w.writerows(filas)


def descargar_osm(fecha: str, avisar: Callable[[str], None] = print, rehacer: bool = False) -> None:
    crudo = carpeta_crudo(fecha) / "osm"
    crudo.mkdir(parents=True, exist_ok=True)
    destino = carpeta_extractos("osm")
    destino.mkdir(parents=True, exist_ok=True)
    entradas = leer_manifiesto("osm")
    consultas = [
        (zonas.CORREDOR_ID, osm.consulta_corredor(zonas.CORREDOR, zonas.centros_corredor()))
    ]
    consultas += [(c.zona_id, osm.consulta_centro(c)) for c in zonas.centros_pueblos_magicos()]
    fallidas: list[str] = []
    for i, (zona, consulta) in enumerate(consultas):
        archivo_crudo = crudo / f"{zona}.json"
        if archivo_crudo.exists() and not rehacer:
            avisar(f"  OSM {zona}: ya descargado hoy")
        else:
            if i:
                time.sleep(PAUSA_OVERPASS_S)
            try:
                cuerpo, url = osm.consultar(consulta)
            except RuntimeError as error:  # se sigue con las demás zonas
                avisar(f"  OSM {zona}: {error}")
                fallidas.append(zona)
                continue
            archivo_crudo.write_bytes(cuerpo)
            (crudo / f"{zona}.overpassql").write_text(consulta, encoding="utf-8")
            (crudo / f"{zona}.url").write_text(url, encoding="utf-8")
            avisar(f"  OSM {zona}: {len(cuerpo):,} bytes de {url}")
        archivo_url = crudo / f"{zona}.url"
        url = archivo_url.read_text(encoding="utf-8") if archivo_url.exists() else osm.SERVIDORES[0]
        compacto = osm.compactar(json.loads(archivo_crudo.read_bytes()), consulta)
        extracto = destino / f"{zona}.json"
        extracto.write_text(
            json.dumps(compacto, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        e = _entrada(extracto, url, fecha, archivo_crudo)
        entradas[e.archivo] = e
        escribir_manifiesto("osm", entradas)
    registrar_fuente(
        "osm-overpass",
        "OpenStreetMap: POI turísticos y etiquetas de accesibilidad (Overpass API)",
        "OpenStreetMap contributors (ODbL 1.0)",
        "https://overpass-api.de/",
        "POI del corredor Puebla–Cholula y de los centros de los Pueblos Mágicos; "
        "etiquetas wheelchair; toilets:wheelchair; ramp; step_count; incline; surface",
    )
    if fallidas:
        raise RuntimeError(f"Overpass no respondió para: {', '.join(fallidas)}")


def descargar_sic(fecha: str, avisar: Callable[[str], None] = print) -> None:
    import httpx

    crudo = carpeta_crudo(fecha) / "sic"
    crudo.mkdir(parents=True, exist_ok=True)
    destino = carpeta_extractos("sic")
    destino.mkdir(parents=True, exist_ok=True)
    entradas = leer_manifiesto("sic")
    for tabla in sic.TABLAS:
        url = sic.URL.format(tabla=tabla)
        original = crudo / f"{tabla}.csv"
        if not original.exists():
            r = httpx.get(
                url, timeout=180, follow_redirects=True, headers={"User-Agent": osm.AGENTE}
            )
            r.raise_for_status()
            original.write_bytes(r.content)
            time.sleep(2)
        contenido = original.read_bytes()
        extracto = destino / f"{tabla}_puebla.csv"
        extracto.write_bytes(sic.filtrar_puebla(contenido))
        e = _entrada(extracto, url, fecha, original)
        entradas[e.archivo] = e
        avisar(f"  SIC {tabla}: {len(contenido):,} bytes; extracto de Puebla {e.bytes:,} bytes")
    escribir_manifiesto("sic", entradas)
    registrar_fuente(
        "sic-cultura",
        "Sistema de Información Cultural: directorios de museos; zonas arqueológicas; "
        "centros culturales; teatros; galerías y casas de artesanías",
        "Secretaría de Cultura",
        "https://sic.cultura.gob.mx/datos.php",
        "Recintos culturales del estado de Puebla (estado_id=21) con ubicación",
    )


def descargar_denue(fecha: str, avisar: Callable[[str], None] = print) -> None:
    import httpx

    crudo = carpeta_crudo(fecha) / "denue"
    crudo.mkdir(parents=True, exist_ok=True)
    original = crudo / "denue_21_csv.zip"
    if not original.exists():
        with httpx.stream(
            "GET", denue.URL, timeout=900, follow_redirects=True, headers={"User-Agent": osm.AGENTE}
        ) as r:
            r.raise_for_status()
            with original.open("wb") as f:
                for bloque in r.iter_bytes():
                    f.write(bloque)
    avisar(f"  DENUE: {original.stat().st_size:,} bytes")
    tabla = denue.filtrar_zip(original)
    estatal, en_zonas = denue.partir(tabla, zonas.en_alguna_zona)
    destino = carpeta_extractos("denue")
    destino.mkdir(parents=True, exist_ok=True)
    for viejo in destino.glob("*.csv"):
        viejo.unlink()
    entradas = {}
    for nombre, parte in (("estatal", estatal), ("zonas", en_zonas)):
        extracto = destino / f"denue_21_turismo_{nombre}.csv"
        parte.to_csv(extracto, index=False, lineterminator="\n")
        e = _entrada(extracto, denue.URL, fecha, original)
        entradas[e.archivo] = e
    escribir_manifiesto("denue", entradas)
    avisar(
        f"  DENUE: {len(tabla):,} establecimientos de SCIAN {', '.join(denue.RAMAS)}; "
        f"{len(en_zonas):,} en las zonas de consulta"
    )
    registrar_fuente(
        "inegi-denue",
        "Directorio Estadístico Nacional de Unidades Económicas; descarga masiva de Puebla "
        "(extracto SCIAN 7211; 7225; 7121; 5615)",
        "INEGI",
        denue.URL,
        "Oferta turística por municipio y enlace con OSM; alojamiento y museos como POI",
    )
