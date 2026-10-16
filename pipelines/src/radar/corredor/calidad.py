"""Reporte de calidad del catálogo (`reports/calidad_datos.md`) y cifras del corredor piloto.

Todo lo que se escribe sale de las tablas: no hay cifras a mano. El reporte no lleva la hora
de la corrida para que dos corridas con los mismos insumos produzcan el mismo archivo.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from radar import catalogo, config
from radar.corredor import descargar, integrar, zonas

INICIO = "<!-- inicio:cifras (generado por `radar corredor reporte`; no editar a mano) -->"
FIN = "<!-- fin:cifras -->"


def _pct(parte: float, total: float) -> str:
    return f"{100 * parte / total:.1f} %" if total else "sin datos"


def _tabla(df: pd.DataFrame) -> str:
    columnas = [str(c) for c in df.columns]
    lineas = ["| " + " | ".join(columnas) + " |", "|" + "---|" * len(columnas)]
    for fila in df.itertuples(index=False):
        lineas.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in fila) + " |")
    return "\n".join(lineas)


def _fechas() -> str:
    partes = []
    for fuente in ("osm", "sic", "denue"):
        fechas = sorted({e.fecha_consulta for e in descargar.leer_manifiesto(fuente).values()})
        partes.append(f"{fuente.upper()}: {', '.join(fechas) or 'sin extracto'}")
    return "; ".join(partes)


def _nombres_destino() -> dict[str, str]:
    return {d.destino_id: d.nombre for d in catalogo.cargar()}


def cobertura(poi: pd.DataFrame, acc: pd.DataFrame) -> pd.DataFrame:
    """Por destino: POI, POI con algún atributo y con dato de acceso sin escalones."""
    con_algo = set(acc["poi_id"])
    con_acceso = set(acc.loc[acc["atributo"] == "acceso_sin_escalones", "poi_id"])
    filas = []
    nombres = _nombres_destino()
    grupos = [("Corredor Puebla–Cholula", poi[poi["corredor_id"] == zonas.CORREDOR_ID])]
    pm = poi[poi["corredor_id"] != zonas.CORREDOR_ID]
    grupos += [(nombres.get(d, d), g) for d, g in sorted(pm.groupby("destino_id"))]
    grupos.append(("Total", poi))
    for nombre, g in grupos:
        n = len(g)
        a = g["poi_id"].isin(con_algo).sum()
        b = g["poi_id"].isin(con_acceso).sum()
        filas.append(
            {
                "Zona": nombre,
                "POI": n,
                "Con algún atributo": int(a),
                "Cobertura de información": _pct(a, n),
                "Con dato de acceso sin escalones": int(b),
                "% acceso": _pct(b, n),
            }
        )
    return pd.DataFrame(filas)


def reporte(r: integrar.Resultado) -> str:
    poi, acc, est = r.poi, r.accesibilidad, r.estadisticas
    nombres = _nombres_destino()
    lineas = [
        "# Reporte de calidad de datos · Catálogo del corredor",
        "",
        "Generado por `uv run radar corredor reporte` desde los extractos de "
        "`data/fuentes/corredor/` (spec 012). No se edita a mano.",
        "",
        f"Fecha de consulta de los extractos: {_fechas()}.",
        "",
        "## Conteos por fuente",
        "",
    ]
    fuentes = pd.DataFrame(
        [
            {
                "Fuente": "OSM (Overpass)",
                "Registros leídos": est["osm_elementos"],
                "En el catálogo como POI propio": est["poi_osm"],
                "Enlazados a otro POI": "—",
            },
            {
                "Fuente": "SIC (Secretaría de Cultura), Puebla",
                "Registros leídos": est["sic_registros"],
                "En el catálogo como POI propio": int(poi["poi_id"].str.startswith("sic-").sum()),
                "Enlazados a otro POI": est["enlaces_sic"],
            },
            {
                "Fuente": "DENUE (INEGI), zonas de consulta",
                "Registros leídos": est["denue_en_zonas"],
                "En el catálogo como POI propio": int(poi["poi_id"].str.startswith("denue-").sum()),
                "Enlazados a otro POI": est["enlaces_denue"],
            },
        ]
    )
    sin_cat = est["osm_sin_categoria_o_nombre"]
    lineas += [
        _tabla(fuentes),
        "",
        f"- Elementos de OSM sin categoría del contrato o sin nombre: {sin_cat:,} "
        f"(incluye {est['bancas_osm']:,} bancas, que no entran como POI).",
        f"- Elementos de OSM fuera de las zonas o de los municipios del corredor: "
        f"{est['fuera_de_zona']:,}.",
        f"- Descartados por coordenadas ausentes o fuera del estado: "
        f"{est['descartados_coordenadas']:,} "
        f"(SIC sin coordenadas válidas: {est['sic_sin_coordenadas_validas']:,}).",
        f"- Oferta DENUE estatal (SCIAN 7211, 7225, 7121, 5615): "
        f"{int(r.oferta['establecimientos'].sum()):,} establecimientos en "
        f"{r.oferta['municipio_cvegeo'].nunique():,} municipios.",
        "",
        "## POI por categoría y zona",
        "",
    ]
    zona = poi["corredor_id"].where(poi["corredor_id"] != "", poi["destino_id"])
    zona = zona.map(lambda z: "corredor" if z == zonas.CORREDOR_ID else nombres.get(z, z))
    cruce = pd.crosstab(poi["categoria"], zona, margins=True, margins_name="Total")
    cruce = cruce.reset_index().rename(columns={"categoria": "Categoría"})
    lineas += [_tabla(cruce), "", "## Nulos en `poi.csv`", ""]
    nulos = pd.DataFrame(
        [
            {
                "Columna": c,
                "Vacíos": int((poi[c].isna() | (poi[c].astype(str) == "")).sum()),
                "%": _pct((poi[c].isna() | (poi[c].astype(str) == "")).sum(), len(poi)),
            }
            for c in integrar.COLUMNAS_POI
        ]
    )
    lineas += [_tabla(nulos), "", "## Duplicados", ""]
    lineas += [
        f"- `poi_id` repetidos: {int(poi['poi_id'].duplicated().sum())}.",
        f"- Elementos de OSM fundidos (mismo nombre y categoría a menos de "
        f"{integrar.DISTANCIA_DUPLICADO_M:.0f} m): {est['duplicados_osm']:,}.",
        f"- Recintos del SIC repetidos entre tablas: {est['duplicados_sic']:,}.",
        f"- Filas de accesibilidad repetidas (`poi_id`, `atributo`): "
        f"{int(acc.duplicated(['poi_id', 'atributo']).sum())}.",
    ]
    posibles = integrar.posibles_duplicados(poi)
    lineas += [
        f"- Posibles duplicados entre fuentes por revisar (nombre con similitud ≥ "
        f"{integrar.UMBRAL_POSIBLE_DUPLICADO:.2f}, entre {integrar.DISTANCIA_ENLACE_M:.0f} y "
        f"{integrar.DISTANCIA_POSIBLE_DUPLICADO_M:.0f} m): {len(posibles):,}. No se funden "
        "en automático; la lista sale de `integrar.posibles_duplicados`.",
        "",
        "## Enlaces entre fuentes",
        "",
        f"Regla: nombre difuso con puntaje ≥ {integrar.UMBRAL_ENLACE:.2f} y distancia "
        f"< {integrar.DISTANCIA_ENLACE_M:.0f} m, entre categorías compatibles; cada POI recibe "
        "a lo más un registro de cada fuente.",
        "",
    ]
    enl = poi[poi["match_score"].notna()]
    lineas += [
        f"- POI con al menos un enlace: {len(enl):,} de {len(poi):,} ({_pct(len(enl), len(poi))}).",
        f"- SIC con OSM: {est['enlaces_sic']:,} de {est['sic_en_zonas']:,} recintos del SIC "
        "en las zonas.",
        f"- DENUE con POI: alojamiento {est['enlaces_denue_7211']:,}; "
        f"alimentos {est['enlaces_denue_7225']:,}; "
        f"museos y sitios históricos {est['enlaces_denue_7121']:,}.",
    ]
    if len(enl):
        lineas.append(
            f"- Puntaje de enlace: mínimo {enl['match_score'].min():.2f}, "
            f"mediana {enl['match_score'].median():.2f}."
        )
    lineas += [
        "",
        "## Cobertura de información de accesibilidad",
        "",
        "Proporción de POI con al menos un atributo de accesibilidad declarado en OSM. Mide cuánto "
        "se sabe, no qué tan accesibles son los lugares: un POI sin dato queda «sin verificar».",
        "",
        _tabla(cobertura(poi, acc)),
        "",
    ]
    if len(acc):
        valores = (
            acc[acc["atributo"] == "acceso_sin_escalones"]["valor"].value_counts().sort_index()
        )
        lineas.append(
            "- Valores de acceso sin escalones: "
            + ", ".join(f"{k}: {v}" for k, v in valores.items())
            + "."
        )
        atributos = acc["atributo"].value_counts().sort_index()
        lineas.append(
            "- Filas por atributo: " + ", ".join(f"{k}: {v}" for k, v in atributos.items()) + "."
        )
    banios = poi[poi["categoria"] == "banio"]
    con_dato = banios["poi_id"].isin(set(acc.loc[acc["atributo"] == "banio_accesible", "poi_id"]))
    lineas += [
        f"- Sanitarios públicos con dato de baño accesible: {int(con_dato.sum())} de {len(banios)} "
        f"({_pct(con_dato.sum(), len(banios))}).",
        "",
        "## Limitaciones",
        "",
        "- OSM depende de quién mapea: la ausencia de un lugar o de una etiqueta no prueba que no "
        "exista.",
        "- Las coordenadas del SIC y del DENUE pueden estar desplazadas; lo no enlazado entra como "
        "POI propio y puede duplicar un lugar de OSM con otro nombre.",
        "- Los límites municipales están simplificados al 4 %: un punto cerca de un límite puede "
        "quedar en el municipio vecino.",
        "- Las etiquetas de accesibilidad de OSM no están verificadas por el equipo "
        "(`estado=sin_verificar`, `confianza=0.6`).",
        "",
        "Datos © OpenStreetMap contributors (ODbL 1.0). Directorios del Sistema de Información "
        "Cultural/Secretaría de Cultura. DENUE, INEGI.",
        "",
    ]
    return "\n".join(lineas)


def cifras_corredor(r: integrar.Resultado) -> str:
    """Bloque de cifras para `docs/corredor_piloto.md`."""
    anual = pd.read_csv(config.ruta(config.CURADO, "indicadores_oficiales_anual.csv"))
    completos = anual[(anual["meses"] == 12) & (anual["nivel"] == "destino")]
    anio = int(completos["anio"].max())
    del_anio = completos[completos["anio"] == anio].copy()
    estado = anual[(anual["anio"] == anio) & (anual["nivel"] == "agregado")]
    total_afluencia = float(estado["afluencia_visitantes"].iloc[0]) if len(estado) else 0.0
    pm = {d.destino_id for d in catalogo.cargar() if d.pueblo_magico}
    filas = []
    poi = r.poi
    for fila in del_anio.sort_values("afluencia_visitantes", ascending=False).itertuples():
        if fila.destino_id not in pm and fila.destino_id != "puebla":
            continue
        n_poi = int((poi["destino_id"] == fila.destino_id).sum())
        filas.append(
            {
                "Destino": fila.centro_ot,
                "Pueblo Mágico": "sí" if fila.destino_id in pm else "no",
                f"Afluencia {anio}": f"{fila.afluencia_visitantes:,.0f}",
                "% del estado": _pct(fila.afluencia_visitantes, total_afluencia),
                "Ocupación %": f"{fila.ocupacion_pct:.1f}",
                "Estadía (días)": f"{fila.estadia_promedio_dias:.2f}",
                "POI en el catálogo": n_poi,
            }
        )
    tabla = pd.DataFrame(filas)
    cob = cobertura(r.poi, r.accesibilidad)
    corredor = cob[cob["Zona"].str.startswith("Corredor")].iloc[0]
    cuenta = r.poi[r.poi["corredor_id"] == zonas.CORREDOR_ID]["categoria"].value_counts()
    patrimonio = int(
        cuenta.reindex(
            ["museo", "sitio_historico", "templo", "zona_arqueologica", "centro_cultural"]
        )
        .fillna(0)
        .sum()
    )
    lineas = [
        INICIO,
        "",
        f"Serie hotelera del Observatorio Turístico, año completo más reciente ({anio}); "
        "catálogo de POI de la spec 012.",
        "",
        _tabla(tabla),
        "",
        f"- POI del corredor: {corredor['POI']:,}; de patrimonio y cultura (museos, sitios "
        f"históricos, templos, zonas arqueológicas y centros culturales): {patrimonio:,}.",
        f"- Cobertura de información de accesibilidad en el corredor: "
        f"{corredor['Cobertura de información']} de los POI tienen algún atributo; "
        f"{corredor['% acceso']} tienen dato de acceso sin escalones.",
        "",
        FIN,
    ]
    return "\n".join(lineas)


def _reemplazar_bloque(ruta: Path, bloque: str) -> None:
    texto = ruta.read_text(encoding="utf-8")
    if INICIO in texto and FIN in texto:
        antes = texto.split(INICIO)[0]
        despues = texto.split(FIN, 1)[1]
        texto = antes + bloque + despues
    else:
        texto = texto.rstrip() + "\n\n" + bloque + "\n"
    ruta.write_text(texto, encoding="utf-8", newline="\n")


def escribir(resultado: integrar.Resultado | None = None) -> list[Path]:
    r = resultado or integrar.construir()
    salida = config.ruta("reports", "calidad_datos.md")
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(reporte(r), encoding="utf-8", newline="\n")
    rutas = [salida]
    doc = config.ruta("docs", "corredor_piloto.md")
    if doc.exists():
        _reemplazar_bloque(doc, cifras_corredor(r))
        rutas.append(doc)
    return rutas
