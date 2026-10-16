"""Componentes de atención: valor bruto, n y percentil de cada destino.

Cada componente sale de una tabla curada de otro contexto. Si la tabla no existe, el
componente no está disponible y no se imputa nada (FR-008-02).
"""

from __future__ import annotations

import pandas as pd

from radar import config
from radar.comun.estadistica import percentiles

COMPONENTES = ("busqueda", "video", "panel", "asistentes")

TABLAS = {
    "busqueda": "interes_busqueda_mensual.csv",
    "video": "presencia_youtube.csv",
    "panel": "presencia_panel.csv",
    "asistentes": "asistentes_visibilidad.csv",
}

SEGMENTO_ASISTENTES = "brazo=controlado"
SEGMENTO_ASISTENTES_RESPALDO = "total"


def cargar_tablas(carpeta=None) -> dict[str, pd.DataFrame]:
    """Tablas que existen en `data/curado/`; las ausentes simplemente no aparecen."""
    base = carpeta if carpeta is not None else config.ruta(config.CURADO)
    tablas: dict[str, pd.DataFrame] = {}
    for componente, archivo in TABLAS.items():
        ruta = base / archivo
        if ruta.exists():
            tablas[componente] = pd.read_csv(ruta)
    return tablas


def _bruto_busqueda(tabla: pd.DataFrame, desde: str, hasta: str) -> dict[str, tuple[float, int]]:
    t = tabla
    if "geo" in t.columns:
        t = t[t["geo"] == "MX"]
    t = t[(t["periodo"] >= desde) & (t["periodo"] <= hasta)].dropna(subset=["interes_ajustado"])
    resumen = t.groupby("destino_id")["interes_ajustado"].agg(["mean", "count"])
    return {d: (float(r["mean"]), int(r["count"])) for d, r in resumen.iterrows()}


def _bruto_video(tabla: pd.DataFrame) -> dict[str, tuple[float, int]]:
    resumen = tabla.groupby("destino_id")[["k_menciones", "n_resultados"]].sum()
    return {
        d: (float(r["k_menciones"] / r["n_resultados"] * 100), int(r["n_resultados"]))
        for d, r in resumen.iterrows()
        if r["n_resultados"] > 0
    }


def _bruto_panel(tabla: pd.DataFrame) -> dict[str, tuple[float, int]]:
    return {
        r["destino_id"]: (float(r["presencia_pct"]), int(r["n_sesiones"]))
        for _, r in tabla.iterrows()
    }


def _bruto_asistentes(tabla: pd.DataFrame) -> tuple[dict[str, tuple[float, int]], str]:
    segmento = SEGMENTO_ASISTENTES
    t = tabla[tabla["segmento"] == segmento]
    if t.empty:
        segmento = SEGMENTO_ASISTENTES_RESPALDO
        t = tabla[tabla["segmento"] == segmento]
    return (
        {r["destino_id"]: (float(r["visibilidad_pct"]), int(r["n"])) for _, r in t.iterrows()},
        segmento,
    )


def valores_brutos(
    tablas: dict[str, pd.DataFrame], desde: str, hasta: str
) -> tuple[dict[str, dict[str, tuple[float, int]]], list[str]]:
    """Valor bruto y n por componente y destino, más las notas que el cálculo genera."""
    brutos: dict[str, dict[str, tuple[float, int]]] = {}
    notas: list[str] = []
    if "busqueda" in tablas:
        brutos["busqueda"] = _bruto_busqueda(tablas["busqueda"], desde, hasta)
    if "video" in tablas:
        brutos["video"] = _bruto_video(tablas["video"])
    if "panel" in tablas:
        brutos["panel"] = _bruto_panel(tablas["panel"])
    if "asistentes" in tablas:
        valores, segmento = _bruto_asistentes(tablas["asistentes"])
        brutos["asistentes"] = valores
        if segmento != SEGMENTO_ASISTENTES:
            notas.append(f"Asistentes: sin segmento {SEGMENTO_ASISTENTES}; se usó «{segmento}»")
    return brutos, notas


def calcular(
    tablas: dict[str, pd.DataFrame], universo: list[str], desde: str, hasta: str
) -> tuple[pd.DataFrame, list[str], list[str]]:
    """Valor, n y percentil de cada componente para los destinos del universo.

    Devuelve la tabla (una fila por destino), los componentes disponibles y las notas
    generales. Un componente es disponible si al menos dos destinos del universo tienen
    valor, que es lo mínimo para calcular un percentil.
    """
    brutos, notas = valores_brutos(tablas, desde, hasta)
    filas = pd.DataFrame({"destino_id": universo})
    disponibles: list[str] = []
    for componente in COMPONENTES:
        valores = brutos.get(componente, {})
        serie = [valores.get(d, (None, None))[0] for d in universo]
        filas[f"atencion_{componente}_valor"] = serie
        filas[f"atencion_{componente}_n"] = pd.array(
            [valores.get(d, (None, None))[1] for d in universo], dtype="Int64"
        )
        filas[f"atencion_{componente}_pctl"] = percentiles(serie)
        if sum(v is not None for v in serie) >= 2:
            disponibles.append(componente)
        elif componente in brutos:
            notas.append(f"Componente {componente} con menos de 2 destinos con valor; no se usa")
            filas[f"atencion_{componente}_pctl"] = None
    return filas, disponibles, notas
