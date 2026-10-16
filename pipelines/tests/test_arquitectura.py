"""Ningún contexto importa a otro; solo pueden compartir los módulos del núcleo (ADR-0003)."""

import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1] / "src" / "radar"
COMPARTIDOS = {"catalogo", "config", "fuentes", "texto", "comun"}
CONTEXTOS = {
    "indicadores",
    "senales",
    "panel",
    "asistentes",
    "comentarios",
    "radar",
    "exportar",
    "entregables",
}


def contexto_de(ruta: Path) -> str | None:
    relativa = ruta.relative_to(RAIZ)
    primero = relativa.parts[0].removesuffix(".py")
    return primero if primero in CONTEXTOS else None


def contextos_importados(fuente: str) -> set[str]:
    arbol = ast.parse(fuente)
    encontrados: set[str] = set()
    for nodo in ast.walk(arbol):
        modulos: list[str] = []
        if isinstance(nodo, ast.Import):
            modulos = [a.name for a in nodo.names]
        elif isinstance(nodo, ast.ImportFrom) and nodo.module and nodo.level == 0:
            modulos = [nodo.module]
            if nodo.module == "radar":
                modulos += [f"radar.{a.name}" for a in nodo.names]
        for m in modulos:
            partes = m.split(".")
            if partes[0] == "radar" and len(partes) > 1 and partes[1] in CONTEXTOS:
                encontrados.add(partes[1])
    return encontrados


def violaciones(archivos: dict[Path, str]) -> list[str]:
    problemas = []
    for ruta, fuente in archivos.items():
        propio = contexto_de(ruta)
        if propio is None:
            continue
        for otro in contextos_importados(fuente) - {propio}:
            problemas.append(f"{ruta.relative_to(RAIZ)} importa el contexto {otro}")
    return problemas


def test_los_contextos_no_se_importan_entre_si():
    archivos = {p: p.read_text(encoding="utf-8") for p in RAIZ.rglob("*.py")}
    assert violaciones(archivos) == []


def test_el_nucleo_compartido_no_importa_contextos():
    for p in RAIZ.rglob("*.py"):
        if p.relative_to(RAIZ).parts[0].removesuffix(".py") in COMPARTIDOS:
            assert contextos_importados(p.read_text(encoding="utf-8")) == set(), p


@pytest.mark.parametrize(
    ("archivo", "fuente"),
    [
        ("asistentes/x.py", "from radar.panel import algo"),
        ("asistentes/x.py", "import radar.panel.consolidar"),
        ("senales/x.py", "from radar import indicadores"),
    ],
)
def test_detecta_una_importacion_prohibida(archivo, fuente):
    assert violaciones({RAIZ / archivo: fuente}) != []


def test_permite_importar_el_nucleo():
    fuente = "from radar import catalogo, config\nfrom radar.comun.estadistica import wilson"
    assert violaciones({RAIZ / "panel/x.py": fuente}) == []
