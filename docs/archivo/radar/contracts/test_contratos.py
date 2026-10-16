"""Los contratos del sitio son esquemas válidos, se resuelven entre sí y no exponen identidad."""

import json

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from radar.config import CONTRATOS, ruta

PROHIBIDOS = {"usuario", "autor", "nombre_participante", "texto_comentario", "correo", "telefono"}


def _esquemas() -> dict[str, dict]:
    archivos = ruta(CONTRATOS).glob("*.schema.json")
    return {p.name: json.loads(p.read_text(encoding="utf-8")) for p in archivos}


def _registro(esquemas: dict[str, dict]) -> Registry:
    return Registry().with_resources(
        (nombre, Resource.from_contents(esquema)) for nombre, esquema in esquemas.items()
    )


def _recorrer(nodo, clave: str):
    if isinstance(nodo, dict):
        for k, v in nodo.items():
            if k == clave:
                yield v
            yield from _recorrer(v, clave)
    elif isinstance(nodo, list):
        for v in nodo:
            yield from _recorrer(v, clave)


ESQUEMAS = _esquemas()


def test_hay_contratos():
    esperados = {
        "comun",
        "manifiesto",
        "destinos",
        "geo",
        "radar",
        "evidencia",
        "metodo",
        "ficha",
        "asistentes",
        "redes",
    }
    assert {n.removesuffix(".schema.json") for n in ESQUEMAS} == esperados


@pytest.mark.parametrize("nombre", sorted(ESQUEMAS))
def test_esquema_valido(nombre):
    esquema = ESQUEMAS[nombre]
    Draft202012Validator.check_schema(esquema)
    assert esquema["$id"] == nombre


@pytest.mark.parametrize("nombre", sorted(ESQUEMAS))
def test_referencias_resueltas(nombre):
    resolver = _registro(ESQUEMAS).resolver(base_uri=nombre)
    for ref in _recorrer(ESQUEMAS[nombre], "$ref"):
        resolver.lookup(ref)


@pytest.mark.parametrize("nombre", sorted(ESQUEMAS))
def test_sin_campos_de_identidad(nombre):
    campos = set()
    for propiedades in _recorrer(ESQUEMAS[nombre], "properties"):
        campos.update(propiedades)
    assert not campos & PROHIBIDOS


def test_radar_acepta_primera_version_solo_con_desempeno():
    fila = {
        "destino_id": "cuetzalan",
        "ocupacion_12m": 30.0,
        "cuartos_libres_dia_12m": 300.0,
        "llegadas_12m": 50000,
        "crecimiento_llegadas_pct": None,
        "componentes": {},
        "indice_atencion": None,
        "indice_desempeno": 9.1,
        "brecha": None,
        "cuadrante": None,
        "sensible": False,
        "notas": ["Sin componentes de atención todavía"],
    }
    instancia = {
        "generado": "2026-10-16T10:00:00-06:00",
        "periodo_ref": {"desde": "2025-07", "hasta": "2026-06"},
        "cortes": {"atencion": 50, "desempeno": 50},
        "componentes_disponibles": [],
        "destinos": [fila] * 12,
        "referencia": {**fila, "destino_id": "puebla", "indice_desempeno": None},
    }
    validador = Draft202012Validator(ESQUEMAS["radar.schema.json"], registry=_registro(ESQUEMAS))
    assert not list(validador.iter_errors(instancia))

    instancia["destinos"] = [{**fila, "cuadrante": "otro"}] * 12
    assert list(validador.iter_errors(instancia))
