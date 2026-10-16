"""Fichas semánticas de los indicadores (`backend/metrics/definitions.yaml`, spec 019).

Se cargan a `core.metric_definition` (lo que cabe en sus columnas) y a `core.data_lineage`
(una fila por fuente del indicador). La ficha completa se sirve desde el YAML versionado.
"""

from datetime import date
from functools import lru_cache
from pathlib import Path

import yaml
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.config import ajustes
from app.models import DataLineage, DataSource, MetricDefinition

CAMPOS_FICHA = (
    "id",
    "nombre",
    "modulo",
    "pregunta",
    "formula",
    "unidad",
    "numerador",
    "denominador",
    "filtros",
    "fuentes",
    "frecuencia",
    "cobertura",
    "limitaciones",
    "k_minimo",
    "decision_potencial",
    "procedencia",
    "version",
)
ENTIDAD = "metric_definition"


class ErrorDefiniciones(Exception):
    """El archivo de definiciones no tiene la forma esperada."""


def leer(ruta: Path | None = None) -> dict:
    ruta = ruta or ajustes().archivo_metricas
    with ruta.open(encoding="utf-8") as archivo:
        contenido = yaml.safe_load(archivo) or {}
    indicadores = contenido.get("indicadores") or []
    vistos: set[str] = set()
    for ficha in indicadores:
        faltan = [c for c in CAMPOS_FICHA if c not in ficha]
        if faltan:
            raise ErrorDefiniciones(f"{ficha.get('id', '?')}: faltan campos {', '.join(faltan)}")
        if ficha["id"] in vistos:
            raise ErrorDefiniciones(f"{ficha['id']}: indicador repetido")
        if ficha["procedencia"] not in ("medido", "derivado"):
            raise ErrorDefiniciones(f"{ficha['id']}: procedencia inválida")
        if not ficha["fuentes"]:
            raise ErrorDefiniciones(f"{ficha['id']}: sin fuentes (constitución III)")
        vistos.add(ficha["id"])
        ficha["version"] = str(ficha["version"])
    return contenido


@lru_cache
def fichas() -> dict[str, dict]:
    """{metric_id: ficha} del YAML. Vacío si el archivo no está (p. ej., en el contenedor)."""
    try:
        return {f["id"]: f for f in leer()["indicadores"]}
    except FileNotFoundError:
        return {}


def cargar(s: Session, ruta: Path | None = None) -> int:
    """Carga idempotente de fichas, fuentes propias y linaje. Devuelve cuántas fichas cargó."""
    contenido = leer(ruta)
    propias = contenido.get("fuentes_propias") or []
    if propias:
        sentencia = insert(DataSource.__table__)
        s.execute(
            sentencia.on_conflict_do_update(
                index_elements=["fuente_id"],
                set_={
                    "nombre": sentencia.excluded.nombre,
                    "institucion": sentencia.excluded.institucion,
                    "tipo": sentencia.excluded.tipo,
                },
            ),
            [
                {
                    "fuente_id": f["fuente_id"],
                    "nombre": f["nombre"],
                    "institucion": f.get("institucion"),
                    "tipo": f.get("tipo"),
                }
                for f in propias
            ],
        )
    existentes = set(s.scalars(select(DataSource.fuente_id)))
    indicadores = contenido["indicadores"]
    citadas = {fuente for f in indicadores for fuente in f["fuentes"]}
    faltan = sorted(citadas - existentes)
    if faltan:
        # Sin URL inventada: la fuente se crea con su identificador y se completa en fuentes.csv.
        s.execute(
            insert(DataSource.__table__).on_conflict_do_nothing(),
            [{"fuente_id": f, "nombre": f} for f in faltan],
        )

    filas = [
        {
            "metric_id": f["id"],
            "nombre": f["nombre"],
            "descripcion": f["pregunta"],
            "formula": f["formula"],
            "version_formula": f["version"],
            "unidad": f["unidad"],
            "denominador": f["denominador"],
            "procedencia": f["procedencia"],
            "fuente_id": f["fuentes"][0],
            "k_minimo": f["k_minimo"],
        }
        for f in indicadores
    ]
    sentencia = insert(MetricDefinition.__table__)
    s.execute(
        sentencia.on_conflict_do_update(
            index_elements=["metric_id"],
            set_={c: sentencia.excluded[c] for c in filas[0] if c != "metric_id"},
        ),
        filas,
    )
    s.execute(delete(DataLineage).where(DataLineage.entidad == ENTIDAD))
    hoy = date.today()
    s.execute(
        insert(DataLineage.__table__),
        [
            {
                "entidad": ENTIDAD,
                "entidad_id": f["id"],
                "fuente_id": fuente,
                "campo": f["unidad"],
                "metodo": f["formula"],
                "fecha": hoy,
            }
            for f in indicadores
            for fuente in f["fuentes"]
        ],
    )
    fichas.cache_clear()
    return len(filas)
