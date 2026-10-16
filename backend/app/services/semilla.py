"""Carga semilla idempotente del catálogo desde `data/`.

Lee el contrato de datos de la spec 012 (`poi.csv`, `poi_accesibilidad.csv`, `corredores.csv`),
el catálogo de destinos, el registro de fuentes y la serie oficial mensual.

Uso:
    uv run python -m app.services.semilla
    uv run python -m app.services.semilla --curado tests/datos   # fixture sintético de demo
"""

import argparse
import csv
import logging
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.config import ajustes
from app.models import (
    AggregateMetric,
    Corridor,
    DataLineage,
    DataSource,
    Destination,
    MetricDefinition,
    OpeningHours,
    POIAccessibilityAttribute,
    PointOfInterest,
)
from app.models.core import ATRIBUTOS_ACCESIBILIDAD, ESTADOS_ATRIBUTO, RANGOS_COSTO
from app.services import definiciones

registro = logging.getLogger("puebla_viva.semilla")

COLUMNAS_POI = (
    "poi_id, nombre, categoria, subcategoria, destino_id, corredor_id, municipio_cvegeo, lat, lon, "
    "direccion, horario_osm, costo_rango, descripcion, fuentes, osm_id, denue_id, sic_id, "
    "match_score, is_synthetic"
).split(", ")
COLUMNAS_ACCESIBILIDAD = (
    "poi_id, atributo, valor, origen, fecha, confianza, estado, evidencia".split(", ")
)
COLUMNAS_CORREDORES = "corredor_id, nombre, descripcion, lat_min, lon_min, lat_max, lon_max".split(
    ", "
)
VERSION_FORMULA_OFICIAL = "oficial-1"
LOTE = 2000


class ErrorSemilla(Exception):
    """Un archivo del contrato de datos no tiene la forma esperada."""


@dataclass
class Reporte:
    cargados: dict[str, int] = field(default_factory=dict)
    rechazados: list[str] = field(default_factory=list)
    omitidos: list[str] = field(default_factory=list)

    def resumen(self) -> str:
        lineas = [f"  {tabla}: {n}" for tabla, n in self.cargados.items()]
        if self.omitidos:
            lineas.append("Omitidos:")
            lineas += [f"  {o}" for o in self.omitidos]
        if self.rechazados:
            lineas.append(f"Filas rechazadas ({len(self.rechazados)}):")
            lineas += [f"  {r}" for r in self.rechazados[:50]]
        return "Carga semilla\n" + "\n".join(lineas)


# ---------------------------------------------------------------------------
# Lectura y conversión


def leer_csv(ruta: Path, columnas: Iterable[str]) -> list[dict[str, str]]:
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        faltan = [c for c in columnas if c not in (lector.fieldnames or [])]
        if faltan:
            raise ErrorSemilla(f"{ruta.name}: faltan columnas {', '.join(faltan)}")
        return [{k: (v or "").strip() for k, v in fila.items() if k} for fila in lector]


def texto(valor: str | None) -> str | None:
    return valor if valor else None


def booleano(valor: str | None) -> bool:
    return (valor or "").strip().lower() in {"true", "1", "si", "sí", "t", "yes"}


def flotante(valor: str | None) -> float | None:
    if valor is None or valor == "":
        return None
    return float(valor)


def fecha_iso(valor: str | None) -> date | None:
    if not valor:
        return None
    return date.fromisoformat(valor[:10])


def punto(lat: float, lon: float) -> str:
    return f"SRID=4326;POINT({lon} {lat})"


def lista_fuentes(valor: str | None) -> list[str]:
    if not valor:
        return []
    return [f.strip() for f in valor.replace(";", "|").split("|") if f.strip()]


def _upsert(sesion: Session, modelo, filas: list[dict], llaves: list[str], **extra) -> None:
    if not filas:
        return
    tabla = modelo.__table__
    for inicio in range(0, len(filas), LOTE):
        sentencia = insert(tabla)
        actualizar = {
            c.name: sentencia.excluded[c.name]
            for c in tabla.columns
            if c.name in filas[0] and c.name not in llaves
        }
        sentencia = sentencia.on_conflict_do_update(index_elements=llaves, set_=actualizar, **extra)
        sesion.execute(sentencia, filas[inicio : inicio + LOTE])


# ---------------------------------------------------------------------------
# Etapas


