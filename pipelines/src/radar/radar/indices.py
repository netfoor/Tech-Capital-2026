"""Índices de atención y desempeño, brecha, cuadrantes y sensibilidad (spec 008)."""

from __future__ import annotations

import pandas as pd

from radar.comun.cuadrantes import RECOMENDACIONES  # noqa: F401  (se reexporta)
from radar.comun.estadistica import mediana, percentiles
from radar.radar import atencion, desempeno

MIN_COMPONENTES = 2


def clasificar(atencion_i: float, desempeno_i: float, corte_a: float, corte_d: float) -> str:
    alta_atencion = atencion_i >= corte_a
    alto_desempeno = desempeno_i >= corte_d
    if alta_atencion and alto_desempeno:
        return "consolidado"
    if alta_atencion:
        return "atencion_sin_estancia"
    if alto_desempeno:
        return "demanda_poco_visible"
    return "por_posicionar"


def _indice_atencion(pctls: list[float | None]) -> float | None:
    presentes = [p for p in pctls if p is not None and not pd.isna(p)]
    if len(presentes) < MIN_COMPONENTES:
        return None
    return sum(presentes) / len(presentes)


def _cuadrantes(
    indices_a: list[float | None], indices_d: list[float | None]
) -> tuple[list[str | None], float | None, float | None]:
    """Cuadrante de cada destino con cortes en la mediana de cada índice."""
    con_a = [a for a in indices_a if a is not None]
    con_d = [d for d in indices_d if d is not None]
    if not con_a or not con_d:
        return [None] * len(indices_a), None, None
    corte_a, corte_d = mediana(con_a), mediana(con_d)
    cuadrantes = [
        clasificar(a, d, corte_a, corte_d) if a is not None and d is not None else None
        for a, d in zip(indices_a, indices_d, strict=True)
    ]
    return cuadrantes, corte_a, corte_d


def _sensibles(
    pctls: dict[str, list[float | None]],
    disponibles: list[str],
    indices_d: list[float | None],
    base: list[str | None],
) -> list[bool]:
    """Un destino es sensible si al omitir un componente cambia de cuadrante."""
    n = len(base)
    sensible = [False] * n
    if len(disponibles) <= MIN_COMPONENTES:
        return sensible
    for omitido in disponibles:
        restantes = [c for c in disponibles if c != omitido]
        indices = [_indice_atencion([pctls[c][i] for c in restantes]) for i in range(n)]
        cuadrantes, _, _ = _cuadrantes(indices, indices_d)
        for i in range(n):
            if base[i] is not None and cuadrantes[i] is not None and cuadrantes[i] != base[i]:
                sensible[i] = True
    return sensible


def calcular(
    mensual: pd.DataFrame,
    tablas: dict[str, pd.DataFrame],
    universo: list[str],
) -> tuple[pd.DataFrame, dict[str, float | None], list[str]]:
    """Tabla del radar para el universo, los cortes y los componentes disponibles."""
    perf = desempeno.calcular(mensual, universo)
    desde, hasta = desempeno.periodo_referencia(mensual)
    aten, disponibles, notas_generales = atencion.calcular(tablas, universo, desde, hasta)

    tabla = perf.merge(aten, on="destino_id", how="left")
    indices_d = percentiles(tabla["ocupacion_12m"].tolist())
    pctls = {c: tabla[f"atencion_{c}_pctl"].tolist() for c in disponibles}
    n = len(tabla)
    indices_a = [_indice_atencion([pctls[c][i] for c in disponibles]) for i in range(n)]
    cuadrantes, corte_a, corte_d = _cuadrantes(indices_a, indices_d)
    sensibles = _sensibles(pctls, disponibles, indices_d, cuadrantes)

    tabla["componentes_disponibles"] = [
        sum(pctls[c][i] is not None and not pd.isna(pctls[c][i]) for c in disponibles)
        for i in range(n)
    ]
    tabla["indice_atencion"] = indices_a
    tabla["indice_desempeno"] = indices_d
    tabla["brecha"] = [
        a - d if a is not None and d is not None else None
        for a, d in zip(indices_a, indices_d, strict=True)
    ]
    tabla["cuadrante"] = cuadrantes
    tabla["sensible"] = sensibles

    notas = []
    for i, fila in tabla.iterrows():
        partes = [fila["notas"]] if fila["notas"] else []
        partes += notas_generales
        faltan = [c for c in atencion.COMPONENTES if c not in disponibles]
        if faltan:
            partes.append("Sin dato de " + ", ".join(faltan))
        if indices_a[i] is None:
            partes.append("Menos de 2 componentes de atención: sin índice ni cuadrante")
        if len(disponibles) == MIN_COMPONENTES:
            partes.append("Con solo 2 componentes no se puede medir la sensibilidad")
        notas.append("; ".join(partes))
    tabla["notas"] = notas

    columnas = [
        "destino_id",
        "periodo_ref_desde",
        "periodo_ref",
        "ocupacion_12m",
        "cuartos_libres_dia_12m",
        "llegadas_12m",
        "crecimiento_llegadas_pct",
    ]
    for c in atencion.COMPONENTES:
        columnas += [f"atencion_{c}_valor", f"atencion_{c}_n", f"atencion_{c}_pctl"]
    columnas += [
        "componentes_disponibles",
        "indice_atencion",
        "indice_desempeno",
        "brecha",
        "cuadrante",
        "sensible",
        "notas",
    ]
    tabla = tabla[columnas].sort_values("destino_id").reset_index(drop=True)
    cortes = {"atencion": corte_a, "desempeno": corte_d}
    return tabla, cortes, disponibles
