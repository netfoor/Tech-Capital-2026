"""Análisis del problema (spec 013, contexto maestro §02.3).

Lee solo `data/curado/`, `data/referencia/` y los metadatos de `data/fuentes/fuentes.csv`.
No usa red ni azar. Escribe tablas, figuras y `reports/01_problema.md`.

Uso, desde la raíz del repositorio:

    uv run --project pipelines --extra analisis python analysis/01_problema.py
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from concentracion import gini, hhi  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CURADO = RAIZ / "data" / "curado"
REFERENCIA = RAIZ / "data" / "referencia"
FUENTES = RAIZ / "data" / "fuentes" / "fuentes.csv"
REPORTES = RAIZ / "reports"
FIGURAS = REPORTES / "figuras"
PITCH = RAIZ / "docs" / "pitch" / "figuras"

ANIOS = list(range(2017, 2027))
ANIO_REF = 2025  # último año completo
ANIO_PARCIAL = 2026  # enero–junio
CAPITAL = "puebla"
CHOLULA = "cholula"
MUN_CAPITAL = ["21114"]
MUN_CHOLULA = ["21119", "21140"]

FLOAT = "%.4f"

# Estilo sobrio y accesible: texto casi negro, rejilla tenue, color + trama.
SUPERFICIE = "#fcfcfb"
TEXTO = "#0b0b0b"
TEXTO_2 = "#52514e"
REJILLA = "#e4e3df"
AZUL = "#2a78d6"  # capital y Cholula
NARANJA = "#eb6834"  # Pueblos Mágicos
GRIS = "#a3a29c"  # otros centros
TRAMA_PM = "///"
TRAMA_OTRO = "..."

GRUPOS = {
    "capital": ("Capital", AZUL, ""),
    "cholula": ("Cholula", AZUL, ""),
    "pueblo_magico": ("Pueblo Mágico", NARANJA, TRAMA_PM),
    "otro": ("Otro centro", GRIS, TRAMA_OTRO),
    "resto": ("Resto del Estado", GRIS, TRAMA_OTRO),
}

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "figure.facecolor": SUPERFICIE,
        "axes.facecolor": SUPERFICIE,
        "savefig.facecolor": SUPERFICIE,
        "axes.edgecolor": REJILLA,
        "axes.labelcolor": TEXTO_2,
        "axes.titlecolor": TEXTO,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": TEXTO_2,
        "ytick.color": TEXTO_2,
        "text.color": TEXTO,
        "grid.color": REJILLA,
        "grid.linewidth": 0.8,
        "hatch.color": SUPERFICIE,
        "hatch.linewidth": 1.0,
        "svg.hashsalt": "spec-013",
        "svg.fonttype": "path",
    }
)


# ---------------------------------------------------------------- utilidades


def fmt_entero(x: float) -> str:
    return f"{x:,.0f}"


def fmt_pct(x: float, dec: int = 1) -> str:
    """x en escala 0–1."""
    return f"{100 * x:.{dec}f} %"


def fmt_num(x: float, dec: int = 1) -> str:
    return f"{x:,.{dec}f}"


def escribir_csv(df: pd.DataFrame, nombre: str) -> None:
    df.to_csv(REPORTES / nombre, index=False, float_format=FLOAT, lineterminator="\n")


def guardar(fig: plt.Figure, nombre: str) -> None:
    fig.savefig(FIGURAS / f"{nombre}.svg", metadata={"Date": None, "Creator": None})
    fig.savefig(FIGURAS / f"{nombre}.png", dpi=200, metadata={"Software": None})
    plt.close(fig)


def pie(fig: plt.Figure, texto: str) -> None:
    fig.text(0.01, 0.01, texto, fontsize=7.5, color=TEXTO_2, ha="left", va="bottom", wrap=True)


def tabla_md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    filas = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        filas.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(filas)


def fuente(fuentes: pd.DataFrame, fuente_id: str) -> dict:
    r = fuentes.loc[fuentes["fuente_id"] == fuente_id].iloc[0]
    return {
        "id": fuente_id,
        "titulo": r["titulo"],
        "institucion": r["institucion"],
        "url": r["url"],
        "fecha": r["fecha_consulta"],
    }


def cita(f: dict) -> str:
    return (
        f"{f['titulo']} ({f['institucion']}), {f['url']}, consultado el {f['fecha']} (`{f['id']}`)"
    )


# ---------------------------------------------------------------- carga


def cargar() -> dict:
    anual = pd.read_csv(CURADO / "indicadores_oficiales_anual.csv", encoding="utf-8")
    destinos = pd.read_csv(
        REFERENCIA / "destinos.csv",
        encoding="utf-8",
        dtype={"municipios_cvegeo": str, "cabecera_cvegeo": str},
    )
    oferta = pd.read_csv(
        CURADO / "oferta_denue_municipio.csv", encoding="utf-8", dtype={"municipio_cvegeo": str}
    )
    poi = pd.read_csv(CURADO / "poi.csv", encoding="utf-8", dtype={"municipio_cvegeo": str})
    acc = pd.read_csv(CURADO / "poi_accesibilidad.csv", encoding="utf-8")
    fuentes = pd.read_csv(FUENTES, encoding="utf-8")
    geo = json.loads((REFERENCIA / "geo" / "municipios-puebla.geojson").read_text("utf-8"))
    municipios = {f["properties"]["cvegeo"]: f["properties"]["nomgeo"] for f in geo["features"]}
    return {
        "anual": anual,
        "destinos": destinos,
        "oferta": oferta,
        "poi": poi,
        "acc": acc,
        "fuentes": fuentes,
        "municipios": municipios,
    }


def grupo_de(destino_id: str, pm: dict) -> str:
    if destino_id == CAPITAL:
        return "capital"
    if destino_id == CHOLULA:
        return "cholula"
    if pm.get(destino_id, False):
        return "pueblo_magico"
    return "otro"


# ---------------------------------------------------------------- A) demanda


def analisis_a(d: dict) -> dict:
    anual = d["anual"]
    pm = dict(zip(d["destinos"]["destino_id"], d["destinos"]["pueblo_magico"], strict=True))
    nombres = dict(zip(d["destinos"]["destino_id"], d["destinos"]["nombre"], strict=True))

    estado = anual[anual["centro_ot"] == "Estado"].set_index("anio")
    centros = anual[anual["nivel"] == "destino"].copy()
    centros["grupo"] = centros["destino_id"].map(lambda x: grupo_de(x, pm))
    resto = anual[anual["centro_ot"] == "Resto del Estado"].copy()
    resto["destino_id"] = "resto-del-estado"
    resto["grupo"] = "resto"
    filas = pd.concat([centros, resto], ignore_index=True)
    filas["nombre"] = filas["destino_id"].map(nombres).fillna(filas["centro_ot"])
    filas["llegadas_estado"] = filas["anio"].map(estado["llegadas_turistas"])
    filas["participacion_estado"] = filas["llegadas_turistas"] / filas["llegadas_estado"]

    # Comprobación: los centros más «Resto del Estado» suman el Estado.
    suma = filas.groupby("anio")["llegadas_turistas"].sum()
    dif = (suma - estado["llegadas_turistas"]).abs().max()
    if dif > 1:
        raise RuntimeError(f"Los centros no suman el Estado (diferencia {dif})")

    part = filas[
        [
            "anio",
            "meses",
            "destino_id",
            "nombre",
            "grupo",
            "llegadas_turistas",
            "llegadas_estado",
            "participacion_estado",
        ]
    ].sort_values(["anio", "llegadas_turistas", "destino_id"], ascending=[True, False, True])
    escribir_csv(part, "013_participacion_llegadas.csv")

    # Panel fijo: centros con dato en todos los años.
    cuenta = centros.groupby("destino_id")["anio"].nunique()
    panel = sorted(cuenta[cuenta == len(ANIOS)].index)
    fuera_panel = sorted(set(centros["destino_id"]) - set(panel))

    conc = []
    for anio in ANIOS:
        c = centros[centros["anio"] == anio]
        p = c[c["destino_id"].isin(panel)]
        tot = estado.loc[anio, "llegadas_turistas"]
        g = c.groupby("grupo")["llegadas_turistas"].sum()
        conc.append(
            {
                "anio": anio,
                "meses": int(estado.loc[anio, "meses"]),
                "llegadas_estado": tot,
                "part_capital": g.get("capital", 0) / tot,
                "part_cholula": g.get("cholula", 0) / tot,
                "part_capital_cholula": (g.get("capital", 0) + g.get("cholula", 0)) / tot,
                "part_pueblos_magicos_sin_cholula": g.get("pueblo_magico", 0) / tot,
                "part_otros_centros": g.get("otro", 0) / tot,
                "part_resto_estado": resto.set_index("anio").loc[anio, "llegadas_turistas"] / tot,
                "n_centros_panel": len(p),
                "hhi_panel": hhi(p["llegadas_turistas"]),
                "hhi_panel_10000": 10000 * hhi(p["llegadas_turistas"]),
                "hhi_igualdad_panel": 1 / len(p),
                "gini_panel": gini(p["llegadas_turistas"]),
            }
        )
    conc = pd.DataFrame(conc)
    escribir_csv(conc, "013_concentracion_anual.csv")

    # Ocupación y estadía por centro, más el agregado de Pueblos Mágicos sin Cholula.
    oe = filas[filas["grupo"] != "resto"][
        [
            "anio",
            "meses",
            "destino_id",
            "nombre",
            "grupo",
            "ocupacion_pct",
            "estadia_promedio_dias",
            "cuartos_disponibles",
            "cuartos_ocupados",
            "llegadas_turistas",
            "turistas_noche",
            "cuartos_libres_por_dia",
        ]
    ].copy()
    agregados = []
    for anio in ANIOS:
        sub = oe[(oe["anio"] == anio) & (oe["grupo"] == "pueblo_magico")]
        e = estado.loc[anio]
        for did, nom, s in [
            ("pueblos-magicos-sin-cholula", "Pueblos Mágicos sin Cholula (11)", sub),
            ("estado", "Estado", None),
        ]:
            if s is None:
                cd, co = e["cuartos_disponibles"], e["cuartos_ocupados"]
                ll, tn, libres = e["llegadas_turistas"], e["turistas_noche"], None
                meses = int(e["meses"])
            else:
                cd, co = s["cuartos_disponibles"].sum(), s["cuartos_ocupados"].sum()
                ll, tn = s["llegadas_turistas"].sum(), s["turistas_noche"].sum()
                libres = s["cuartos_libres_por_dia"].sum()
                meses = int(s["meses"].max())
            agregados.append(
                {
                    "anio": anio,
                    "meses": meses,
                    "destino_id": did,
                    "nombre": nom,
                    "grupo": "agregado",
                    "ocupacion_pct": 100 * co / cd,
                    "estadia_promedio_dias": tn / ll,
                    "cuartos_disponibles": cd,
                    "cuartos_ocupados": co,
                    "llegadas_turistas": ll,
                    "turistas_noche": tn,
                    "cuartos_libres_por_dia": libres,
                }
            )
    oe = pd.concat([oe, pd.DataFrame(agregados)], ignore_index=True)
    oe = oe.sort_values(["destino_id", "anio"]).reset_index(drop=True)
    escribir_csv(oe, "013_ocupacion_estadia.csv")

    return {"part": part, "conc": conc, "oe": oe, "panel": panel, "fuera_panel": fuera_panel}


def figura_participacion(a: dict, f_ot: dict) -> None:
    p = a["part"]
    p = p[p["anio"] == ANIO_REF].sort_values("participacion_estado")
    fig, ax = plt.subplots(figsize=(8, 6.6))
    y = range(len(p))
    for i, (_, r) in enumerate(p.iterrows()):
        _, color, trama = GRUPOS[r["grupo"]]
        ax.barh(i, 100 * r["participacion_estado"], color=color, hatch=trama, height=0.72, lw=0)
        ax.text(
            100 * r["participacion_estado"] + 0.6,
            i,
            fmt_pct(r["participacion_estado"]),
            va="center",
            fontsize=8.5,
            color=TEXTO,
        )
    ax.set_yticks(list(y), p["nombre"], fontsize=9)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 100 * p["participacion_estado"].max() + 8)
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    ax.set_xlabel(f"% de las llegadas de turistas a hotel del Estado, {ANIO_REF}")
    cc = a["conc"].set_index("anio").loc[ANIO_REF, "part_capital_cholula"]
    ax.set_title(
        f"La capital y Cholula reciben {fmt_pct(cc, 0)} de las llegadas a hotel ({ANIO_REF})",
        pad=12,
    )
    ax.legend(
        handles=[
            Patch(facecolor=AZUL, label="Capital y Cholula"),
            Patch(facecolor=NARANJA, hatch=TRAMA_PM, label="Pueblo Mágico"),
            Patch(facecolor=GRIS, hatch=TRAMA_OTRO, label="Otro centro / resto"),
        ],
        loc="lower right",
        frameon=False,
        fontsize=9,
    )
    fig.subplots_adjust(left=0.24, right=0.97, top=0.92, bottom=0.13)
    pie(
        fig,
        f"Fuente: DataTur vía Observatorio Turístico del Estado de Puebla, datos a junio 2026, "
        f"consultado el {f_ot['fecha']}. Denominador: llegadas del Estado en {ANIO_REF} "
        f"({fmt_entero(p['llegadas_estado'].iloc[0])}). Solo hoteles registrados.",
    )
    guardar(fig, "013_participacion_llegadas_2025")


def figura_serie_concentracion(a: dict, f_ot: dict) -> None:
    c = a["conc"]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    series = [
        ("part_capital_cholula", "Capital y Cholula", AZUL, "-", "o"),
        ("part_pueblos_magicos_sin_cholula", "11 Pueblos Mágicos", NARANJA, "--", "^"),
        ("part_resto_estado", "Otros centros y resto", GRIS, ":", "s"),
    ]
    c = c.assign(part_resto_estado=c["part_resto_estado"] + c["part_otros_centros"])
    finales = []
    for col, etiqueta, color, estilo, marca in series:
        ax.plot(c["anio"], 100 * c[col], color=color, ls=estilo, lw=2, marker=marca, ms=6)
        finales.append((100 * c[col].iloc[-1], etiqueta))
    finales.sort()
    pos = []
    for v, _ in finales:
        pos.append(max(v, pos[-1] + 6) if pos else v)
    for (v, etiqueta), yy in zip(finales, pos, strict=True):
        ax.text(ANIO_PARCIAL + 0.15, yy, f"{etiqueta} {v:.0f} %", va="center", fontsize=8.5)
    ax.set_xticks(ANIOS, [str(x) if x != ANIO_PARCIAL else f"{x}\n(ene–jun)" for x in ANIOS])
    ax.set_xlim(2016.6, 2029.2)
    ax.set_ylim(0, 100)
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    ax.set_ylabel("% de las llegadas a hotel del Estado")
    arriba = c.loc[c["part_capital_cholula"] > 0.5, "anio"].tolist()
    desde = arriba[0] if arriba else None
    if desde is not None and arriba == list(range(desde, ANIOS[-1] + 1)):
        titulo = f"Desde {desde}, la capital y Cholula reciben más de la mitad de las llegadas"
    else:
        titulo = "Participación en las llegadas a hotel del Estado"
    ax.set_title(titulo, pad=12)
    fig.subplots_adjust(left=0.09, right=0.97, top=0.9, bottom=0.2)
    pie(
        fig,
        f"Fuente: DataTur vía Observatorio Turístico del Estado de Puebla, consultado el "
        f"{f_ot['fecha']}. {ANIO_PARCIAL}: solo enero a junio.",
    )
    guardar(fig, "013_concentracion_serie")


def figura_ocupacion(a: dict, f_ot: dict) -> None:
    oe = a["oe"]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    series = [
        (CAPITAL, "Capital", AZUL, "-", "o"),
        (CHOLULA, "Cholula", AZUL, "--", "D"),
        ("estado", "Estado", TEXTO_2, ":", "s"),
        ("pueblos-magicos-sin-cholula", "11 Pueblos Mágicos", NARANJA, "-", "^"),
    ]
    finales = []
    for did, etiqueta, color, estilo, marca in series:
        s = oe[oe["destino_id"] == did].sort_values("anio")
        ax.plot(s["anio"], s["ocupacion_pct"], color=color, ls=estilo, lw=2, marker=marca, ms=6)
        finales.append((s["ocupacion_pct"].iloc[-1], etiqueta))
    # Etiquetas finales sin encimarse.
    finales.sort()
    pos = []
    for v, _ in finales:
        pos.append(max(v, pos[-1] + 3.2) if pos else v)
    for (v, etiqueta), yy in zip(finales, pos, strict=True):
        ax.text(ANIO_PARCIAL + 0.15, yy, f"{etiqueta} {fmt_num(v)} %", va="center", fontsize=8.5)
    ax.set_xticks(ANIOS, [str(x) if x != ANIO_PARCIAL else f"{x}\n(ene–jun)" for x in ANIOS])
    ax.set_xlim(2016.6, 2029.2)
    ax.set_ylim(0, 80)
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    ax.set_ylabel("Ocupación hotelera anual (%)")
    ax.set_title("Los Pueblos Mágicos llenan menos cuartos que la capital y Cholula", pad=12)
    fig.subplots_adjust(left=0.09, right=0.97, top=0.9, bottom=0.2)
    pie(
        fig,
        f"Fuente: DataTur vía Observatorio Turístico del Estado de Puebla, consultado el "
        f"{f_ot['fecha']}. Ocupación = cuartos ocupados / cuartos disponibles. "
        "Pueblos Mágicos: suma de los 11 sin Cholula. 2020: pandemia.",
    )
    guardar(fig, "013_ocupacion_serie")


# ---------------------------------------------------------------- B) oferta


def analisis_b(d: dict) -> dict:
    oferta = d["oferta"]
    municipios = d["municipios"]
    destinos = d["destinos"]
    mun_destino = {}
    for _, r in destinos.iterrows():
        for m in str(r["municipios_cvegeo"]).split(";"):
            mun_destino[m] = r["destino_id"]

    ancho = (
        oferta.pivot_table(
            index="municipio_cvegeo",
            columns="rama",
            values="establecimientos",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )
    ramas = [
        "alojamiento",
        "alimentos_y_bebidas",
        "museos_y_sitios_historicos",
        "agencias_de_viajes",
    ]
    for r in ramas:
        if r not in ancho:
            ancho[r] = 0
    ancho["total"] = ancho[ramas].sum(axis=1)
    ancho["municipio"] = ancho["municipio_cvegeo"].map(municipios).fillna("sin nombre")
    ancho["destino_id"] = ancho["municipio_cvegeo"].map(mun_destino).fillna("")
    tot_estado = ancho["total"].sum()
    ancho["participacion_total"] = ancho["total"] / tot_estado
    for r in ramas:
        ancho[f"participacion_{r}"] = ancho[r] / ancho[r].sum()
    ancho = ancho[
        ["municipio_cvegeo", "municipio", "destino_id", *ramas, "total", "participacion_total"]
        + [f"participacion_{r}" for r in ramas]
    ].sort_values(["total", "municipio_cvegeo"], ascending=[False, True])
    escribir_csv(ancho, "013_oferta_denue_municipio.csv")

    scian = dict(zip(oferta["rama"], oferta["scian_prefijo"], strict=False))
    filas = []
    for r in [*ramas, "total"]:
        v = ancho.set_index("municipio_cvegeo")[r]
        tot = v.sum()
        cap = v.reindex(MUN_CAPITAL).fillna(0).sum()
        cho = v.reindex(MUN_CHOLULA).fillna(0).sum()
        filas.append(
            {
                "rama": r,
                "scian_prefijo": scian.get(r, "7211|7225|7121|5615"),
                "establecimientos_estado": tot,
                "municipios_con_al_menos_uno": int((v > 0).sum()),
                "part_capital": cap / tot,
                "part_cholula": cho / tot,
                "part_capital_cholula": (cap + cho) / tot,
                "part_top5_municipios": v.sort_values(ascending=False).head(5).sum() / tot,
                "hhi_municipios": hhi(v[v > 0]),
            }
        )
    conc = pd.DataFrame(filas)
    escribir_csv(conc, "013_concentracion_oferta.csv")

    poi = d["poi"]
    sic = poi[poi["sic_id"].notna()]
    nombres = dict(zip(destinos["destino_id"], destinos["nombre"], strict=True))
    tabla_sic = (
        sic.pivot_table(
            index="destino_id", columns="categoria", values="poi_id", aggfunc="count", fill_value=0
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )
    cats = [c for c in tabla_sic.columns if c != "destino_id"]
    tabla_sic["recintos_sic"] = tabla_sic[cats].sum(axis=1)
    tabla_sic["poi_en_zona"] = tabla_sic["destino_id"].map(poi["destino_id"].value_counts())
    tabla_sic["nombre"] = tabla_sic["destino_id"].map(nombres)
    tabla_sic = tabla_sic[["destino_id", "nombre", *sorted(cats), "recintos_sic", "poi_en_zona"]]
    tabla_sic = tabla_sic.sort_values(["recintos_sic", "destino_id"], ascending=[False, True])
    escribir_csv(tabla_sic, "013_recintos_sic_destino.csv")
    return {"ancho": ancho, "conc": conc, "sic": tabla_sic, "ramas": ramas}


def figura_oferta(b: dict, a: dict, f_denue: dict, f_ot: dict) -> None:
    conc = b["conc"].set_index("rama")
    etiquetas = {
        "alojamiento": "Alojamiento (SCIAN 7211)",
        "alimentos_y_bebidas": "Alimentos y bebidas (7225)",
        "museos_y_sitios_historicos": "Museos y sitios históricos (7121)",
        "agencias_de_viajes": "Agencias de viajes (5615)",
    }
    filas = [(etiquetas[r], conc.loc[r, "part_capital_cholula"]) for r in b["ramas"]]
    llegadas = a["conc"].set_index("anio").loc[ANIO_REF, "part_capital_cholula"]
    filas.append((f"Llegadas a hotel {ANIO_REF} (referencia)", llegadas))
    fig, ax = plt.subplots(figsize=(8, 4.2))
    for i, (_, v) in enumerate(reversed(filas)):
        es_ref = i == 0
        ax.barh(
            i,
            100 * v,
            color=GRIS if es_ref else AZUL,
            hatch=TRAMA_OTRO if es_ref else "",
            height=0.66,
            lw=0,
        )
        ax.text(100 * v + 1, i, fmt_pct(v), va="center", fontsize=9)
    ax.set_yticks(range(len(filas)), [f[0] for f in reversed(filas)], fontsize=9)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 100)
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    ax.set_xlabel("% del Estado en los municipios de Puebla, San Andrés y San Pedro Cholula")
    ax.set_title("Oferta registrada en Puebla, San Andrés y San Pedro Cholula", pad=12)
    fig.subplots_adjust(left=0.36, right=0.97, top=0.88, bottom=0.2)
    pie(
        fig,
        f"Fuente: DENUE 05_2026, INEGI, consultado el {f_denue['fecha']}; DataTur vía "
        f"Observatorio Turístico, consultado el {f_ot['fecha']}. Denominador: establecimientos "
        "de cada rama en todos los municipios de Puebla.",
    )
    guardar(fig, "013_oferta_concentracion")


# ---------------------------------------------------------------- C) desajuste


def analisis_c(d: dict, a: dict, b: dict) -> dict:
    destinos = d["destinos"]
    ancho = b["ancho"].set_index("municipio_cvegeo")
    sic = b["sic"].set_index("destino_id")["recintos_sic"]
    oe = a["oe"]
    oe_ref = oe[oe["anio"] == ANIO_REF].set_index("destino_id")
    part = a["part"]
    part_ref = part[part["anio"] == ANIO_REF].set_index("destino_id")
    ocup_estado = oe_ref.loc["estado", "ocupacion_pct"]

    filas = []
    for _, r in destinos.iterrows():
        did = r["destino_id"]
        muns = str(r["municipios_cvegeo"]).split(";")
        denue = ancho.reindex(muns).fillna(0)
        if did not in oe_ref.index:
            continue
        o = oe_ref.loc[did]
        museos = int(denue["museos_y_sitios_historicos"].sum())
        recintos = int(sic.get(did, 0))
        filas.append(
            {
                "destino_id": did,
                "nombre": r["nombre"],
                "pueblo_magico": bool(r["pueblo_magico"]),
                "municipios_cvegeo": r["municipios_cvegeo"],
                "denue_museos_sitios_7121": museos,
                "recintos_sic_zona": recintos,
                "oferta_cultural_registrada": museos + recintos,
                "denue_alojamiento_7211": int(denue["alojamiento"].sum()),
                "llegadas_2025": o["llegadas_turistas"],
                "participacion_llegadas_2025": part_ref.loc[did, "participacion_estado"],
                "ocupacion_2025": o["ocupacion_pct"],
                "ocupacion_estado_2025": ocup_estado,
                "diferencia_ocupacion_pp": o["ocupacion_pct"] - ocup_estado,
                "estadia_2025": o["estadia_promedio_dias"],
                "cuartos_libres_por_dia_2025": o["cuartos_libres_por_dia"],
            }
        )
    t = pd.DataFrame(filas)
    t["oferta_cultural_relevante"] = t["pueblo_magico"] & (t["oferta_cultural_registrada"] >= 1)
    t["baja_demanda"] = t["ocupacion_2025"] < t["ocupacion_estado_2025"]
    t["candidato_destino_alternativo"] = t["oferta_cultural_relevante"] & t["baja_demanda"]
    t = t.sort_values(
        ["candidato_destino_alternativo", "oferta_cultural_registrada", "ocupacion_2025"],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    t.insert(0, "orden", range(1, len(t) + 1))
    escribir_csv(t, "013_desajuste_destinos.csv")
    return {"t": t, "ocup_estado": ocup_estado}


def figura_desajuste(c: dict, f_ot: dict, f_denue: dict, f_sic: dict) -> None:
    t = c["t"].sort_values(["ocupacion_2025", "destino_id"])
    fig, ax = plt.subplots(figsize=(8.4, 7.2))
    x_etiqueta = 63
    for i, (_, r) in enumerate(t.iterrows()):
        borde, lw = "none", 0
        if r["destino_id"] in (CAPITAL, CHOLULA):
            color, trama = AZUL, ""
        elif r["candidato_destino_alternativo"]:
            color, trama = NARANJA, TRAMA_PM
        elif r["pueblo_magico"]:
            color, trama, borde, lw = SUPERFICIE, "", NARANJA, 1.6
        else:
            color, trama = GRIS, TRAMA_OTRO
        ax.barh(
            i, r["ocupacion_2025"], color=color, hatch=trama, height=0.72, lw=lw, edgecolor=borde
        )
        n = int(r["oferta_cultural_registrada"])
        ax.text(
            x_etiqueta,
            i,
            f"{fmt_num(r['ocupacion_2025'])} %  ·  {n} {'recinto' if n == 1 else 'recintos'}",
            va="center",
            fontsize=8.2,
        )
    ax.axvline(c["ocup_estado"], color=TEXTO, lw=1.2, ls="--")
    ax.text(
        c["ocup_estado"] - 0.8,
        len(t) - 0.3,
        f"Estado {fmt_num(c['ocup_estado'])} %",
        ha="right",
        va="bottom",
        fontsize=8.5,
    )
    ax.text(
        x_etiqueta,
        len(t) - 0.3,
        "Ocupación · recintos culturales",
        fontsize=8.2,
        color=TEXTO_2,
        va="bottom",
    )
    ax.set_yticks(range(len(t)), t["nombre"], fontsize=9)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 90)
    ax.set_xticks([0, 10, 20, 30, 40, 50, 60])
    ax.set_ylim(-0.7, len(t) + 0.6)
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    ax.spines["bottom"].set_bounds(0, 60)
    ax.set_xlabel(f"Ocupación hotelera {ANIO_REF} (%)")
    n = int(t["candidato_destino_alternativo"].sum())
    ax.set_title(
        f"{n} Pueblos Mágicos con oferta cultural y ocupación menor a la estatal",
        pad=12,
        fontsize=11,
    )
    ax.legend(
        handles=[
            Patch(facecolor=AZUL, label="Capital y Cholula"),
            Patch(facecolor=NARANJA, hatch=TRAMA_PM, label="Candidato a destino alternativo"),
            Patch(
                facecolor=SUPERFICIE, edgecolor=NARANJA, lw=1.6, label="Pueblo Mágico, no candidato"
            ),
            Patch(facecolor=GRIS, hatch=TRAMA_OTRO, label="Otro centro"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.4, -0.08),
        ncol=2,
        frameon=False,
        fontsize=8.5,
    )
    fig.subplots_adjust(left=0.22, right=0.98, top=0.93, bottom=0.2)
    pie(
        fig,
        f"Recintos = museos y sitios históricos del DENUE (municipio, consultado el "
        f"{f_denue['fecha']}) + recintos del SIC en la zona del catálogo (consultado el "
        f"{f_sic['fecha']}); puede contar dos veces un mismo lugar. Ocupación: DataTur vía "
        f"Observatorio Turístico, consultado el {f_ot['fecha']}.",
    )
    guardar(fig, "013_desajuste_ocupacion_oferta")


# ---------------------------------------------------------------- D) accesibilidad


def analisis_d(d: dict) -> dict:
    poi = d["poi"].copy()
    acc = d["acc"]
    nombres = dict(zip(d["destinos"]["destino_id"], d["destinos"]["nombre"], strict=True))
    con_algo = set(acc["poi_id"])
    sin_escalones = acc[acc["atributo"] == "acceso_sin_escalones"].set_index("poi_id")["valor"]
    banio = set(acc.loc[acc["atributo"] == "banio_accesible", "poi_id"])
    poi["con_atributo"] = poi["poi_id"].isin(con_algo)
    poi["con_acceso_sin_escalones"] = poi["poi_id"].isin(sin_escalones.index)
    poi["valor_sin_escalones"] = poi["poi_id"].map(sin_escalones).fillna("")
    poi["con_osm"] = poi["osm_id"].notna()
    poi["zona"] = poi["corredor_id"].fillna(poi["destino_id"])

    def resumen(g: pd.DataFrame) -> pd.Series:
        return pd.Series(
            {
                "poi": len(g),
                "poi_con_osm": int(g["con_osm"].sum()),
                "con_algun_atributo": int(g["con_atributo"].sum()),
                "cobertura_informacion": g["con_atributo"].mean(),
                "cobertura_sobre_poi_osm": (
                    g["con_atributo"].sum() / g["con_osm"].sum() if g["con_osm"].sum() else None
                ),
                "con_dato_acceso_sin_escalones": int(g["con_acceso_sin_escalones"].sum()),
                "sin_escalones_si": int((g["valor_sin_escalones"] == "si").sum()),
                "sin_escalones_parcial": int((g["valor_sin_escalones"] == "parcial").sum()),
                "sin_escalones_no": int((g["valor_sin_escalones"] == "no").sum()),
                "sin_dato": int((~g["con_atributo"]).sum()),
            }
        )

    por_zona = []
    for zona, g in poi.groupby("zona", sort=True):
        fila = resumen(g)
        fila["zona"] = zona
        fila["nombre"] = (
            "Corredor Puebla–Cholula" if zona == "puebla-cholula" else nombres.get(zona, zona)
        )
        por_zona.append(fila)
    total = resumen(poi)
    total["zona"] = "total"
    total["nombre"] = "Total del catálogo"
    por_zona.append(total)
    cols = ["zona", "nombre", *[c for c in total.index if c not in ("zona", "nombre")]]
    por_zona = pd.DataFrame(por_zona)[cols]
    escribir_csv(por_zona, "013_cobertura_accesibilidad_destino.csv")

    por_cat = []
    for cat, g in poi.groupby("categoria", sort=True):
        fila = resumen(g)
        fila["categoria"] = cat
        por_cat.append(fila)
    por_cat = pd.DataFrame(por_cat)[
        ["categoria", *[c for c in cols if c not in ("zona", "nombre")]]
    ]
    escribir_csv(por_cat, "013_cobertura_accesibilidad_categoria.csv")

    banios = poi[poi["categoria"] == "banio"]
    banios_con = int(banios["poi_id"].isin(banio).sum())
    return {
        "zona": por_zona,
        "cat": por_cat,
        "banios": len(banios),
        "banios_con": banios_con,
        "total": total,
    }


def figura_accesibilidad(dd: dict, f_osm: dict) -> None:
    z = dd["zona"]
    z = z[z["zona"] != "total"].sort_values(["cobertura_informacion", "poi"])
    fig, ax = plt.subplots(figsize=(8, 6))
    for i, (_, r) in enumerate(z.iterrows()):
        cob = r["cobertura_informacion"]
        ax.barh(i, 100, color=REJILLA, height=0.7, lw=0)
        ax.barh(
            i,
            100 * cob,
            color=AZUL if r["zona"] == "puebla-cholula" else NARANJA,
            hatch="" if r["zona"] == "puebla-cholula" else TRAMA_PM,
            height=0.7,
            lw=0,
        )
        ax.text(
            101.5,
            i,
            f"{fmt_pct(cob)}  ({fmt_entero(r['con_algun_atributo'])} de {fmt_entero(r['poi'])})",
            va="center",
            fontsize=8.5,
        )
    ax.set_yticks(range(len(z)), z["nombre"], fontsize=9)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 135)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Cobertura de información: % de lugares con algún dato de accesibilidad")
    t = dd["total"]
    ax.set_title(
        f"Solo {fmt_pct(t['cobertura_informacion'])} de los lugares tiene algún dato "
        "de accesibilidad",
        pad=12,
    )
    ax.legend(
        handles=[
            Patch(facecolor=AZUL, label="Con dato (corredor piloto)"),
            Patch(facecolor=NARANJA, hatch=TRAMA_PM, label="Con dato (Pueblo Mágico)"),
            Patch(facecolor=REJILLA, label="Sin dato: «sin verificar»"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.45, -0.1),
        ncol=3,
        frameon=False,
        fontsize=8.5,
    )
    fig.subplots_adjust(left=0.24, right=0.98, top=0.92, bottom=0.22)
    pie(
        fig,
        f"Fuente: catálogo de POI (spec 012) con OpenStreetMap (© OpenStreetMap contributors, "
        f"ODbL), SIC y DENUE, consultados el {f_osm['fecha']}. Mide cuánto se sabe, no qué tan "
        "accesibles son los lugares. Sin verificación del equipo.",
    )
    guardar(fig, "013_cobertura_accesibilidad")


# ---------------------------------------------------------------- reporte


def reporte(d: dict, a: dict, b: dict, c: dict, dd: dict) -> str:
    fu = d["fuentes"]
    f_ot = fuente(fu, "sectur-ot-2026-06")
    f_denue = fuente(fu, "inegi-denue")
    f_sic = fuente(fu, "sic-cultura")
    f_osm = fuente(fu, "osm-overpass")
    conc = a["conc"].set_index("anio")
    r25, r17 = conc.loc[ANIO_REF], conc.loc[2017]
    oe = a["oe"].set_index(["destino_id", "anio"])
    oc_cap = oe.loc[(CAPITAL, ANIO_REF), "ocupacion_pct"]
    oc_cho = oe.loc[(CHOLULA, ANIO_REF), "ocupacion_pct"]
    oc_pm = oe.loc[("pueblos-magicos-sin-cholula", ANIO_REF), "ocupacion_pct"]
    oc_est = oe.loc[("estado", ANIO_REF), "ocupacion_pct"]
    libres_pm = oe.loc[("pueblos-magicos-sin-cholula", ANIO_REF), "cuartos_libres_por_dia"]
    est25 = a["oe"][(a["oe"]["anio"] == ANIO_REF) & (a["oe"]["grupo"] != "agregado")]
    est_min, est_max = est25["estadia_promedio_dias"].min(), est25["estadia_promedio_dias"].max()
    oc_min_pm = (
        a["oe"][(a["oe"]["anio"] == ANIO_REF) & (a["oe"]["grupo"] == "pueblo_magico")]
        .sort_values("ocupacion_pct")
        .iloc[0]
    )
    serie = a["conc"][(a["conc"]["anio"] >= 2018) & (a["conc"]["anio"] <= ANIO_REF)]
    hhi_min = a["conc"].loc[a["conc"]["hhi_panel"].idxmin()]
    hhi_max = a["conc"].loc[a["conc"]["hhi_panel"].idxmax()]

    oc_b = b["conc"].set_index("rama")
    t = c["t"]
    cand = t[t["candidato_destino_alternativo"]]
    n_pm = int(t["pueblo_magico"].sum()) - 1  # sin Cholula
    pm_bajo = t[t["pueblo_magico"] & (t["destino_id"] != CHOLULA) & t["baja_demanda"]]

    zt = dd["total"]
    zc = dd["zona"].set_index("zona").loc["puebla-cholula"]
    pm_zonas = dd["zona"][~dd["zona"]["zona"].isin(["puebla-cholula", "total"])]
    pm_sin_dato = int((pm_zonas["con_algun_atributo"] == 0).sum())
    pm_poi = int(pm_zonas["poi"].sum())
    pm_con = int(pm_zonas["con_algun_atributo"].sum())

    lin = []
    w = lin.append
    w("# Análisis del problema · Evidencia con datos")
    w("")
    w(
        "Generado por `analysis/01_problema.py` (spec 013) desde `data/curado/` y "
        "`data/referencia/`. No se edita a mano. Para regenerarlo:"
    )
    w("")
    w("```")
    w("uv run --project pipelines --extra analisis python analysis/01_problema.py")
    w("```")
    w("")
    w(
        f"Año de referencia: {ANIO_REF} (último año completo). {ANIO_PARCIAL} solo tiene enero a "
        "junio y se muestra aparte. Las tablas están en `reports/013_*.csv` y las figuras en "
        "`reports/figuras/`."
    )
    w("")

    # Cifras clave
    w("## Cifras clave para el pitch")
    w("")
    w(
        f"1. **{fmt_pct(r25['part_capital_cholula'])}** de las llegadas de turistas a hotel del "
        f"Estado en {ANIO_REF} fueron a la capital y Cholula "
        f"({fmt_entero(r25['llegadas_estado'] * r25['part_capital_cholula'])} de "
        f"{fmt_entero(r25['llegadas_estado'])}). Los 11 Pueblos Mágicos restantes recibieron "
        f"{fmt_pct(r25['part_pueblos_magicos_sin_cholula'])}. Fuente: DataTur vía Observatorio "
        f"Turístico (`{f_ot['id']}`), consultado el {f_ot['fecha']}."
    )
    w(
        f"2. **{fmt_num(oc_cap)} %** de ocupación hotelera en la capital y "
        f"**{fmt_num(oc_pm)} %** en el conjunto de los 11 Pueblos Mágicos sin Cholula "
        f"({ANIO_REF}): {fmt_num(oc_cap - oc_pm)} puntos de diferencia. Fuente: DataTur vía "
        f"Observatorio Turístico (`{f_ot['id']}`), consultado el {f_ot['fecha']}."
    )
    w(
        f"3. **{len(cand)} de {n_pm}** Pueblos Mágicos (sin Cholula) tienen oferta cultural "
        f"registrada y ocupación por debajo del promedio estatal ({fmt_num(oc_est)} %) en "
        f"{ANIO_REF}: candidatos a destino alternativo. Entre todos tuvieron en promedio "
        f"{fmt_entero(cand['cuartos_libres_por_dia_2025'].sum())} cuartos libres por día. "
        f"Fuentes: DataTur (`{f_ot['id']}`), DENUE (`{f_denue['id']}`) y SIC (`{f_sic['id']}`)."
    )
    w(
        f"4. **{fmt_pct(oc_b.loc['museos_y_sitios_historicos', 'part_capital_cholula'], 0)}** de "
        f"los museos y sitios históricos y "
        f"**{fmt_pct(oc_b.loc['alojamiento', 'part_capital_cholula'], 0)}** del alojamiento "
        f"registrados en el DENUE del Estado están en los municipios de Puebla, San Andrés y San "
        f"Pedro Cholula. Fuente: DENUE 05_2026, INEGI (`{f_denue['id']}`), consultado el "
        f"{f_denue['fecha']}."
    )
    w(
        f"5. **{fmt_pct(zt['cobertura_informacion'])}** de los "
        f"{fmt_entero(zt['poi'])} lugares del catálogo tiene algún dato de accesibilidad en "
        f"fuentes abiertas ({fmt_entero(zt['con_algun_atributo'])} lugares). En {pm_sin_dato} de "
        f"las {len(pm_zonas)} zonas de Pueblos Mágicos no hay ninguno. Es cobertura de "
        f"información, no nivel de accesibilidad. Fuente: OpenStreetMap (`{f_osm['id']}`), "
        f"consultado el {f_osm['fecha']}."
    )
    w(
        f"6. **{dd['banios_con']} de {dd['banios']}** sanitarios públicos del catálogo dice si su "
        f"baño es accesible. Fuente: OpenStreetMap (`{f_osm['id']}`), consultado el "
        f"{f_osm['fecha']}."
    )
    w("")

    # A
    w("## A) Concentración de la demanda hotelera")
    w("")
    w("**Hallazgos**")
    w("")
    w(
        f"- En {ANIO_REF}, la capital recibió {fmt_pct(r25['part_capital'])} de las llegadas a "
        f"hotel del Estado y Cholula {fmt_pct(r25['part_cholula'])}. Juntas, "
        f"{fmt_pct(r25['part_capital_cholula'])}."
    )
    w(
        f"- En 2017 esa proporción era {fmt_pct(r17['part_capital_cholula'])}. Entre 2018 y "
        f"{ANIO_REF} osciló entre {fmt_pct(serie['part_capital_cholula'].min())} y "
        f"{fmt_pct(serie['part_capital_cholula'].max())}."
    )
    w(
        f"- Los 11 Pueblos Mágicos sin Cholula pasaron de "
        f"{fmt_pct(r17['part_pueblos_magicos_sin_cholula'])} (2017) a "
        f"{fmt_pct(r25['part_pueblos_magicos_sin_cholula'])} ({ANIO_REF}) de las llegadas, y "
        f"«Resto del Estado» bajó de {fmt_pct(r17['part_resto_estado'])} a "
        f"{fmt_pct(r25['part_resto_estado'])}. Con estos datos no se puede separar cuánto es "
        "crecimiento real y cuánto cambio en los hoteles que mide cada centro."
    )
    w(
        f"- HHI de las llegadas entre los {int(r25['n_centros_panel'])} centros con serie "
        f"completa: {fmt_num(r25['hhi_panel_10000'], 0)} en {ANIO_REF} (escala 0–10,000; con "
        f"reparto igual sería {fmt_num(10000 * r25['hhi_igualdad_panel'], 0)}). Mínimo "
        f"{fmt_num(hhi_min['hhi_panel_10000'], 0)} en {int(hhi_min['anio'])}, máximo "
        f"{fmt_num(hhi_max['hhi_panel_10000'], 0)} en {int(hhi_max['anio'])}. Gini "
        f"{ANIO_REF}: {fmt_num(r25['gini_panel'], 2)}."
    )
    w(
        f"- Ocupación {ANIO_REF}: capital {fmt_num(oc_cap)} %, Cholula {fmt_num(oc_cho)} %, "
        f"Estado {fmt_num(oc_est)} %, 11 Pueblos Mágicos juntos {fmt_num(oc_pm)} %. La más baja "
        f"entre los Pueblos Mágicos: {oc_min_pm['nombre']} "
        f"({fmt_num(oc_min_pm['ocupacion_pct'])} %)."
    )
    w(
        f"- Los 11 Pueblos Mágicos sin Cholula tuvieron en promedio "
        f"{fmt_entero(libres_pm)} cuartos libres por día en {ANIO_REF}."
    )
    w(
        f"- La estadía promedio va de {fmt_num(est_min, 2)} a {fmt_num(est_max, 2)} días en todos "
        "los centros: no distingue destinos."
    )
    w("")
    tabla = a["part"][a["part"]["anio"] == ANIO_REF].merge(
        a["oe"][a["oe"]["anio"] == ANIO_REF][
            ["destino_id", "ocupacion_pct", "estadia_promedio_dias"]
        ],
        on="destino_id",
        how="left",
    )
    tabla = pd.DataFrame(
        {
            "Centro": tabla["nombre"],
            "Grupo": tabla["grupo"].map(lambda g: GRUPOS[g][0]),
            f"Llegadas {ANIO_REF}": tabla["llegadas_turistas"].map(fmt_entero),
            "% del Estado": tabla["participacion_estado"].map(fmt_pct),
            "Ocupación %": tabla["ocupacion_pct"].map(lambda x: "—" if pd.isna(x) else fmt_num(x)),
            "Estadía (días)": tabla["estadia_promedio_dias"].map(
                lambda x: "—" if pd.isna(x) else fmt_num(x, 2)
            ),
        }
    )
    w(tabla_md(tabla))
    w("")
    w(
        "![Participación de llegadas 2025](figuras/013_participacion_llegadas_2025.svg)\n\n"
        "![Serie de concentración](figuras/013_concentracion_serie.svg)\n\n"
        "![Ocupación por grupo](figuras/013_ocupacion_serie.svg)"
    )
    w("")
    w(f"- **Fuente:** {cita(f_ot)}. Llegadas, ocupación y estadía son datos medidos (DataTur).")
    w(
        "- **Denominador:** llegadas de turistas a hotel del Estado por año "
        "(`centro_ot = Estado`, "
        f"igual a la suma de los centros más «Resto del Estado»). El HHI y el Gini usan el panel "
        f"fijo de {len(a['panel'])} centros con serie 2017–{ANIO_PARCIAL}; quedan fuera "
        f"{', '.join(a['fuera_panel'])} (serie desde 2025) y «Resto del Estado»."
    )
    w(
        "- **Limitaciones:** solo cuenta huéspedes de hoteles registrados; no incluye "
        "excursionistas, que en Cholula y en los Pueblos Mágicos cercanos pueden ser muchos, ni "
        "hospedaje informal o por plataformas. 2020 refleja la pandemia. El HHI depende de cuántos "
        "centros mide DataTur."
    )
    w("")

    # B
    w("## B) Concentración de la oferta")
    w("")
    w("**Hallazgos**")
    w("")
    ramas_txt = {
        "alojamiento": "alojamiento",
        "alimentos_y_bebidas": "alimentos y bebidas",
        "museos_y_sitios_historicos": "museos y sitios históricos",
        "agencias_de_viajes": "agencias de viajes",
    }
    for r in b["ramas"]:
        x = oc_b.loc[r]
        w(
            f"- {ramas_txt[r].capitalize()} (SCIAN {x['scian_prefijo']}): "
            f"{fmt_entero(x['establecimientos_estado'])} establecimientos en "
            f"{x['municipios_con_al_menos_uno']} municipios; "
            f"{fmt_pct(x['part_capital_cholula'])} en Puebla, San Andrés y San Pedro Cholula; "
            f"HHI entre municipios {fmt_num(10000 * x['hhi_municipios'], 0)}."
        )
    w(
        f"- Para comparar: esos tres municipios reciben {fmt_pct(r25['part_capital_cholula'])} de "
        f"las llegadas a hotel ({ANIO_REF})."
    )
    sic = b["sic"]
    sic_cap = int(sic.loc[sic["destino_id"].isin([CAPITAL, CHOLULA]), "recintos_sic"].sum())
    w(
        f"- Recintos del SIC en las zonas del catálogo: {int(sic['recintos_sic'].sum())}; "
        f"{sic_cap} en la capital y Cholula."
    )
    w("")
    top = b["ancho"].head(10)
    w(
        tabla_md(
            pd.DataFrame(
                {
                    "Municipio": top["municipio"],
                    "Alojamiento": top["alojamiento"].map(fmt_entero),
                    "Alimentos y bebidas": top["alimentos_y_bebidas"].map(fmt_entero),
                    "Museos y sitios": top["museos_y_sitios_historicos"].map(fmt_entero),
                    "Agencias": top["agencias_de_viajes"].map(fmt_entero),
                    "% del Estado": top["participacion_total"].map(fmt_pct),
                }
            )
        )
    )
    w("")
    w("![Concentración de la oferta](figuras/013_oferta_concentracion.svg)")
    w("")
    w(f"- **Fuentes:** {cita(f_denue)}; {cita(f_sic)}.")
    w(
        "- **Denominador:** establecimientos de cada rama en todos los municipios del Estado "
        "(DENUE); recintos del SIC dentro de las zonas del catálogo (corredor y círculos de 1.5 km "
        "de los Pueblos Mágicos)."
    )
    w(
        "- **Limitaciones:** el DENUE cuenta unidades económicas, no su tamaño ni su calidad; los "
        "establecimientos pequeños pueden estar desactualizados. Alimentos y bebidas incluye "
        "negocios de servicio local, no solo turístico. El SIC depende de que cada institución "
        "actualice su ficha y aquí solo se cuenta dentro de las zonas del catálogo."
    )
    w("")

    # C
    w("## C) Desajuste oferta–demanda")
    w("")
    w("**Criterio (explícito):** un destino es candidato a destino alternativo si cumple las dos:")
    w("")
    w(
        "1. Oferta cultural relevante: es Pueblo Mágico y tiene al menos un recinto cultural "
        "registrado (museo o sitio histórico del DENUE en su municipio, o recinto del SIC en su "
        "zona)."
    )
    w(
        f"2. Baja demanda hotelera: ocupación {ANIO_REF} menor que la del Estado "
        f"({fmt_num(oc_est)} %)."
    )
    w("")
    w(
        "Orden: primero los candidatos; dentro, por oferta cultural registrada (de más a menos) y "
        "luego por ocupación (de menos a más)."
    )
    w("")
    w("**Hallazgos**")
    w("")
    w(
        f"- {len(cand)} candidatos: {', '.join(cand['nombre'])}. Recibieron "
        f"{fmt_pct(cand['participacion_llegadas_2025'].sum())} de las llegadas a hotel en "
        f"{ANIO_REF} y tuvieron {fmt_entero(cand['cuartos_libres_por_dia_2025'].sum())} cuartos "
        "libres por día."
    )
    w(
        f"- {len(pm_bajo)} de {n_pm} Pueblos Mágicos sin Cholula están por debajo de la ocupación "
        "estatal."
    )
    no_c = t[t["pueblo_magico"] & ~t["candidato_destino_alternativo"]]
    if len(no_c):
        w(
            "- Pueblos Mágicos que no son candidatos y por qué: "
            + "; ".join(
                f"{r['nombre']} ("
                + (
                    "sin recinto cultural registrado"
                    if not r["oferta_cultural_relevante"]
                    else f"ocupación {fmt_num(r['ocupacion_2025'])} % ≥ Estado"
                )
                + ")"
                for _, r in no_c.iterrows()
            )
            + "."
        )
    w("")
    w(
        tabla_md(
            pd.DataFrame(
                {
                    "#": t["orden"],
                    "Destino": t["nombre"],
                    "Pueblo Mágico": t["pueblo_magico"].map({True: "sí", False: "no"}),
                    "Museos y sitios DENUE": t["denue_museos_sitios_7121"],
                    "Recintos SIC (zona)": t["recintos_sic_zona"],
                    f"Ocupación {ANIO_REF} %": t["ocupacion_2025"].map(fmt_num),
                    "Dif. vs. Estado (pp)": t["diferencia_ocupacion_pp"].map(lambda x: f"{x:+.1f}"),
                    "Estadía (días)": t["estadia_2025"].map(lambda x: fmt_num(x, 2)),
                    "Cuartos libres/día": t["cuartos_libres_por_dia_2025"].map(fmt_entero),
                    "Candidato": t["candidato_destino_alternativo"].map({True: "sí", False: "no"}),
                }
            )
        )
    )
    w("")
    w("![Desajuste oferta–demanda](figuras/013_desajuste_ocupacion_oferta.svg)")
    w("")
    w(f"- **Fuentes:** {cita(f_ot)}; {cita(f_denue)}; {cita(f_sic)}.")
    w(
        f"- **Denominador:** los {len(t)} destinos del catálogo (`data/referencia/destinos.csv`) "
        f"con centro turístico en DataTur; ocupación {ANIO_REF} de cada centro."
    )
    w(
        "- **Limitaciones:** es un cruce descriptivo, no una relación causal: la baja ocupación "
        "puede deberse a acceso, distancia, temporada o tamaño de la planta hotelera. El conteo de "
        "recintos mezcla el municipio (DENUE) y la zona (SIC) y puede contar dos veces un lugar. "
        "Ser Pueblo Mágico se toma como señal de valor cultural reconocido; no mide atractivo "
        "natural. La ocupación de referencia incluye a la capital, que la eleva."
    )
    w("")

    # D
    w("## D) Brecha de información de accesibilidad")
    w("")
    w(
        "Se reporta **cobertura de información**: cuántos lugares tienen algún dato de "
        "accesibilidad declarado en fuentes abiertas. No es el nivel de accesibilidad de los "
        "lugares. Un lugar sin dato queda «sin verificar»."
    )
    w("")
    w("**Hallazgos**")
    w("")
    w(
        f"- {fmt_entero(zt['con_algun_atributo'])} de {fmt_entero(zt['poi'])} lugares del catálogo "
        f"({fmt_pct(zt['cobertura_informacion'])}) tienen algún atributo de accesibilidad. Si se "
        f"cuentan solo los lugares que vienen de OpenStreetMap (única fuente con estas etiquetas), "
        f"son {fmt_entero(zt['con_algun_atributo'])} de {fmt_entero(zt['poi_con_osm'])} "
        f"({fmt_pct(zt['cobertura_sobre_poi_osm'])})."
    )
    w(
        f"- Corredor piloto Puebla–Cholula: {fmt_pct(zc['cobertura_informacion'])} "
        f"({fmt_entero(zc['con_algun_atributo'])} de {fmt_entero(zc['poi'])}). Zonas de Pueblos "
        f"Mágicos: {pm_con} de {fmt_entero(pm_poi)}; {pm_sin_dato} de {len(pm_zonas)} zonas sin "
        "ningún dato."
    )
    w(
        "- Dato de acceso sin escalones: "
        f"{fmt_entero(zt['con_dato_acceso_sin_escalones'])} lugares "
        f"(sí: {int(zt['sin_escalones_si'])}, parcial: {int(zt['sin_escalones_parcial'])}, "
        f"no: {int(zt['sin_escalones_no'])})."
    )
    w(
        f"- Sanitarios públicos con dato de baño accesible: {dd['banios_con']} de {dd['banios']} "
        f"({fmt_pct(dd['banios_con'] / dd['banios']) if dd['banios'] else 'sin denominador'})."
    )
    w("")
    zt_tab = dd["zona"]
    w(
        tabla_md(
            pd.DataFrame(
                {
                    "Zona": zt_tab["nombre"],
                    "Lugares": zt_tab["poi"].map(fmt_entero),
                    "Con algún dato": zt_tab["con_algun_atributo"].map(fmt_entero),
                    "Cobertura de información": zt_tab["cobertura_informacion"].map(fmt_pct),
                    "Sin dato («sin verificar»)": zt_tab["sin_dato"].map(fmt_entero),
                }
            )
        )
    )
    w("")
    ct = dd["cat"]
    w(
        tabla_md(
            pd.DataFrame(
                {
                    "Categoría": ct["categoria"],
                    "Lugares": ct["poi"].map(fmt_entero),
                    "Con algún dato": ct["con_algun_atributo"].map(fmt_entero),
                    "Cobertura de información": ct["cobertura_informacion"].map(fmt_pct),
                }
            )
        )
    )
    w("")
    w("![Cobertura de información de accesibilidad](figuras/013_cobertura_accesibilidad.svg)")
    w("")
    w(
        f"- **Fuentes:** {cita(f_osm)} (etiquetas `wheelchair`, `toilets:wheelchair` y otras); "
        "catálogo integrado de la spec 012 (`data/curado/poi.csv` y `poi_accesibilidad.csv`)."
    )
    w(
        "- **Denominador:** todos los lugares del catálogo de la zona o categoría; se da también "
        "la cobertura sobre los lugares con registro de OpenStreetMap."
    )
    w(
        "- **Limitaciones:** el SIC y el DENUE no publican accesibilidad, así que sus lugares sin "
        "enlace a OpenStreetMap no pueden tener dato. Las etiquetas de OpenStreetMap no están "
        "verificadas por el equipo. La ausencia de una etiqueta no prueba que el lugar sea o no "
        "accesible."
    )
    w("")

    # E y F
    w("## E) Población residente con discapacidad motriz (pendiente)")
    w("")
    w(
        "Sin datos. El Censo de Población y Vivienda 2020 por AGEB y manzana (INEGI, PCDISC_MOT) "
        "no está descargado en el repositorio. No se estima ni se sustituye. Se hará cuando una "
        "spec de ingesta lo registre en `data/fuentes/fuentes.csv`; se usará solo como contexto "
        "agregado de población residente, con las celdas suprimidas por INEGI tratadas como "
        "suprimidas, no como cero."
    )
    w("")
    w("## F) Pendiente del entorno peatonal (pendiente)")
    w("")
    w(
        "Sin datos. No hay un modelo digital de elevación (CEM de INEGI o Copernicus GLO-30) ni "
        "una red peatonal descargada. No se estima. Cuando exista, la resolución de 30 m no capta "
        "escalones ni banquetas y así se dirá."
    )
    w("")
    w("## Lectura honesta")
    w("")
    w(
        "- Estos resultados describen concentración y brechas de información. No prueban por qué "
        "ocurren: las hipótesis H1–H3 del proyecto siguen siendo hipótesis."
    )
    w(
        "- La serie hotelera solo ve a quien duerme en un hotel registrado. La afluencia de "
        "visitantes del Observatorio es un dato derivado (llegadas × factor fijo); por eso aquí "
        "se usan las llegadas, que son medidas."
    )
    w("")
    w(
        "Datos © OpenStreetMap contributors (ODbL 1.0). Directorios del Sistema de Información "
        "Cultural/Secretaría de Cultura. DENUE, INEGI. DataTur vía Observatorio Turístico del "
        "Estado de Puebla."
    )
    w("")
    return "\n".join(lin)


def main() -> None:
    REPORTES.mkdir(parents=True, exist_ok=True)
    FIGURAS.mkdir(parents=True, exist_ok=True)
    PITCH.mkdir(parents=True, exist_ok=True)
    d = cargar()
    fu = d["fuentes"]
    f_ot = fuente(fu, "sectur-ot-2026-06")
    f_denue = fuente(fu, "inegi-denue")
    f_sic = fuente(fu, "sic-cultura")
    f_osm = fuente(fu, "osm-overpass")

    a = analisis_a(d)
    b = analisis_b(d)
    c = analisis_c(d, a, b)
    dd = analisis_d(d)

    figura_participacion(a, f_ot)
    figura_serie_concentracion(a, f_ot)
    figura_ocupacion(a, f_ot)
    figura_oferta(b, a, f_denue, f_ot)
    figura_desajuste(c, f_ot, f_denue, f_sic)
    figura_accesibilidad(dd, f_osm)

    (REPORTES / "01_problema.md").write_text(
        reporte(d, a, b, c, dd), encoding="utf-8", newline="\n"
    )

    for nombre in [
        "013_participacion_llegadas_2025",
        "013_ocupacion_serie",
        "013_desajuste_ocupacion_oferta",
        "013_cobertura_accesibilidad",
    ]:
        for ext in ("svg", "png"):
            shutil.copyfile(FIGURAS / f"{nombre}.{ext}", PITCH / f"{nombre}.{ext}")
    print("Listo: reports/01_problema.md, reports/013_*.csv y reports/figuras/")


if __name__ == "__main__":
    main()
