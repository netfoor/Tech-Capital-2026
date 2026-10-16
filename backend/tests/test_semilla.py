import shutil

import pytest
from sqlalchemy import func, select, update

from app.models import (
    AggregateMetric,
    Corridor,
    DataLineage,
    DataSource,
    Destination,
    MetricDefinition,
    OpeningHours,
    PointOfInterest,
    POIAccessibilityAttribute,
)
from app.services import semilla
from tests.utiles import DATOS_PRUEBA


def contar(sesion, modelo) -> int:
    return sesion.scalar(select(func.count()).select_from(modelo))


def test_carga_el_fixture_y_rechaza_atributos_sin_fecha(sesion):
    reporte = semilla.cargar(sesion, curado=DATOS_PRUEBA, indicadores=False)
    assert contar(sesion, Destination) == 18
    assert contar(sesion, Corridor) == 1
    assert contar(sesion, PointOfInterest) == 8
    assert contar(sesion, POIAccessibilityAttribute) == 12
    assert any("sin origen o sin fecha" in r for r in reporte.rechazados)
    # Todo el fixture es sintético (constitución XII), también los atributos heredados.
    assert sesion.scalar(select(func.bool_and(PointOfInterest.is_synthetic)))
    assert sesion.scalar(select(func.bool_and(POIAccessibilityAttribute.is_synthetic)))
    assert sesion.scalar(select(func.bool_and(Corridor.is_synthetic)))


def test_geometria_y_linaje(sesion):
    semilla.cargar(sesion, curado=DATOS_PRUEBA, indicadores=False)
    poi = sesion.get(PointOfInterest, "demo-cholula-museo")
    assert poi.lat == pytest.approx(19.0640)
    assert poi.lon == pytest.approx(-98.3050)
    assert poi.fuentes == ["osm-demo", "denue-demo"]
    # Las fuentes no registradas se crean con su id, sin inventar URL.
    fuente = sesion.get(DataSource, "osm-demo")
    assert fuente.nombre == "osm-demo" and fuente.url is None
    linaje = sesion.scalars(
        select(DataLineage.fuente_id).where(DataLineage.entidad_id == "demo-cholula-museo")
    ).all()
    assert sorted(linaje) == ["denue-demo", "osm-demo"]
    assert contar(sesion, OpeningHours) == 6
    destino = sesion.get(Destination, "cholula")
    assert destino.municipios_cvegeo == ["21140", "21119"]
    assert destino.pueblo_magico is True


def test_es_idempotente_y_respeta_lo_moderado(sesion):
    semilla.cargar(sesion, curado=DATOS_PRUEBA, indicadores=False)
    sesion.execute(
        update(POIAccessibilityAttribute)
        .where(
            POIAccessibilityAttribute.poi_id == "demo-cholula-zocalo",
            POIAccessibilityAttribute.atributo == "acceso_sin_escalones",
        )
        .values(valor="no", estado="reportado", origen="comunidad")
    )
    sesion.commit()
    semilla.cargar(sesion, curado=DATOS_PRUEBA, indicadores=False)
    assert contar(sesion, PointOfInterest) == 8
    assert contar(sesion, POIAccessibilityAttribute) == 12
    assert contar(sesion, OpeningHours) == 6
    atributo = sesion.scalar(
        select(POIAccessibilityAttribute).where(
            POIAccessibilityAttribute.poi_id == "demo-cholula-zocalo",
            POIAccessibilityAttribute.atributo == "acceso_sin_escalones",
        )
    )
    sesion.refresh(atributo)
    assert (atributo.valor, atributo.origen) == ("no", "comunidad")


def test_columna_faltante_falla_con_mensaje(sesion, tmp_path):
    for nombre in ("corredores.csv", "poi_accesibilidad.csv"):
        shutil.copy(DATOS_PRUEBA / nombre, tmp_path / nombre)
    lineas = (DATOS_PRUEBA / "poi.csv").read_text(encoding="utf-8").splitlines()
    encabezado = lineas[0].replace(",match_score", "")
    (tmp_path / "poi.csv").write_text(encabezado + "\n", encoding="utf-8")
    with pytest.raises(semilla.ErrorSemilla, match="match_score"):
        semilla.cargar(sesion, curado=tmp_path, indicadores=False)


def test_sin_archivos_de_012_carga_lo_demas(sesion, tmp_path):
    reporte = semilla.cargar(sesion, curado=tmp_path, indicadores=False)
    assert contar(sesion, Destination) == 18
    assert contar(sesion, PointOfInterest) == 0
    assert len(reporte.omitidos) == 3


def test_indicadores_oficiales_con_version_y_fecha(sesion, tmp_path):
    origen = semilla.ajustes().directorio_datos / "curado" / "indicadores_oficiales_mensual.csv"
    datos = tmp_path / "datos"
    for sub in ("curado", "referencia", "fuentes"):
        (datos / sub).mkdir(parents=True)
    lineas = origen.read_text(encoding="utf-8").splitlines()[:40]
    (datos / "curado" / "indicadores_oficiales_mensual.csv").write_text(
        "\n".join(lineas) + "\n", encoding="utf-8"
    )
    raiz = semilla.ajustes().directorio_datos
    shutil.copy(raiz / "referencia" / "destinos.csv", datos / "referencia" / "destinos.csv")
    shutil.copy(raiz / "fuentes" / "fuentes.csv", datos / "fuentes" / "fuentes.csv")
    semilla.cargar(sesion, datos=datos)
    semilla.cargar(sesion, datos=datos)
    assert contar(sesion, AggregateMetric) == 39
    assert contar(sesion, MetricDefinition) >= 1
    sin_version = sesion.scalar(
        select(func.count())
        .select_from(AggregateMetric)
        .where((AggregateMetric.version_formula.is_(None)) | AggregateMetric.calculado_en.is_(None))
    )
    assert sin_version == 0