def cargar_fuentes(sesion: Session, ruta: Path, reporte: Reporte) -> None:
    if not ruta.exists():
        reporte.omitidos.append(f"{ruta} no existe")
        return
    filas = [
        {
            "fuente_id": f["fuente_id"],
            "nombre": f.get("titulo") or f["fuente_id"],
            "institucion": texto(f.get("institucion")),
            "tipo": texto(f.get("tipo")),
            "url": texto(f.get("url")),
            "licencia": texto(f.get("licencia")),
            "fecha_consulta": fecha_iso(f.get("fecha_consulta")),
            "sha256": texto(f.get("sha256")),
        }
        for f in leer_csv(ruta, ["fuente_id"])
    ]
    _upsert(sesion, DataSource, filas, ["fuente_id"])
    reporte.cargados["data_source"] = len(filas)


def asegurar_fuentes(sesion: Session, ids: set[str]) -> None:
    """Crea las fuentes citadas que no están en el registro, sin inventar URL."""
    if not ids:
        return
    existentes = set(sesion.scalars(select(DataSource.fuente_id)))
    nuevas = [{"fuente_id": i, "nombre": i} for i in sorted(ids - existentes)]
    if nuevas:
        sesion.execute(insert(DataSource.__table__).on_conflict_do_nothing(), nuevas)


def cargar_destinos(sesion: Session, ruta: Path, reporte: Reporte) -> None:
    filas = []
    for f in leer_csv(ruta, ["destino_id", "nombre", "lat", "lon"]):
        filas.append(
            {
                "destino_id": f["destino_id"],
                "nombre": f["nombre"],
                "tipo": texto(f.get("tipo")),
                "pueblo_magico": booleano(f.get("pueblo_magico")),
                "municipios_cvegeo": lista_fuentes(f.get("municipios_cvegeo")),
                "cabecera_cvegeo": texto(f.get("cabecera_cvegeo")),
                "zona": texto(f.get("zona")),
                "centro_ot": texto(f.get("centro_ot")),
                "altitud_m": flotante(f.get("altitud_m")),
                "geom": punto(float(f["lat"]), float(f["lon"])),
                "is_synthetic": booleano(f.get("is_synthetic")),
            }
        )
    _upsert(sesion, Destination, filas, ["destino_id"])
    reporte.cargados["destination"] = len(filas)


def cargar_corredores(sesion: Session, ruta: Path, reporte: Reporte) -> None:
    if not ruta.exists():
        reporte.omitidos.append(f"{ruta} no existe (spec 012)")
        return
    filas = []
    for f in leer_csv(ruta, COLUMNAS_CORREDORES):
        lat_min, lon_min = float(f["lat_min"]), float(f["lon_min"])
        lat_max, lon_max = float(f["lat_max"]), float(f["lon_max"])
        filas.append(
            {
                "corredor_id": f["corredor_id"],
                "nombre": f["nombre"],
                "descripcion": texto(f.get("descripcion")),
                "lat_min": lat_min,
                "lon_min": lon_min,
                "lat_max": lat_max,
                "lon_max": lon_max,
                "geom": (
                    f"SRID=4326;POLYGON(({lon_min} {lat_min},{lon_max} {lat_min},"
                    f"{lon_max} {lat_max},{lon_min} {lat_max},{lon_min} {lat_min}))"
                ),
                "is_synthetic": booleano(f.get("is_synthetic")),
            }
        )
    _upsert(sesion, Corridor, filas, ["corredor_id"])
    reporte.cargados["corridor"] = len(filas)


