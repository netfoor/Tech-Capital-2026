"""Genera `04-inventario-fuentes.md` y las tablas de `09-resultados.md` (T011-08).

Solo lee `data/`. Escribir dos veces con los mismos datos produce el mismo archivo.
"""

from __future__ import annotations

import json

import pandas as pd

from radar import config

CARPETA = "docs/entregables"
INICIO = "<!-- generado:inicio -->"
FIN = "<!-- generado:fin -->"
CUADRANTES = {
    "consolidado": "Consolidado",
    "atencion_sin_estancia": "Atención sin estancia",
    "demanda_poco_visible": "Demanda poco visible",
    "por_posicionar": "Por posicionar",
}
IDIOMAS = {"es": "Español", "en": "Inglés", "fr": "Francés", "ko": "Coreano", "zh": "Chino"}


def _num(x, d: int = 1) -> str:
    return "sin dato" if pd.isna(x) else f"{x:,.{d}f}"


def _tabla(encabezados: list[str], filas: list[list[str]]) -> str:
    lineas = ["| " + " | ".join(encabezados) + " |", "|" + "---|" * len(encabezados)]
    lineas += ["| " + " | ".join(f) + " |" for f in filas]
    return "\n".join(lineas)


def inventario() -> str:
    fuentes = pd.read_csv(config.ruta(config.FUENTES, "fuentes.csv"), dtype=str).fillna("")
    extra = pd.read_csv(config.ruta(config.REFERENCIA, "inventario_fuentes.csv"), dtype=str)
    propias = json.loads(config.ruta(config.REFERENCIA, "metodo.json").read_text("utf-8"))[
        "fuentes_propias"
    ]
    registro = {r["fuente_id"]: r for _, r in fuentes.iterrows()}
    for p in propias:
        registro[p["fuente_id"]] = {
            "titulo": p["titulo"],
            "institucion": p["institucion"],
            "tipo": p["tipo"],
            "url": p["url"] or "",
            "fecha_consulta": p["fecha_consulta"] or "",
            "archivo": "",
            "sha256": "",
            "uso_en_el_proyecto": p["uso_en_el_proyecto"],
        }
    salida = [
        "# 4. Inventario y documentación de las fuentes de datos",
        "",
        "> Generado por `uv run radar entregables` desde `data/fuentes/fuentes.csv` y "
        "`data/referencia/inventario_fuentes.csv`. No se edita a mano.",
        "",
    ]
    for _, e in extra.iterrows():
        f = registro[e["fuente_id"]]
        evidencia = (
            f"`{f['archivo']}` · SHA-256 `{f['sha256'][:16]}…`" if f["archivo"] else "Sin archivo"
        )
        origen = f"[{f['institucion']}]({f['url']})" if f["url"] else f["institucion"]
        salida += [
            f"## {f['titulo']} (`{e['fuente_id']}`)",
            "",
            f"- **Qué:** {f['uso_en_el_proyecto']}",
            f"- **Por qué:** {e['por_que']}",
            f"- **De dónde:** {origen}"
            + (f", consultado el {f['fecha_consulta']}" if f["fecha_consulta"] else ""),
            f"- **Cómo:** {e['como']}",
            f"- **Calidad:** {e['calidad']}",
            f"- **Preparación:** {e['preparacion']}",
            f"- **Evidencia:** {evidencia}",
            "",
        ]
    return "\n".join(salida).rstrip() + "\n"


def tablas_resultados() -> str:
    radar = pd.read_csv(config.ruta(config.CURADO, "radar_destinos.csv"))
    destinos = pd.read_csv(config.ruta(config.REFERENCIA, "destinos.csv")).set_index("destino_id")
    r = radar.sort_values("brecha", ascending=False)
    filas = [
        [
            destinos.loc[x["destino_id"], "nombre"],
            CUADRANTES.get(x["cuadrante"], "Sin clasificar"),
            _num(x["indice_atencion"]),
            _num(x["indice_desempeno"]),
            _num(x["brecha"]),
            _num(x["ocupacion_12m"]),
        ]
        for _, x in r.iterrows()
    ]
    desde, hasta = radar["periodo_ref_desde"].iloc[0], radar["periodo_ref"].iloc[0]
    bloques = [
        f"Periodo de referencia: {desde} a {hasta}.",
        "",
        "**Radar por destino** (ordenado por brecha)",
        "",
        _tabla(
            ["Destino", "Cuadrante", "Atención", "Desempeño", "Brecha", "Ocupación 12 m (%)"], filas
        ),
    ]
    vis = pd.read_csv(config.ruta(config.CURADO, "asistentes_visibilidad.csv"))
    pueblos = set(destinos.index[destinos["pueblo_magico"]])
    filas = []
    for idioma, nombre in IDIOMAS.items():
        s = vis[(vis["segmento"] == f"idioma={idioma}") & vis["destino_id"].isin(pueblos)]
        filas.append([nombre, str(int(s["n"].max())), _num(s["visibilidad_pct"].mean())])
    bloques += [
        "",
        "**Visibilidad promedio de los Pueblos Mágicos en asistentes, por idioma**",
        "",
        _tabla(["Idioma", "Corridas por destino", "Visibilidad promedio (%)"], filas),
    ]
    c = pd.read_csv(config.ruta(config.CURADO, "asistentes_corridas.csv"))
    g = c.groupby(["proveedor", "modelo"]).agg(
        n=("corrida_id", "size"),
        busco=("busco", "mean"),
        entrada=("tokens_entrada", "sum"),
        salida=("tokens_salida", "sum"),
    )
    filas = [
        [
            p,
            m,
            str(int(x["n"])),
            _num(x["busco"] * 100),
            f"{int(x['entrada']):,}",
            f"{int(x['salida']):,}",
        ]
        for (p, m), x in g.iterrows()
    ]
    bloques += [
        "",
        "**Corridas de asistentes**",
        "",
        _tabla(
            [
                "Proveedor",
                "Modelo",
                "Corridas",
                "Buscó en la web (%)",
                "Tokens de entrada",
                "Tokens de salida",
            ],
            filas,
        ),
    ]
    return "\n".join(bloques) + "\n"


def escribir_resultados(texto: str, bloque: str) -> str:
    cuerpo = f"{INICIO}\n{bloque}{FIN}"
    if INICIO in texto and FIN in texto:
        antes = texto.split(INICIO)[0]
        despues = texto.split(FIN, 1)[1]
        return f"{antes}{cuerpo}{despues}"
    encabezado, _, resto = texto.partition("\n## ")
    return f"{encabezado}\n## Tablas generadas\n\n{cuerpo}\n\n## {resto}"


def generar() -> list[str]:
    """Escribe los archivos y devuelve los que cambiaron."""
    cambiados = []
    destino = config.ruta(CARPETA, "04-inventario-fuentes.md")
    nuevo = inventario()
    if not destino.exists() or destino.read_text("utf-8") != nuevo:
        destino.write_text(nuevo, encoding="utf-8")
        cambiados.append(destino.name)
    resultados = config.ruta(CARPETA, "09-resultados.md")
    texto = resultados.read_text("utf-8")
    nuevo = escribir_resultados(texto, tablas_resultados())
    if nuevo != texto:
        resultados.write_text(nuevo, encoding="utf-8")
        cambiados.append(resultados.name)
    return cambiados
