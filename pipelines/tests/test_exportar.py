"""Paquete de datos del sitio (T009-02): contratos, firma y determinismo."""

import json

import pytest

from radar.exportar import paquete


@pytest.fixture(scope="module")
def armado():
    return paquete.armar(generado="2026-10-16T00:00:00Z")


def test_el_paquete_cumple_los_contratos(armado):
    assert paquete.validar(armado) == []


def test_un_archivo_fuera_de_contrato_se_reporta(armado):
    roto = dict(armado)
    roto["destinos.json"] = {"generado": "2026-10-16T00:00:00Z", "destinos": [{}]}
    errores = paquete.validar(roto)
    assert errores and all(e.startswith("destinos.json") for e in errores)


def test_hay_una_ficha_por_pueblo_magico_y_la_capital(armado):
    fichas = {r for r in armado if r.startswith("fichas/")}
    assert len(fichas) == 13
    assert "fichas/puebla.json" in fichas


def test_el_contorno_del_estado_es_feature_collection(armado):
    estado = armado["geo/estado.json"]
    assert estado["type"] == "FeatureCollection" and estado["features"]


def test_la_evidencia_tiene_al_menos_cuatro_hallazgos(armado):
    assert len(armado["evidencia.json"]["hallazgos"]) >= 4


def test_la_capital_no_tiene_cuadrante(armado):
    assert armado["fichas/puebla.json"]["radar"]["cuadrante"] is None


def test_serializar_es_determinista_y_no_deja_nan(armado):
    a = paquete.serializar(armado["radar.json"])
    assert a == paquete.serializar(armado["radar.json"])
    assert b"NaN" not in a


def test_escribir_firma_cada_archivo(armado, tmp_path):
    destino = paquete.escribir(armado, tmp_path / "datos")
    manifiesto = json.loads((destino / "manifiesto.json").read_text(encoding="utf-8"))
    assert manifiesto["archivos"]
    for a in manifiesto["archivos"]:
        datos = (destino / a["ruta"]).read_bytes()
        assert paquete.sha256(datos) == a["sha256"] and len(datos) == a["bytes"]