def cargar_pois(sesion: Session, ruta: Path, reporte: Reporte) -> dict[str, bool]:
    """Devuelve {poi_id: is_synthetic} de los POI cargados."""
    if not ruta.exists():
        reporte.omitidos.append(f"{ruta} no existe (spec 012)")
        return {}
    destinos = set(sesion.scalars(select(Destination.destino_id)))
    corredores = set(sesion.scalars(select(Corridor.corredor_id)))
    filas, horarios, linaje, citadas = [], [], [], set()
    vistos: set[str] = set()
    for n, f in enumerate(leer_csv(ruta, COLUMNAS_POI), start=2):
        poi_id = f["poi_id"]
        if not poi_id or poi_id in vistos:
            reporte.rechazados.append(f"poi.csv:{n} poi_id vacío o repetido ({poi_id})")
            continue
        if f["destino_id"] not in destinos:
            reporte.rechazados.append(f"poi.csv:{n} destino_id desconocido ({f['destino_id']})")
            continue
        try:
            lat, lon = float(f["lat"]), float(f["lon"])
            match_score = flotante(f["match_score"])
        except ValueError:
            reporte.rechazados.append(f"poi.csv:{n} lat, lon o match_score no numéricos")
            continue
        costo = (f["costo_rango"] or "").lower() or None
        if costo is not None and costo not in RANGOS_COSTO:
            reporte.rechazados.append(f"poi.csv:{n} costo_rango «{costo}» se guarda como nulo")
            costo = None
        corredor = f["corredor_id"] or None
        if corredor is not None and corredor not in corredores:
            reporte.rechazados.append(f"poi.csv:{n} corredor_id «{corredor}» se guarda como nulo")
            corredor = None
        fuentes = lista_fuentes(f["fuentes"])
        citadas.update(fuentes)
        vistos.add(poi_id)
        sintetica = booleano(f["is_synthetic"])
        filas.append(
            {
                "poi_id": poi_id,
                "nombre": f["nombre"],
                "categoria": f["categoria"] or "sin_categoria",
                "subcategoria": texto(f["subcategoria"]),
                "destino_id": f["destino_id"],
                "corredor_id": corredor,
                "municipio_cvegeo": texto(f["municipio_cvegeo"]),
                "geom": punto(lat, lon),
                "direccion": texto(f["direccion"]),
                "horario_osm": texto(f["horario_osm"]),
                "costo_rango": costo,
                "descripcion": texto(f["descripcion"]),
                "fuentes": fuentes,
                "osm_id": texto(f["osm_id"]),
                "denue_id": texto(f["denue_id"]),
                "sic_id": texto(f["sic_id"]),
                "match_score": match_score,
                "is_synthetic": sintetica,
            }
        )
        if f["horario_osm"]:
            horarios.append(
                {
                    "poi_id": poi_id,
                    "texto_osm": f["horario_osm"],
                    "origen": "poi.csv",
                    "is_synthetic": sintetica,
                }
            )
        linaje += [
            {"entidad": "point_of_interest", "entidad_id": poi_id, "fuente_id": fuente}
            for fuente in fuentes
        ]

    asegurar_fuentes(sesion, citadas)
    _upsert(sesion, PointOfInterest, filas, ["poi_id"])
    sesion.execute(delete(OpeningHours).where(OpeningHours.origen == "poi.csv"))
    if horarios:
        sesion.execute(insert(OpeningHours.__table__), horarios)
    sesion.execute(delete(DataLineage).where(DataLineage.entidad == "point_of_interest"))
    if linaje:
        sesion.execute(insert(DataLineage.__table__), linaje)
    reporte.cargados["point_of_interest"] = len(filas)
    reporte.cargados["opening_hours"] = len(horarios)
    return {f["poi_id"]: f["is_synthetic"] for f in filas}


def cargar_accesibilidad(
    sesion: Session, ruta: Path, pois: dict[str, bool], reporte: Reporte
) -> None:
    if not ruta.exists():
        reporte.omitidos.append(f"{ruta} no existe (spec 012)")
        return
    if not pois:
        pois = {
            p: s
            for p, s in sesion.execute(select(PointOfInterest.poi_id, PointOfInterest.is_synthetic))
        }
    filas: dict[tuple[str, str], dict] = {}
    for n, f in enumerate(leer_csv(ruta, COLUMNAS_ACCESIBILIDAD), start=2):
        donde = f"poi_accesibilidad.csv:{n}"
        if f["poi_id"] not in pois:
            reporte.rechazados.append(f"{donde} poi_id desconocido ({f['poi_id']})")
            continue
        if f["atributo"] not in ATRIBUTOS_ACCESIBILIDAD:
            reporte.rechazados.append(f"{donde} atributo desconocido ({f['atributo']})")
            continue
        if f["estado"] not in ESTADOS_ATRIBUTO:
            reporte.rechazados.append(f"{donde} estado desconocido ({f['estado']})")
            continue
        if not f["origen"] or not f["fecha"]:
            reporte.rechazados.append(f"{donde} sin origen o sin fecha (invariante de §13.2)")
            continue
        try:
            confianza = float(f["confianza"]) if f["confianza"] else 0.0
            fecha = fecha_iso(f["fecha"])
        except ValueError:
            reporte.rechazados.append(f"{donde} confianza o fecha inválidas")
            continue
        if not 0 <= confianza <= 1:
            reporte.rechazados.append(f"{donde} confianza fuera de [0, 1]")
            continue
        filas[(f["poi_id"], f["atributo"])] = {
            "poi_id": f["poi_id"],
            "atributo": f["atributo"],
            "valor": texto(f["valor"]),
            "origen": f["origen"],
            "fecha": fecha,
            "confianza": confianza,
            "estado": f["estado"],
            "evidencia": texto(f["evidencia"]),
            "is_synthetic": pois[f["poi_id"]],
        }
    tabla = POIAccessibilityAttribute.__table__
    # Lo que viene de moderación (origen comunidad) no lo pisa una recarga.
    _upsert(
        sesion,
        POIAccessibilityAttribute,
        list(filas.values()),
        ["poi_id", "atributo"],
        where=tabla.c.origen != "comunidad",
    )
    reporte.cargados["poi_accessibility_attribute"] = len(filas)


