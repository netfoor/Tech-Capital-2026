"""DENUE de INEGI: descarga masiva por entidad (sin token) y filtro de ramas turísticas.

Del extracto se excluyen teléfono, correo, sitio web y razón social: no hacen falta para el
catálogo y en unidades de personas físicas pueden ser datos personales.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd

FUENTE_ID = "inegi-denue"
URL = "https://www.inegi.org.mx/contenidos/masiva/denue/denue_21_csv.zip"

# Prefijo SCIAN → rama (§02.3 B).
RAMAS = {
    "7211": "alojamiento",
    "7225": "alimentos_y_bebidas",
    "7121": "museos_y_sitios_historicos",
    "5615": "agencias_de_viajes",
}
COLUMNAS = [
    "id",
    "nom_estab",
    "codigo_act",
    "nombre_act",
    "per_ocu",
    "tipo_vial",
    "nom_vial",
    "numero_ext",
    "nomb_asent",
    "cod_postal",
    "cve_ent",
    "cve_mun",
    "municipio",
    "cve_loc",
    "localidad",
    "latitud",
    "longitud",
    "fecha_alta",
]


def filtrar_zip(ruta_zip: Path) -> pd.DataFrame:
    """Filas de las ramas turísticas, con las columnas del extracto y orden estable."""
    with zipfile.ZipFile(ruta_zip) as z:
        nombre = next(
            n for n in z.namelist() if n.startswith("conjunto_de_datos/") and n.endswith(".csv")
        )
        with z.open(nombre) as f:
            texto = io.TextIOWrapper(f, encoding="latin-1", newline="")
            partes = []
            for bloque in pd.read_csv(
                texto, dtype=str, usecols=COLUMNAS, chunksize=200_000, keep_default_na=False
            ):
                prefijo = bloque["codigo_act"].str[:4]
                partes.append(bloque[prefijo.isin(RAMAS)])
    tabla = pd.concat(partes, ignore_index=True)[COLUMNAS]
    for c in COLUMNAS:
        tabla[c] = tabla[c].str.strip()
    return tabla.sort_values("id", key=lambda s: s.astype(int)).reset_index(drop=True)


COLUMNAS_ESTATAL = ["id", "codigo_act", "per_ocu", "cve_ent", "cve_mun", "latitud", "longitud"]


def partir(tabla: pd.DataFrame, en_zona) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Extracto estatal compacto (para conteos) y extracto completo de las zonas (para POI)."""
    lat = pd.to_numeric(tabla["latitud"], errors="coerce")
    lon = pd.to_numeric(tabla["longitud"], errors="coerce")
    dentro = [
        bool(en_zona(a, o)) if pd.notna(a) and pd.notna(o) else False
        for a, o in zip(lat, lon, strict=True)
    ]
    return tabla[COLUMNAS_ESTATAL].copy(), tabla[dentro].reset_index(drop=True)


def leer(ruta: Path) -> pd.DataFrame:
    tabla = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    tabla["lat"] = pd.to_numeric(tabla["latitud"], errors="coerce")
    tabla["lon"] = pd.to_numeric(tabla["longitud"], errors="coerce")
    tabla["scian_prefijo"] = tabla["codigo_act"].str[:4]
    tabla["municipio_cvegeo"] = tabla["cve_ent"] + tabla["cve_mun"].str.zfill(3)
    return tabla


def direccion(fila: pd.Series) -> str:
    calle = " ".join(
        p for p in (fila.get("tipo_vial", ""), fila.get("nom_vial", "")) if p and p != "NINGUNO"
    )
    numero = fila.get("numero_ext", "")
    partes = [" ".join(p for p in (calle.title(), numero) if p and p != "0")]
    if fila.get("nomb_asent"):
        partes.append(str(fila["nomb_asent"]).title())
    return ", ".join(p for p in partes if p)


def oferta_por_municipio(tabla: pd.DataFrame) -> pd.DataFrame:
    """Establecimientos por municipio y rama (insumo de la spec 013)."""
    conteo = (
        tabla.groupby(["municipio_cvegeo", "scian_prefijo"]).size().rename("establecimientos")
    ).reset_index()
    conteo["rama"] = conteo["scian_prefijo"].map(RAMAS)
    conteo["fuente_id"] = FUENTE_ID
    conteo = conteo[["municipio_cvegeo", "scian_prefijo", "rama", "establecimientos", "fuente_id"]]
    return conteo.sort_values(["municipio_cvegeo", "scian_prefijo"]).reset_index(drop=True)
