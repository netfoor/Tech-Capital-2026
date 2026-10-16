"""Lectura del catálogo con el contrato de la spec 012.

``poi.csv``: poi_id, nombre, categoria, subcategoria, destino_id, corredor_id,
municipio_cvegeo, lat, lon, direccion, horario_osm, costo_rango, descripcion,
fuentes, osm_id, denue_id, sic_id, match_score, is_synthetic. Columnas
opcionales que el cargador aprovecha si existen: ``popularidad`` y
``es_destino_alternativo``.

``poi_accesibilidad.csv``: poi_id, atributo, valor, origen, fecha, confianza,
estado, evidencia. Si hay varias filas por atributo, gana la más reciente
(un reporte de barrera posterior a una verificación la sustituye).
"""

from __future__ import annotations

import csv
from pathlib import Path

from .config import POLOS_SATURADOS
from .tipos import AtributoAcc, POICandidato

# Alias de OSM a los nombres del recomendador.
ALIAS_ATRIBUTOS = {
    "wheelchair": "acceso_sin_escalones",
    "toilets:wheelchair": "banio_accesible",
    "incline": "pendiente_pct",
    "bench": "asientos_descanso",
}
ALIAS_VALORES = {"yes": "si", "designated": "si", "limited": "limitado"}


def _verdadero(texto: str | None) -> bool:
    return (texto or "").strip().lower() in {"true", "1", "si", "sí", "yes"}


def _flotante(texto: str | None, defecto: float) -> float:
    try:
        return float(texto) if texto not in (None, "") else defecto
    except ValueError:
        return defecto


def cargar_accesibilidad(ruta: Path) -> dict[str, dict[str, AtributoAcc]]:
    filas: dict[tuple[str, str], tuple[str, float, AtributoAcc]] = {}
    with ruta.open(encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            atributo = ALIAS_ATRIBUTOS.get(fila["atributo"], fila["atributo"])
            valor = (fila.get("valor") or "").strip()
            valor = ALIAS_VALORES.get(valor.lower(), valor)
            attr = AtributoAcc(
                valor=valor,
                estado=(fila.get("estado") or "sin_verificar").strip(),
                origen=(fila.get("origen") or "").strip(),
                confianza=_flotante(fila.get("confianza"), 0.0),
            )
            clave = (fila["poi_id"], atributo)
            orden = (fila.get("fecha") or "", attr.confianza)
            previo = filas.get(clave)
            if previo is None or orden >= previo[:2]:
                filas[clave] = (orden[0], orden[1], attr)
    salida: dict[str, dict[str, AtributoAcc]] = {}
    for (pid, atributo), (_, _, attr) in sorted(filas.items()):
        salida.setdefault(pid, {})[atributo] = attr
    return salida


def cargar_catalogo(ruta_poi: Path, ruta_accesibilidad: Path | None = None) -> list[POICandidato]:
    acc = cargar_accesibilidad(ruta_accesibilidad) if ruta_accesibilidad else {}
    pois: list[POICandidato] = []
    with ruta_poi.open(encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            destino = (fila.get("destino_id") or "").strip() or None
            polo = destino in POLOS_SATURADOS
            alternativo = fila.get("es_destino_alternativo")
            pois.append(
                POICandidato(
                    poi_id=fila["poi_id"],
                    nombre=fila["nombre"],
                    categoria=(fila.get("categoria") or "").strip().lower(),
                    subcategoria=(fila.get("subcategoria") or "").strip() or None,
                    destino_id=destino,
                    corredor_id=(fila.get("corredor_id") or "").strip() or None,
                    lat=float(fila["lat"]),
                    lon=float(fila["lon"]),
                    costo_rango=(fila.get("costo_rango") or "").strip().lower() or None,
                    horario_osm=(fila.get("horario_osm") or "").strip() or None,
                    descripcion=fila.get("descripcion") or "",
                    accesibilidad=acc.get(fila["poi_id"], {}),
                    es_destino_alternativo=(
                        _verdadero(alternativo) if alternativo not in (None, "") else not polo
                    ),
                    popularidad=_flotante(fila.get("popularidad"), 0.8 if polo else 0.3),
                    is_synthetic=_verdadero(fila.get("is_synthetic")),
                )
            )
    return sorted(pois, key=lambda p: p.poi_id)