def cargar_indicadores(sesion: Session, ruta: Path, reporte: Reporte) -> None:
    if not ruta.exists():
        reporte.omitidos.append(f"{ruta} no existe")
        return
    columnas = ["indicador", "periodo", "valor", "unidad", "procedencia", "fuente_id"]
    datos = leer_csv(ruta, columnas)
    destinos = set(sesion.scalars(select(Destination.destino_id)))
    asegurar_fuentes(sesion, {f["fuente_id"] for f in datos if f["fuente_id"]})
    definiciones: dict[str, dict] = {}
    for f in datos:
        definiciones.setdefault(
            f["indicador"],
            {
                "metric_id": f["indicador"],
                "nombre": f["indicador"].replace("_", " "),
                "formula": "Valor publicado por la fuente",
                "version_formula": VERSION_FORMULA_OFICIAL,
                "unidad": texto(f["unidad"]),
                "procedencia": texto(f["procedencia"]),
                "fuente_id": texto(f["fuente_id"]),
            },
        )
    _upsert(sesion, MetricDefinition, list(definiciones.values()), ["metric_id"])
    calculado_en = datetime.now(UTC)
    filas: dict[tuple, dict] = {}
    for f in datos:
        destino = f.get("destino_id") or None
        llave = (f["indicador"], f.get("centro_ot") or None, f.get("nivel") or None, f["periodo"])
        filas[llave] = {
            "metric_id": f["indicador"],
            "destino_id": destino if destino in destinos else None,
            "centro_ot": llave[1],
            "nivel": llave[2],
            "periodo": f["periodo"],
            "valor": flotante(f["valor"]),
            "n": None,
            "suprimido": False,
            "procedencia": texto(f["procedencia"]),
            "version_formula": VERSION_FORMULA_OFICIAL,
            "calculado_en": calculado_en,
            "fuente_id": texto(f["fuente_id"]),
            "is_synthetic": False,
        }
    _upsert(
        sesion,
        AggregateMetric,
        list(filas.values()),
        ["metric_id", "centro_ot", "nivel", "periodo"],
    )
    reporte.cargados["metric_definition"] = len(definiciones)
    reporte.cargados["aggregate_metric"] = len(filas)


def cargar_definiciones(sesion: Session, reporte: Reporte) -> None:
    """Fichas de `metrics/definitions.yaml` (spec 019); van después de la serie oficial."""
    ruta = ajustes().archivo_metricas
    if not ruta.exists():
        reporte.omitidos.append(f"{ruta} no existe (spec 019)")
        return
    reporte.cargados["metric_definition (fichas)"] = definiciones.cargar(sesion, ruta)


def cargar(
    sesion: Session,
    datos: Path | None = None,
    curado: Path | None = None,
    indicadores: bool = True,
) -> Reporte:
    """Carga todo en una transacción. Devuelve el reporte de lo cargado y rechazado."""
    datos = datos or ajustes().directorio_datos
    curado = curado or datos / "curado"
    reporte = Reporte()
    cargar_fuentes(sesion, datos / "fuentes" / "fuentes.csv", reporte)
    cargar_destinos(sesion, datos / "referencia" / "destinos.csv", reporte)
    cargar_corredores(sesion, curado / "corredores.csv", reporte)
    pois = cargar_pois(sesion, curado / "poi.csv", reporte)
    cargar_accesibilidad(sesion, curado / "poi_accesibilidad.csv", pois, reporte)
    if indicadores:
        cargar_indicadores(sesion, datos / "curado" / "indicadores_oficiales_mensual.csv", reporte)
    cargar_definiciones(sesion, reporte)
    sesion.commit()
    return reporte


def main(argumentos: list[str] | None = None) -> int:
    lector = argparse.ArgumentParser(description="Carga semilla del catálogo desde data/.")
    lector.add_argument(
        "--datos", type=Path, help="Carpeta data/ (por omisión, la del repositorio)"
    )
    lector.add_argument(
        "--curado",
        type=Path,
        help="Carpeta con poi.csv, poi_accesibilidad.csv y corredores.csv (data/curado)",
    )
    lector.add_argument(
        "--sin-indicadores", action="store_true", help="No carga la serie oficial mensual"
    )
    args = lector.parse_args(argumentos)

    from app.db import SesionLocal

    try:
        with SesionLocal() as sesion:
            reporte = cargar(sesion, args.datos, args.curado, not args.sin_indicadores)
    except ErrorSemilla as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(reporte.resumen())
    return 0


if __name__ == "__main__":
    sys.exit(main())
