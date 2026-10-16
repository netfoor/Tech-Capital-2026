"""Capa anticorrupción de Google Trends (spec 003).

Trends devuelve valores de 0 a 100 relativos a cada consulta, así que dos lotes no son
comparables entre sí. Cada lote lleva un término ancla; el reescalado usa la media del ancla
en el lote de referencia frente a su media en el lote (FR-003-03), y para destinos de bajo
volumen se encadena un ancla de segundo nivel (FR-003-02).
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

from radar import config

ANCLA_POR_DEFECTO = "cholula"
UMBRAL_BAJO_VOLUMEN = 1.0
MAX_TERMINOS_POR_LOTE = 5

# Lotes del plan 003: el primero fija la referencia; el tercero usa a Cuetzalan como
# ancla de segundo nivel porque Cholula aplasta a los destinos pequeños.
LOTES_POR_DEFECTO: tuple[tuple[str, tuple[str, ...], str | None], ...] = (
    ("A", ("zacatlan", "chignahuapan", "atlixco", "cuetzalan"), None),
    ("B", ("huauchinango", "teziutlan", "xicotepec", "huejotzingo"), None),
    ("C", ("cuetzalan", "tlatlauquitepec", "tetela-de-ocampo", "pahuatlan"), "cuetzalan"),
)


@dataclass(frozen=True)
class Lote:
    nombre: str
    ancla: str
    destinos: tuple[str, ...]
    ancla2: str | None = None
    terminos: dict[str, str] = field(default_factory=dict)

    @property
    def ids(self) -> tuple[str, ...]:
        """Destinos consultados en el lote, con el ancla primero y sin repetir."""
        vistos = [self.ancla]
        for d in self.destinos:
            if d not in vistos:
                vistos.append(d)
        return tuple(vistos)

    def palabras(self) -> list[str]:
        return [self.terminos[d] for d in self.ids]


def armar_lotes(
    terminos: dict[str, str],
    ancla: str = ANCLA_POR_DEFECTO,
    plan: tuple[tuple[str, tuple[str, ...], str | None], ...] = LOTES_POR_DEFECTO,
) -> list[Lote]:
    """Lotes con el ancla incluida en cada uno y a lo más 5 términos (FR-003-01)."""
    lotes = []
    for nombre, destinos, ancla2 in plan:
        lote = Lote(nombre, ancla, destinos, ancla2, terminos)
        if len(lote.ids) > MAX_TERMINOS_POR_LOTE:
            raise ValueError(f"El lote {nombre} tiene más de {MAX_TERMINOS_POR_LOTE} términos")
        faltan = [d for d in lote.ids if d not in terminos]
        if faltan:
            raise ValueError(f"Faltan términos para {', '.join(faltan)}")
        lotes.append(lote)
    return lotes


def ultimo_mes_cerrado(hoy: date | None = None) -> date:
    hoy = hoy or date.today()
    return hoy.replace(day=1) - timedelta(days=1)


def timeframe(desde: str, hoy: date | None = None) -> str:
    return f"{desde} {ultimo_mes_cerrado(hoy).isoformat()}"


def _media(serie: pd.Series) -> float:
    return float(serie.mean())


def factor_reescalado(ancla_referencia: pd.Series, ancla_lote: pd.Series) -> float:
    """`media(ancla en la referencia) / media(ancla en el lote)` sobre todo el rango."""
    en_lote = _media(ancla_lote)
    if en_lote == 0:
        raise ValueError("El ancla no tiene interés en el lote; usa un ancla de segundo nivel")
    return _media(ancla_referencia) / en_lote


def es_bajo_volumen(ancla_lote: pd.Series) -> bool:
    """El ancla casi no registra interés en la mayoría de los meses del lote."""
    return float((ancla_lote < UMBRAL_BAJO_VOLUMEN).mean()) > 0.5


def reescalar(
    lotes: list[Lote], series: dict[str, pd.DataFrame]
) -> tuple[pd.DataFrame, dict[str, dict[str, object]]]:
    """Une los lotes en una sola escala.

    `series[nombre]` es una tabla ancha: índice `periodo` (AAAA-MM) y una columna por
    `destino_id`. Devuelve la tabla larga `(destino_id, periodo, interes, ancla, factor,
    interes_ajustado, lote)` y, por lote, el ancla y el factor usados. Si un destino aparece
    en más de un lote se conserva el del lote de referencia (el primero).
    """
    referencia = lotes[0]
    ref = series[referencia.nombre]
    filas = []
    detalle: dict[str, dict[str, object]] = {}
    vistos: set[str] = set()
    for lote in lotes:
        tabla = series[lote.nombre]
        if lote is referencia:
            ancla_id, factor = lote.ancla, 1.0
        elif lote.ancla2 and es_bajo_volumen(tabla[lote.ancla]):
            # Ancla de segundo nivel: ya vive en la escala de referencia por estar en su lote.
            ancla_id = lote.ancla2
            factor = factor_reescalado(ref[ancla_id], tabla[ancla_id])
        else:
            ancla_id = lote.ancla
            factor = factor_reescalado(ref[ancla_id], tabla[ancla_id])
        detalle[lote.nombre] = {"ancla": ancla_id, "factor": factor}
        for destino in lote.ids:
            if destino in vistos:
                continue
            vistos.add(destino)
            for periodo, valor in tabla[destino].items():
                filas.append(
                    {
                        "destino_id": destino,
                        "periodo": periodo,
                        "interes": int(valor),
                        "ancla": ancla_id,
                        "factor": factor,
                        "interes_ajustado": float(valor) * factor,
                        "lote": lote.nombre,
                    }
                )
    largo = pd.DataFrame(filas).sort_values(["destino_id", "periodo"]).reset_index(drop=True)
    return largo, detalle


# --- Consulta y lo crudo -------------------------------------------------------------------


def consulta_id(geo: str, lote: str, fecha: date) -> str:
    return f"trends-{geo}-{lote}-{fecha:%Y%m%d}"


def _cliente_pytrends():  # pragma: no cover - requiere red
    from pytrends.request import TrendReq

    # Sin `retries` ni `backoff_factor`: fallan con urllib3 2 (método `method_whitelist`).
    return TrendReq(hl="es-MX", tz=360)


def consultar_con_reintentos(
    consulta: Callable[[], pd.DataFrame],
    reintentos: int = 3,
    espera_base: float = 60.0,
    dormir: Callable[[float], None] = time.sleep,
) -> pd.DataFrame:
    """Reintenta ante error 429 con espera exponencial (FR-003-05)."""
    for intento in range(reintentos + 1):
        try:
            return consulta()
        except Exception as error:  # pytrends lanza ResponseError con el código en el texto
            es_limite = "429" in str(error)
            if not es_limite or intento == reintentos:
                raise
            dormir(espera_base * 2**intento)
    raise RuntimeError("inalcanzable")  # pragma: no cover


def consultar_lote(
    lote: Lote,
    geo: str,
    desde: str,
    pausa: float = 60.0,
    hoy: date | None = None,
    cliente_fabrica: Callable[[], object] | None = None,
    dormir: Callable[[float], None] = time.sleep,
) -> dict:  # pragma: no cover - requiere red
    """Una consulta real; devuelve el registro crudo listo para guardar."""
    cliente = (cliente_fabrica or _cliente_pytrends)()
    marco = timeframe(desde, hoy)

    def pedir() -> pd.DataFrame:
        cliente.build_payload(lote.palabras(), timeframe=marco, geo=geo)
        return cliente.interest_over_time()

    datos = consultar_con_reintentos(pedir, dormir=dormir, espera_base=pausa)
    hoy = hoy or date.today()
    return crudo_desde_tabla(lote, geo, marco, datos, hoy)


def crudo_desde_tabla(lote: Lote, geo: str, marco: str, datos: pd.DataFrame, hoy: date) -> dict:
    """Respuesta de Trends convertida al registro que se guarda en `data/crudo/trends/`."""
    palabras = lote.palabras()
    filas = []
    for fecha, fila in datos.iterrows():
        if "isPartial" in fila and bool(fila["isPartial"]):
            continue
        registro = {"fecha": pd.Timestamp(fecha).strftime("%Y-%m-%d")}
        registro.update({p: int(fila[p]) for p in palabras})
        filas.append(registro)
    return {
        "consulta_id": consulta_id(geo, lote.nombre, hoy),
        "lote": lote.nombre,
        "terminos": palabras,
        "destinos": list(lote.ids),
        "geo": geo,
        "timeframe": marco,
        "fecha_consulta": hoy.isoformat(),
        "filas": filas,
    }


def guardar_crudo(registro: dict, carpeta: Path | None = None) -> Path:
    carpeta = carpeta or config.ruta(config.CRUDO, "trends")
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{registro['consulta_id']}.json"
    ruta.write_text(json.dumps(registro, ensure_ascii=False, indent=1), encoding="utf-8")
    return ruta


def serie_desde_crudo(registro: dict) -> pd.DataFrame:
    """Tabla ancha (índice AAAA-MM, columnas `destino_id`) a partir de un registro crudo."""
    filas = registro["filas"]
    periodos = [f["fecha"][:7] for f in filas]
    datos = {
        destino: [f[palabra] for f in filas]
        for destino, palabra in zip(registro["destinos"], registro["terminos"], strict=True)
    }
    return pd.DataFrame(datos, index=pd.Index(periodos, name="periodo"))


def tabla_curada(lotes: list[Lote], registros: dict[str, dict], geo: str) -> pd.DataFrame:
    """Tabla `interes_busqueda_mensual.csv` a partir de los registros crudos por lote."""
    series = {nombre: serie_desde_crudo(r) for nombre, r in registros.items()}
    largo, _ = reescalar(lotes, series)
    por_lote = {lote.nombre: lote for lote in lotes}
    largo["termino"] = [
        por_lote[lote].terminos[destino]
        for destino, lote in zip(largo["destino_id"], largo["lote"], strict=True)
    ]
    largo["geo"] = geo
    largo["consulta_id"] = [registros[lote]["consulta_id"] for lote in largo["lote"]]
    largo["fecha_consulta"] = [registros[lote]["fecha_consulta"] for lote in largo["lote"]]
    columnas = [
        "destino_id",
        "termino",
        "geo",
        "periodo",
        "interes",
        "ancla",
        "factor",
        "interes_ajustado",
        "consulta_id",
        "fecha_consulta",
    ]
    return largo[columnas]


def terminos_de_consulta(destinos) -> dict[str, str]:
    """Término de búsqueda de cada destino: tema verificado si existe, si no el primer término."""
    ruta = config.ruta(config.REFERENCIA, "trends_temas.csv")
    temas: dict[str, str] = {}
    if ruta.exists():
        tabla = pd.read_csv(ruta, dtype=str).fillna("")
        for _, f in tabla.iterrows():
            if f.get("verificado", "").lower() == "true" and f.get("tema", ""):
                temas[f["destino_id"]] = f["tema"]
    return {d.destino_id: temas.get(d.destino_id, d.terminos_es[0]) for d in destinos}


def ejecutar(
    destinos,
    geo: str = "MX",
    desde: str = "2017-01-01",
    pausa: float = 60.0,
) -> pd.DataFrame:  # pragma: no cover - requiere red
    lotes = armar_lotes(terminos_de_consulta(destinos))
    registros: dict[str, dict] = {}
    for i, lote in enumerate(lotes):
        if i:
            time.sleep(pausa)
        registro = consultar_lote(lote, geo, desde, pausa)
        guardar_crudo(registro)
        registros[lote.nombre] = registro
    return tabla_curada(lotes, registros, geo)


def fecha_de(texto: str) -> date:
    return datetime.strptime(texto, "%Y-%m-%d").date()


def registros_guardados(geo: str, carpeta: Path | None = None) -> dict[str, dict]:
    """El crudo más reciente de cada lote en `data/crudo/trends/` (rehace la tabla sin red)."""
    carpeta = carpeta or config.ruta(config.CRUDO, "trends")
    por_lote: dict[str, tuple[str, dict]] = {}
    for ruta in sorted(carpeta.glob(f"trends-{geo}-*.json")):
        registro = json.loads(ruta.read_text(encoding="utf-8"))
        actual = por_lote.get(registro["lote"])
        if actual is None or registro["fecha_consulta"] >= actual[0]:
            por_lote[registro["lote"]] = (registro["fecha_consulta"], registro)
    return {lote: r for lote, (_, r) in por_lote.items()}


def destinos_sin_senal(tabla: pd.DataFrame) -> list[str]:
    """Destinos cuyo interés es cero en todos los meses (señal de término mal elegido)."""
    suma = tabla.groupby("destino_id")["interes"].sum()
    return sorted(suma[suma == 0].index)
