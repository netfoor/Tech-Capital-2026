"""Paquete de datos del sitio (spec 009): arma los JSON de `contracts/`, los valida y los firma.

Solo lee `data/curado/` y `data/referencia/`. Si algún archivo no pasa su esquema, no se
escribe ninguno (FR-009-02).
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from radar import config
from radar.comun.cuadrantes import RECOMENDACIONES
from radar.comun.estadistica import mediana

COMPONENTES = ("busqueda", "video", "panel", "asistentes")
IDIOMAS = ("es", "en", "fr", "ko", "zh")
PROVEEDORES_PUBLICOS = {"openai": "openai", "gemini": "google"}
HERRAMIENTAS = {"openai": "web_search", "google": "google_search"}


# --- utilidades -------------------------------------------------------------------------------


def _nulo(x) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x)) or x is pd.NA


def num(x, decimales: int = 1):
    """Número redondeado o `None` si falta."""
    if _nulo(x):
        return None
    return round(float(x), decimales)


def entero(x):
    return None if _nulo(x) else int(round(float(x)))


def texto_o_nulo(x):
    return None if _nulo(x) or str(x).strip() == "" else str(x)


def ahora() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def commit_actual() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=config.raiz(),
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "sin-commit"


def _leer(nombre: str, carpeta: str = config.CURADO) -> pd.DataFrame | None:
    ruta = config.ruta(carpeta, nombre)
    return pd.read_csv(ruta) if ruta.exists() else None


# --- insumos ----------------------------------------------------------------------------------


class Insumos:
    """Tablas que alimentan el paquete. Las opcionales son `None` si no existen."""

    def __init__(self) -> None:
        self.destinos = pd.read_csv(config.ruta(config.REFERENCIA, "destinos.csv"))
        self.mensual = pd.read_csv(config.ruta(config.CURADO, "indicadores_oficiales_mensual.csv"))
        self.anual = pd.read_csv(config.ruta(config.CURADO, "indicadores_oficiales_anual.csv"))
        self.factor = pd.read_csv(config.ruta(config.CURADO, "factor_afluencia_por_centro.csv"))
        self.radar = pd.read_csv(config.ruta(config.CURADO, "radar_destinos.csv"))
        self.referencia = pd.read_csv(config.ruta(config.CURADO, "radar_referencia.csv"))
        self.corridas = _leer("asistentes_corridas.csv")
        self.menciones = _leer("asistentes_menciones.csv")
        self.citas = _leer("asistentes_citas.csv")
        self.visibilidad = _leer("asistentes_visibilidad.csv")
        self.ejemplos = _leer("asistentes_ejemplos.csv")
        self.fuentes = pd.read_csv(config.ruta(config.FUENTES, "fuentes.csv"))
        self.evidencia_externa = pd.read_csv(
            config.ruta(config.REFERENCIA, "evidencia_externa.csv"), dtype=str
        )
        self.metodo = json.loads(
            config.ruta(config.REFERENCIA, "metodo.json").read_text(encoding="utf-8")
        )
        self.prompts = pd.read_csv(config.ruta(config.REFERENCIA, "prompts.csv"))

    @property
    def tiene_asistentes(self) -> bool:
        return self.visibilidad is not None and self.corridas is not None

    @property
    def pueblos(self) -> list[str]:
        return sorted(self.destinos.loc[self.destinos["pueblo_magico"], "destino_id"])


# --- constructores ----------------------------------------------------------------------------


def destinos_json(i: Insumos, generado: str) -> dict:
    filas = []
    for _, d in i.destinos.sort_values("destino_id").iterrows():
        filas.append(
            {
                "destino_id": d["destino_id"],
                "nombre": d["nombre"],
                "tipo": d["tipo"],
                "pueblo_magico": bool(d["pueblo_magico"]),
                "zona": d["zona"],
                "lat": round(float(d["lat"]), 4),
                "lon": round(float(d["lon"]), 4),
                "municipios_cvegeo": str(d["municipios_cvegeo"]).split(";"),
            }
        )
    return {"generado": generado, "destinos": filas}


def _redondear_coordenadas(c):
    if isinstance(c, list):
        return [_redondear_coordenadas(x) for x in c]
    return round(float(c), 4)


def geo_json(i: Insumos) -> tuple[dict, dict]:
    por_municipio: dict[str, str] = {}
    for _, d in i.destinos.iterrows():
        for cve in str(d["municipios_cvegeo"]).split(";"):
            por_municipio.setdefault(cve, d["destino_id"])
    crudo = json.loads(
        config.ruta(config.REFERENCIA, "geo", "municipios-puebla.geojson").read_text("utf-8")
    )
    municipios = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "cvegeo": f["properties"]["cvegeo"],
                    "nombre": f["properties"]["nomgeo"],
                    "destino_id": por_municipio.get(f["properties"]["cvegeo"]),
                },
                "geometry": {
                    "type": f["geometry"]["type"],
                    "coordinates": _redondear_coordenadas(f["geometry"]["coordinates"]),
                },
            }
            for f in sorted(crudo["features"], key=lambda f: f["properties"]["cvegeo"])
        ],
    }
    contorno = json.loads(
        config.ruta(config.REFERENCIA, "geo", "estado-puebla.geojson").read_text("utf-8")
    )
    geometrias = contorno.get("geometries") or [f["geometry"] for f in contorno["features"]]
    estado = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"cvegeo": "21", "nombre": "Puebla", "destino_id": None},
                "geometry": {
                    "type": g["type"],
                    "coordinates": _redondear_coordenadas(g["coordinates"]),
                },
            }
            for g in geometrias
        ],
    }
    return municipios, estado


def _componentes_de(fila: pd.Series) -> dict:
    salida = {}
    for c in COMPONENTES:
        pctl = fila.get(f"atencion_{c}_pctl")
        if _nulo(pctl):
            continue
        salida[c] = {
            "valor": num(fila.get(f"atencion_{c}_valor"), 2),
            "pctl": num(pctl),
            "n": entero(fila.get(f"atencion_{c}_n")),
        }
    return salida


def _notas(fila: pd.Series) -> list[str]:
    nota = texto_o_nulo(fila.get("notas"))
    return [n.strip() for n in nota.split(";") if n.strip()] if nota else []


def _fila_radar(fila: pd.Series, referencia: bool = False) -> dict:
    cuadrante = None if referencia else texto_o_nulo(fila.get("cuadrante"))
    return {
        "destino_id": fila["destino_id"],
        "ocupacion_12m": num(fila["ocupacion_12m"]),
        "cuartos_libres_dia_12m": num(fila["cuartos_libres_dia_12m"]),
        "llegadas_12m": entero(fila["llegadas_12m"]),
        "crecimiento_llegadas_pct": num(fila["crecimiento_llegadas_pct"]),
        "componentes": {} if referencia else _componentes_de(fila),
        "indice_atencion": None if referencia else num(fila.get("indice_atencion")),
        "indice_desempeno": None if referencia else num(fila.get("indice_desempeno")),
        "brecha": None if referencia else num(fila.get("brecha")),
        "cuadrante": cuadrante,
        "sensible": False if referencia else bool(fila.get("sensible", False)),
        "notas": ["Referencia: no entra en los percentiles"] if referencia else _notas(fila),
    }


def radar_json(i: Insumos, generado: str) -> dict:
    r = i.radar.sort_values("destino_id")
    disponibles = [c for c in COMPONENTES if r[f"atencion_{c}_pctl"].notna().any()]
    indices = r["indice_atencion"].dropna().tolist()
    return {
        "generado": generado,
        "periodo_ref": {
            "desde": str(r["periodo_ref_desde"].iloc[0]),
            "hasta": str(r["periodo_ref"].iloc[0]),
        },
        "cortes": {
            "atencion": num(mediana(indices)) if indices else 50.0,
            "desempeno": num(mediana(r["indice_desempeno"].dropna().tolist())),
        },
        "componentes_disponibles": disponibles,
        "destinos": [_fila_radar(f) for _, f in r.iterrows()],
        "referencia": _fila_radar(i.referencia.iloc[0], referencia=True),
    }


def _doce_meses(i: Insumos, destino: str, indicador: str, desde: str, hasta: str) -> float:
    m = i.mensual
    f = m[
        (m["destino_id"] == destino)
        & (m["nivel"] == "destino")
        & (m["indicador"] == indicador)
        & (m["periodo"] >= desde)
        & (m["periodo"] <= hasta)
    ]
    return float(f["valor"].sum())


def _serie_mensual(i: Insumos, destino: str) -> list[dict]:
    m = i.mensual
    f = m[(m["destino_id"] == destino) & (m["nivel"] == "destino")]
    ancha = f.pivot_table(index="periodo", columns="indicador", values="valor", aggfunc="first")
    ancha = ancha.sort_index().tail(36)
    return [
        {
            "periodo": periodo,
            "llegadas_turistas": num(f_.get("llegadas_turistas"), 0),
            "ocupacion_pct": num(f_.get("ocupacion_pct")),
        }
        for periodo, f_ in ancha.iterrows()
    ]


def _bloque_asistentes(i: Insumos, destino: str) -> dict | None:
    if not i.tiene_asistentes:
        return None
    v = i.visibilidad
    por_idioma = []
    for idioma in IDIOMAS:
        f = v[(v["destino_id"] == destino) & (v["segmento"] == f"idioma={idioma}")]
        if f.empty:
            continue
        r = f.iloc[0]
        por_idioma.append(
            {
                "idioma": idioma,
                "n": int(r["n"]),
                "k": int(r["k"]),
                "pct": num(r["visibilidad_pct"]),
                "ic95_bajo": num(r["ic95_bajo"]),
                "ic95_alto": num(r["ic95_alto"]),
            }
        )
    dominios = []
    if i.menciones is not None and i.citas is not None:
        corridas = set(i.menciones.loc[i.menciones["destino_id"] == destino, "corrida_id"])
        c = i.citas[i.citas["corrida_id"].isin(corridas) & i.citas["dominio"].notna()]
        top = c.groupby(["dominio", "tipo_dominio"]).size().reset_index(name="n")
        top = top.sort_values(["n", "dominio"], ascending=[False, True]).head(5)
        dominios = [
            {"dominio": r["dominio"], "tipo_dominio": r["tipo_dominio"], "n_citas": int(r["n"])}
            for _, r in top.iterrows()
        ]
    return {"por_idioma": por_idioma, "dominios": dominios}


def ficha_json(i: Insumos, destino: str, generado: str) -> dict:
    d = i.destinos[i.destinos["destino_id"] == destino].iloc[0]
    es_referencia = destino not in set(i.radar["destino_id"])
    fila = (
        i.referencia.iloc[0] if es_referencia else i.radar[i.radar["destino_id"] == destino].iloc[0]
    )
    desde, hasta = str(fila["periodo_ref_desde"]), str(fila["periodo_ref"])
    llegadas = _doce_meses(i, destino, "llegadas_turistas", desde, hasta)
    noches = _doce_meses(i, destino, "turistas_noche", desde, hasta)
    afluencia = _doce_meses(i, destino, "afluencia_visitantes", desde, hasta)
    derrama = _doce_meses(i, destino, "derrama_mxn", desde, hasta)
    radar = _fila_radar(fila, referencia=es_referencia)
    cuadrante = radar["cuadrante"]
    municipios = str(d["municipios_cvegeo"]).split(";")
    fuentes = ["sectur-ot-2026-06", "inegi-mg-2025-12"]
    notas = list(radar["notas"])
    asistentes = _bloque_asistentes(i, destino)
    if asistentes:
        fuentes.append("asistentes-auditoria")
    if radar["componentes"].get("busqueda"):
        fuentes.append("google-trends")
    return {
        "generado": generado,
        "destino": {
            "destino_id": destino,
            "nombre": d["nombre"],
            "tipo": d["tipo"],
            "zona": d["zona"],
            "municipios": municipios,
        },
        "periodo_ref": {"desde": desde, "hasta": hasta},
        "desempeno": {
            "ocupacion_12m": radar["ocupacion_12m"],
            "cuartos_libres_dia_12m": radar["cuartos_libres_dia_12m"],
            "llegadas_12m": radar["llegadas_12m"],
            "crecimiento_llegadas_pct": radar["crecimiento_llegadas_pct"],
            "estadia_promedio_dias": num(noches / llegadas, 2) if llegadas else None,
            "derrama_por_visitante_mxn": num(derrama / afluencia, 0) if afluencia else None,
            "mediana_pm_ocupacion_12m": num(mediana(i.radar["ocupacion_12m"].tolist())),
        },
        "serie_mensual": _serie_mensual(i, destino),
        "radar": {
            "indice_atencion": radar["indice_atencion"],
            "indice_desempeno": radar["indice_desempeno"],
            "brecha": radar["brecha"],
            "cuadrante": cuadrante,
            "recomendacion": RECOMENDACIONES.get(cuadrante) if cuadrante else None,
            "sensible": radar["sensible"],
            "componentes": radar["componentes"],
        },
        "asistentes": asistentes,
        "redes": None,
        "opinion": None,
        "escenario": None,
        "fuentes": fuentes,
        "notas": notas,
    }


def _proporcion(r: pd.Series) -> dict:
    return {
        "n": int(r["n"]),
        "k": int(r["k"]),
        "pct": num(r["visibilidad_pct"]),
        "ic95_bajo": num(r["ic95_bajo"]),
        "ic95_alto": num(r["ic95_alto"]),
    }


def asistentes_json(i: Insumos, generado: str) -> dict | None:
    if not i.tiene_asistentes:
        return None
    c, v = i.corridas, i.visibilidad
    segmentos = []
    combinaciones = [("todos", "total")]
    combinaciones += [(p, f"proveedor={o}") for o, p in PROVEEDORES_PUBLICOS.items()]
    for proveedor, segmento in combinaciones:
        segmentos.append(("todos" if segmento == "total" else proveedor, "todos", segmento))
    for idioma in IDIOMAS:
        segmentos.append(("todos", idioma, f"idioma={idioma}"))
        for o, p in PROVEEDORES_PUBLICOS.items():
            segmentos.append((p, idioma, f"proveedor={o};idioma={idioma}"))
    salida = []
    for proveedor, idioma, clave in segmentos:
        f = v[v["segmento"] == clave]
        if f.empty:
            continue
        salida.append(
            {
                "proveedor": proveedor,
                "idioma": idioma,
                "tono": "todos",
                "destinos": [
                    {"destino_id": r["destino_id"], **_proporcion(r)}
                    for _, r in f.sort_values("destino_id").iterrows()
                ],
            }
        )
    modelos = (
        c.groupby(["proveedor", "modelo"]).size().reset_index().sort_values(["proveedor", "modelo"])
    )
    prompts_por_idioma = {
        idioma: int(c.loc[c["idioma"] == idioma, "prompt_id"].nunique())
        for idioma in IDIOMAS
        if (c["idioma"] == idioma).any()
    }
    dominios = []
    if i.citas is not None:
        citas = i.citas.merge(c[["corrida_id", "idioma"]], on="corrida_id")
        citas = citas[citas["dominio"].notna()]
        for idioma in ("todos", *IDIOMAS):
            sub = citas if idioma == "todos" else citas[citas["idioma"] == idioma]
            total = c.shape[0] if idioma == "todos" else int((c["idioma"] == idioma).sum())
            if sub.empty or not total:
                continue
            agrupado = sub.groupby(["dominio", "tipo_dominio"]).agg(
                n=("url", "size"), corridas=("corrida_id", "nunique")
            )
            top = agrupado.reset_index().sort_values(["n", "dominio"], ascending=[False, True])
            for _, r in top.head(15).iterrows():
                dominios.append(
                    {
                        "idioma": idioma,
                        "dominio": r["dominio"],
                        "tipo_dominio": r["tipo_dominio"],
                        "n_citas": int(r["n"]),
                        "pct_corridas": num(r["corridas"] / total * 100),
                    }
                )
    ejemplos = []
    if i.ejemplos is not None:
        for _, r in i.ejemplos.iterrows():
            ejemplos.append(
                {
                    "corrida_id": r["corrida_id"],
                    "idioma": r["idioma"],
                    "proveedor": PROVEEDORES_PUBLICOS[r["proveedor"]],
                    "prompt": r["prompt"],
                    "fragmento": r["fragmento"],
                    "destinos_mencionados": [
                        x for x in str(r["destinos_mencionados"]).split("|") if x and x != "nan"
                    ],
                    "dominios": [x for x in str(r["dominios"]).split("|") if x and x != "nan"],
                }
            )
    return {
        "generado": generado,
        "corridas": {
            "n": int(len(c)),
            "desde": str(c["fecha"].min()),
            "hasta": str(c["fecha"].max()),
            "modelos": [
                {
                    "proveedor": PROVEEDORES_PUBLICOS[r["proveedor"]],
                    "modelo": r["modelo"],
                    "herramienta": HERRAMIENTAS[PROVEEDORES_PUBLICOS[r["proveedor"]]],
                }
                for _, r in modelos.iterrows()
            ],
            "prompts_por_idioma": prompts_por_idioma,
            "repeticiones": int(c["repeticion"].max()),
        },
        "segmentos": salida,
        "dominios": dominios,
        "ejemplos": ejemplos,
        "validacion_deteccion": _validacion(),
    }


def _validacion() -> dict | None:
    ruta = config.ruta(config.REFERENCIA, "validacion_deteccion.json")
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None


def redes_json(i: Insumos, generado: str) -> dict:
    return {"generado": generado, "panel": None, "youtube": None, "opinion": None}


def evidencia_json(i: Insumos, generado: str) -> dict:
    hallazgos = []
    ext = i.evidencia_externa.set_index("id")

    def externo(id_: str) -> dict:
        r = ext.loc[id_]
        try:
            cifra: float | str = float(r["cifra"])
        except ValueError:
            cifra = r["cifra"]
        return {
            "id": id_,
            "titulo": r["titulo"],
            "cifra": cifra,
            "unidad": r["unidad"],
            "texto": r["texto"],
            "periodo": r["periodo"],
            "fuente_id": r["fuente_id"],
            "origen": r["origen"],
        }

    hallazgos.append(externo("redes"))

    # Medición: factor fijo entre llegadas a hotel y afluencia
    centros_pm = {d["centro_ot"] for _, d in i.destinos.iterrows() if bool(d["pueblo_magico"])}
    f = i.factor[i.factor["centro_ot"].isin(centros_pm)]
    fijos = f[(f["factor_mas_frecuente"] == 2.222) & (f["proporcion_desde_2019"] >= 0.9999)]
    hallazgos.append(
        {
            "id": "medicion",
            "titulo": "La afluencia se deriva de las llegadas a hotel",
            "cifra": 2.222,
            "unidad": "factor",
            "texto": (
                f"La afluencia mensual es la llegada de turistas a hotel por un factor fijo: "
                f"desde 2019, {len(fijos)} de los {len(f)} Pueblos Mágicos usan 2.222 en el 100 % "
                "de los meses. El visitante que no pernocta en un hotel registrado no está en "
                "la medición directa."
            ),
            "periodo": "2019 a 2026",
            "fuente_id": "sectur-ot-2026-06",
            "origen": "data/curado/factor_afluencia_por_centro.csv (proporcion_desde_2019)",
        }
    )

    # Concentración y capacidad: año completo más reciente
    a = i.anual
    anio = int(a[(a["meses"] == 12) & (a["nivel"] == "agregado")]["anio"].max())
    del_anio = a[(a["anio"] == anio) & (a["meses"] == 12)]
    estado = float(del_anio[del_anio["nivel"] == "agregado"].iloc[0]["afluencia_visitantes"])
    capital = del_anio[del_anio["destino_id"] == "puebla"].iloc[0]
    pm = del_anio[del_anio["destino_id"].isin(i.pueblos) & (del_anio["nivel"] == "destino")]
    pct_capital = float(capital["afluencia_visitantes"]) / estado * 100
    pct_pm = float(pm["afluencia_visitantes"].sum()) / estado * 100
    hallazgos.append(
        {
            "id": "concentracion",
            "titulo": "La afluencia se concentra en la capital",
            "cifra": num(pct_pm),
            "unidad": "% de la afluencia estatal en los 12 Pueblos Mágicos",
            "texto": (
                f"En {anio}, la capital concentró {num(pct_capital)} % de la afluencia estatal "
                f"y los 12 Pueblos Mágicos {num(pct_pm)} %."
            ),
            "periodo": str(anio),
            "fuente_id": "sectur-ot-2026-06",
            "origen": "data/curado/indicadores_oficiales_anual.csv (afluencia_visitantes)",
        }
    )
    menores = int((pm["ocupacion_pct"] < float(capital["ocupacion_pct"])).sum())
    serie = [
        {"etiqueta": r["centro_ot"], "valor": num(r["cuartos_libres_por_dia"], 0)}
        for _, r in pm.sort_values("cuartos_libres_por_dia", ascending=False).iterrows()
    ]
    hallazgos.append(
        {
            "id": "capacidad",
            "titulo": "Hay capacidad disponible fuera de la capital",
            "cifra": int(round(float(pm["cuartos_libres_por_dia"].sum()))),
            "unidad": "cuartos libres por día en los 12 Pueblos Mágicos",
            "texto": (
                f"En {anio}, {menores} de los {len(pm)} Pueblos Mágicos tuvieron menor ocupación "
                f"que la capital ({num(capital['ocupacion_pct'])} %)."
            ),
            "periodo": str(anio),
            "fuente_id": "sectur-ot-2026-06",
            "origen": "data/curado/indicadores_oficiales_anual.csv (cuartos_libres_por_dia)",
            "serie": serie,
        }
    )
    hallazgos.append(externo("tianguis"))
    return {"generado": generado, "hallazgos": hallazgos}


def metodo_json(i: Insumos, generado: str) -> dict:
    fuentes = []
    for _, r in i.fuentes.iterrows():
        fuentes.append(
            {
                "fuente_id": r["fuente_id"],
                "titulo": r["titulo"],
                "institucion": r["institucion"],
                "tipo": r["tipo"],
                "url": texto_o_nulo(r["url"]),
                "fecha_consulta": texto_o_nulo(r["fecha_consulta"]),
                "uso_en_el_proyecto": texto_o_nulo(r["uso_en_el_proyecto"]) or "",
            }
        )
    fuentes += i.metodo["fuentes_propias"]
    m = i.metodo
    return {
        "generado": generado,
        "fuentes": fuentes,
        "procesos": m["procesos"],
        "formulas": m["formulas"],
        "componentes_ia": m["componentes_ia"],
        "limitaciones": m["limitaciones"],
    }


# --- paquete ----------------------------------------------------------------------------------

FUENTES_POR_ARCHIVO = {
    "destinos.json": ["inegi-cabeceras"],
    "geo/municipios.json": ["inegi-mg-2025-12"],
    "geo/estado.json": ["inegi-mg-2025-12"],
    "radar.json": ["sectur-ot-2026-06", "google-trends", "asistentes-auditoria"],
    "evidencia.json": ["sectur-ot-2026-06", "sectur-obs-verano-2024", "tianguis-2027"],
    "metodo.json": ["sectur-ot-2026-06"],
    "asistentes.json": ["asistentes-auditoria"],
    "redes.json": [],
}


def armar(i: Insumos | None = None, generado: str | None = None) -> dict[str, object]:
    """Todos los JSON del paquete, por ruta relativa a `datos/`, sin escribir nada."""
    i = i or Insumos()
    generado = generado or ahora()
    municipios, estado = geo_json(i)
    paquete: dict[str, object] = {
        "destinos.json": destinos_json(i, generado),
        "geo/municipios.json": municipios,
        "geo/estado.json": estado,
        "radar.json": radar_json(i, generado),
        "evidencia.json": evidencia_json(i, generado),
        "metodo.json": metodo_json(i, generado),
        "redes.json": redes_json(i, generado),
    }
    asistentes = asistentes_json(i, generado)
    if asistentes is not None:
        paquete["asistentes.json"] = asistentes
    destinos_con_ficha = [*i.pueblos, "puebla"]
    for destino in destinos_con_ficha:
        paquete[f"fichas/{destino}.json"] = ficha_json(i, destino, generado)
    return paquete


ESQUEMAS_POR_ARCHIVO = {
    "manifiesto.json": "manifiesto.schema.json",
    "destinos.json": "destinos.schema.json",
    "geo/municipios.json": "geo.schema.json",
    "geo/estado.json": "geo.schema.json",
    "radar.json": "radar.schema.json",
    "evidencia.json": "evidencia.schema.json",
    "metodo.json": "metodo.schema.json",
    "asistentes.json": "asistentes.schema.json",
    "redes.json": "redes.schema.json",
}


def _esquema_de(ruta: str) -> str:
    return "ficha.schema.json" if ruta.startswith("fichas/") else ESQUEMAS_POR_ARCHIVO[ruta]


def validar(paquete: dict[str, object]) -> list[str]:
    """Errores de validación contra `contracts/`; vacío si todo pasa."""
    carpeta = config.ruta(config.CONTRATOS)
    esquemas = {
        p.name: json.loads(p.read_text(encoding="utf-8")) for p in carpeta.glob("*.schema.json")
    }
    registro = Registry().with_resources(
        (nombre, Resource.from_contents(e)) for nombre, e in esquemas.items()
    )
    errores = []
    for ruta, contenido in paquete.items():
        nombre = _esquema_de(ruta)
        validador = Draft202012Validator(esquemas[nombre], registry=registro)
        for e in sorted(validador.iter_errors(contenido), key=lambda e: list(e.path))[:5]:
            donde = "/".join(str(p) for p in e.path) or "(raíz)"
            errores.append(f"{ruta} · {donde}: {e.message[:200]}")
    return errores


def serializar(contenido: object) -> bytes:
    return (json.dumps(contenido, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def sha256(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


def escribir(paquete: dict[str, object], destino: Path | None = None) -> Path:
    """Escribe los JSON, copia las descargas y firma todo en `manifiesto.json`."""
    raiz_datos = destino or config.ruta(config.WEB_DATOS)
    descargas = raiz_datos.parent / "descargas"
    if raiz_datos.exists():
        shutil.rmtree(raiz_datos)
    raiz_datos.mkdir(parents=True)
    archivos = []
    for ruta, contenido in sorted(paquete.items()):
        datos = serializar(contenido)
        salida = raiz_datos / ruta
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_bytes(datos)
        fuentes = FUENTES_POR_ARCHIVO.get(ruta, ["sectur-ot-2026-06", "google-trends"])
        archivos.append(
            {"ruta": ruta, "sha256": sha256(datos), "bytes": len(datos), "fuentes": fuentes}
        )
    if descargas.exists():
        shutil.rmtree(descargas)
    descargas.mkdir(parents=True)
    for csv in sorted(config.ruta(config.CURADO).glob("*.csv")):
        shutil.copy2(csv, descargas / csv.name)
        datos = csv.read_bytes()
        archivos.append(
            {
                "ruta": f"../descargas/{csv.name}",
                "sha256": sha256(datos),
                "bytes": len(datos),
                "fuentes": [],
            }
        )
    manifiesto = {"generado": ahora(), "commit": commit_actual(), "archivos": archivos}
    errores = validar({"manifiesto.json": manifiesto})
    if errores:
        raise ValueError("; ".join(errores))
    (raiz_datos / "manifiesto.json").write_bytes(serializar(manifiesto))
    return raiz_datos
