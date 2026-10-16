"""Ingesta de «Datos del Observatorio Turístico» (Secretaría de Desarrollo Turístico de Puebla).

El PDF trae una tabla por página con las columnas: centro turístico, indicador, año, los doce
meses y el acumulado. Esta ingesta la convierte en una tabla larga, una fila por
centro, indicador y mes, con la procedencia de cada indicador según el glosario del propio PDF:

- **medido**: registro de establecimientos en DataTur (cuartos, llegadas, noches, ocupación,
  estadía y densidad).
- **derivado**: estimado por la Secretaría (afluencia de visitantes y derrama económica).
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pdfplumber

from radar import catalogo
from radar.texto import normalizar

FUENTE_ID = "sectur-ot-2026-06"

MESES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]


@dataclass(frozen=True)
class Indicador:
    nombre_pdf: str
    indicador_id: str
    unidad: str
    procedencia: str
    aditivo: bool


INDICADORES = [
    Indicador("Cuartos disponibles", "cuartos_disponibles", "cuartos", "medido", True),
    Indicador("Cuartos ocupados", "cuartos_ocupados", "cuartos", "medido", True),
    Indicador("Llegadas de turistas", "llegadas_turistas", "turistas", "medido", True),
    Indicador("Turistas noche", "turistas_noche", "turistas noche", "medido", True),
    Indicador("Porcentaje de ocupación", "ocupacion_pct", "porcentaje", "medido", False),
    Indicador("Estadía promedio", "estadia_promedio_dias", "días", "medido", False),
    Indicador(
        "Densidad de ocupación", "densidad_ocupacion", "turistas por cuarto", "medido", False
    ),
    Indicador("Afluencia de visitantes", "afluencia_visitantes", "visitantes", "derivado", True),
    Indicador("Derrama económica", "derrama_mxn", "pesos", "derivado", True),
]
_POR_NOMBRE = {i.nombre_pdf: i for i in INDICADORES}

# Centros que aparecen en el PDF pero no son destinos del catálogo.
CENTROS_EXTRA = {
    "estado": ("Estado", "agregado"),
    "resto del estado": ("Resto del Estado", "agregado"),
    "san pedro cholula": ("San Pedro Cholula", "subcentro"),
    "san andres cholula": ("San Andrés Cholula", "subcentro"),
}
_ALIAS_PDF = {"cd puebla": "ciudad de puebla"}


def _indicador(texto: str) -> Indicador:
    """Corrige nombres de indicador mezclados con texto de la celda vecina en el PDF."""
    limpio = " ".join(texto.split())
    if limpio in _POR_NOMBRE:
        return _POR_NOMBRE[limpio]
    for nombre, ind in _POR_NOMBRE.items():
        if limpio.endswith(nombre[2:]):
            return ind
    cercano = difflib.get_close_matches(limpio, list(_POR_NOMBRE), n=1, cutoff=0.5)
    if not cercano:
        raise ValueError(f"Indicador no reconocido en el PDF: {texto!r}")
    return _POR_NOMBRE[cercano[0]]


def _numero(texto: str | None) -> float | None:
    if texto is None:
        return None
    limpio = texto.replace(",", "").strip()
    if not limpio:
        return None
    return float(limpio)


def leer_tabla(pdf: Path) -> pd.DataFrame:
    """Lee todas las filas de datos del PDF tal como vienen, incluido el acumulado."""
    filas = []
    with pdfplumber.open(pdf) as documento:
        for pagina in documento.pages:
            for tabla in pagina.extract_tables():
                for fila in tabla:
                    if not fila or len(fila) != 16 or fila[0] == "Centro Turístico":
                        continue
                    anio = (fila[2] or "").strip()
                    if not anio.isdigit():
                        continue
                    filas.append(
                        {
                            "centro_pdf": " ".join((fila[0] or "").split()),
                            "indicador_pdf": fila[1] or "",
                            "anio": int(anio),
                            **{m: _numero(fila[3 + i]) for i, m in enumerate(MESES)},
                            "acumulado": _numero(fila[15]),
                        }
                    )
    if not filas:
        raise ValueError(f"No se encontraron tablas de datos en {pdf}")
    return pd.DataFrame(filas)


def _resolver_centro(
    centro_pdf: str, destinos: dict[str, catalogo.Destino]
) -> tuple[str, str | None, str]:
    """Devuelve (centro_ot, destino_id, nivel). El PDF corta nombres largos de la celda."""
    clave = _ALIAS_PDF.get(normalizar(centro_pdf), normalizar(centro_pdf))
    candidatos: dict[str, tuple[str, str | None, str]] = {
        k: (d.centro_ot, d.destino_id, "destino") for k, d in destinos.items()
    }
    candidatos.update({k: (nombre, None, nivel) for k, (nombre, nivel) in CENTROS_EXTRA.items()})
    if clave in candidatos:
        return candidatos[clave]
    prefijo = [k for k in candidatos if k.startswith(clave)]
    if len(prefijo) == 1:
        return candidatos[prefijo[0]]
    raise ValueError(f"Centro turístico no reconocido en el PDF: {centro_pdf!r}")


def a_tabla_larga(crudo: pd.DataFrame, destinos: list[catalogo.Destino]) -> pd.DataFrame:
    por_centro = catalogo.por_centro_ot(destinos)
    resueltos = {c: _resolver_centro(c, por_centro) for c in crudo["centro_pdf"].unique()}
    registros = []
    for fila in crudo.itertuples(index=False):
        centro_ot, destino_id, nivel = resueltos[fila.centro_pdf]
        ind = _indicador(fila.indicador_pdf)
        for numero_mes, mes in enumerate(MESES, start=1):
            valor = getattr(fila, mes)
            if valor is None or pd.isna(valor):
                continue
            registros.append(
                {
                    "centro_ot": centro_ot,
                    "destino_id": destino_id or "",
                    "nivel": nivel,
                    "anio": fila.anio,
                    "mes": numero_mes,
                    "periodo": f"{fila.anio}-{numero_mes:02d}",
                    "indicador": ind.indicador_id,
                    "valor": valor,
                    "unidad": ind.unidad,
                    "procedencia": ind.procedencia,
                    "fuente_id": FUENTE_ID,
                }
            )
    tabla = pd.DataFrame(registros)
    tabla = _recortar_meses_sin_publicar(tabla)
    return tabla.sort_values(["centro_ot", "indicador", "anio", "mes"]).reset_index(drop=True)


def _recortar_meses_sin_publicar(tabla: pd.DataFrame) -> pd.DataFrame:
    """Algunos centros traen 0.00 en los meses aún no publicados del último año.

    El último periodo publicado es el último mes con llegadas de turistas mayores que cero en
    el agregado «Estado»; todo lo posterior se descarta.
    """
    estado = tabla[
        (tabla["centro_ot"] == "Estado")
        & (tabla["indicador"] == "llegadas_turistas")
        & (tabla["valor"] > 0)
    ]
    if estado.empty:
        return tabla
    ultimo = estado["periodo"].max()
    return tabla[tabla["periodo"] <= ultimo]


def ultimo_periodo(tabla: pd.DataFrame) -> str:
    return str(tabla["periodo"].max())


def comprobar_acumulados(
    crudo: pd.DataFrame, tolerancia: float = 1.0
) -> tuple[list[str], list[str]]:
    """La suma de los meses de un indicador aditivo debe igualar el acumulado del PDF.

    Devuelve (errores, huecos). Un error es una diferencia con los meses completos: indica
    una lectura incorrecta del PDF. Un hueco es un mes en blanco dentro de un año cuyo
    acumulado sí lo incluye: es un faltante de la fuente y se reporta, no se imputa.
    """
    errores, huecos = [], []
    ultimo_anio = int(crudo["anio"].max())
    for fila in crudo.itertuples(index=False):
        ind = _indicador(fila.indicador_pdf)
        if not ind.aditivo or fila.acumulado is None or pd.isna(fila.acumulado):
            continue
        valores = [getattr(fila, m) for m in MESES]
        presentes = [v for v in valores if v is not None and not pd.isna(v)]
        suma = sum(presentes)
        if abs(suma - fila.acumulado) <= max(tolerancia, abs(fila.acumulado) * 1e-6):
            continue
        detalle = (
            f"{fila.centro_pdf} {ind.indicador_id} {fila.anio}: suma {suma:,.2f} "
            f"≠ acumulado {fila.acumulado:,.2f}"
        )
        faltan = [m for m, v in zip(MESES, valores, strict=True) if v is None or pd.isna(v)]
        if faltan and fila.anio != ultimo_anio:
            huecos.append(f"{detalle} (mes en blanco: {', '.join(faltan)})")
        else:
            errores.append(detalle)
    return errores, huecos


def comprobar_coherencia(tabla: pd.DataFrame) -> list[str]:
    """Reglas internas: unicidad y ocupación = cuartos ocupados / disponibles."""
    problemas = []
    llave = ["centro_ot", "indicador", "anio", "mes"]
    if tabla.duplicated(llave).any():
        problemas.append(f"Filas repetidas: {int(tabla.duplicated(llave).sum())}")
    ancha = tabla.pivot_table(
        index=["centro_ot", "anio", "mes"], columns="indicador", values="valor", aggfunc="first"
    )
    con_cuartos = ancha.dropna(subset=["cuartos_disponibles", "cuartos_ocupados", "ocupacion_pct"])
    con_cuartos = con_cuartos[con_cuartos["cuartos_disponibles"] > 0]
    calculada = con_cuartos["cuartos_ocupados"] / con_cuartos["cuartos_disponibles"] * 100
    diferencia = (calculada - con_cuartos["ocupacion_pct"]).abs()
    malas = diferencia[diferencia > 0.6]
    if len(malas):
        problemas.append(
            f"Ocupación incongruente con cuartos en {len(malas)} meses; ejemplo {malas.index[0]}"
        )
    return problemas


def factor_afluencia(tabla: pd.DataFrame) -> pd.DataFrame:
    """Razón afluencia de visitantes / llegadas de turistas por centro (hallazgo de método).

    Para cada centro reporta el factor más frecuente y la proporción de meses que lo usan
    exactamente (±0.002). Una proporción cercana a 1 indica que la afluencia se deriva de las
    llegadas a hotel con un multiplicador fijo.
    """
    ancha = tabla.pivot_table(
        index=["centro_ot", "anio", "mes"], columns="indicador", values="valor", aggfunc="first"
    ).reset_index()
    ancha = ancha[ancha["llegadas_turistas"] > 0].copy()
    ancha["factor"] = ancha["afluencia_visitantes"] / ancha["llegadas_turistas"]

    def resumen(grupo: pd.DataFrame) -> pd.Series:
        modo = grupo["factor"].round(3).mode().iloc[0]
        desde_2019 = grupo[grupo["anio"] >= 2019]
        return pd.Series(
            {
                "factor_mas_frecuente": modo,
                "meses": len(grupo),
                "proporcion_meses_con_ese_factor": ((grupo["factor"] - modo).abs() < 0.002).mean(),
                "proporcion_desde_2019": ((desde_2019["factor"] - modo).abs() < 0.002).mean(),
            }
        )

    return ancha.groupby("centro_ot").apply(resumen, include_groups=False).round(3).reset_index()
