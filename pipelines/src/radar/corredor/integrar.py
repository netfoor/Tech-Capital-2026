"""Etapa sin red: integra OSM, SIC y DENUE en el catálogo de POI con su accesibilidad.

Lee solo los extractos versionados de `data/fuentes/corredor/` y escribe en `data/curado/`:
`poi.csv`, `poi_accesibilidad.csv`, `corredores.csv` y `oferta_denue_municipio.csv`.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz

from radar import catalogo, config, geo
from radar.corredor import denue, osm, sic, zonas
from radar.texto import normalizar

COLUMNAS_POI = [
    "poi_id",
    "nombre",
    "categoria",
    "subcategoria",
    "destino_id",
    "corredor_id",
    "municipio_cvegeo",
    "lat",
    "lon",
    "direccion",
    "horario_osm",
    "costo_rango",
    "descripcion",
    "fuentes",
    "osm_id",
    "denue_id",
    "sic_id",
    "match_score",
    "is_synthetic",
]
COLUMNAS_ACCESIBILIDAD = [
    "poi_id",
    "atributo",
    "valor",
    "origen",
    "fecha",
    "confianza",
    "estado",
    "evidencia",
]
COLUMNAS_CORREDORES = [
    "corredor_id",
    "nombre",
    "descripcion",
    "lat_min",
    "lon_min",
    "lat_max",
    "lon_max",
]
CATEGORIAS = {
    "museo",
    "sitio_historico",
    "templo",
    "zona_arqueologica",
    "mercado",
    "artesanias",
    "parque",
    "mirador",
    "restaurante",
    "cafe",
    "alojamiento",
    "banio",
    "centro_cultural",
    "otro",
}
ATRIBUTOS = {
    "acceso_sin_escalones",
    "rampa",
    "banio_accesible",
    "elevador",
    "superficie",
    "asientos",
    "estacionamiento_reservado",
    "pendiente_pct",
    "numero_escalones",
}

DISTANCIA_ENLACE_M = 75.0
UMBRAL_ENLACE = 0.80
DISTANCIA_DUPLICADO_M = 30.0
ORDEN_FUENTES = (osm.FUENTE_ID, sic.FUENTE_ID, denue.FUENTE_ID)

# Palabras genéricas que no distinguen un lugar de otro al comparar nombres.
GENERICAS = {
    "museo",
    "templo",
    "parroquia",
    "iglesia",
    "capilla",
    "santuario",
    "hotel",
    "hostal",
    "posada",
    "restaurante",
    "restaurant",
    "cafe",
    "cafeteria",
    "casa",
    "centro",
    "cultural",
    "de",
    "del",
    "la",
    "el",
    "los",
    "las",
    "y",
    "a",
    "c",
    "s",
    "sa",
    "cv",
}

# Categorías compatibles para enlazar un registro de DENUE (prefijo SCIAN) con un POI.
COMPATIBLES_DENUE = {
    "7211": {"alojamiento"},
    "7225": {"restaurante", "cafe"},
    "7121": {"museo", "sitio_historico", "zona_arqueologica", "centro_cultural", "parque", "otro"},
}
COMPATIBLES_SIC = {
    "museo": {"museo", "centro_cultural", "sitio_historico", "otro"},
    "zona_arqueologica": {"zona_arqueologica", "sitio_historico", "museo", "otro"},
    "centro_cultural": {"centro_cultural", "museo", "sitio_historico", "otro"},
    "artesanias": {"artesanias", "mercado", "centro_cultural", "otro"},
}
MUNICIPIO_A_DESTINO_CORREDOR = {"21114": "puebla", "21119": "cholula", "21140": "cholula"}


def base_nombre(nombre: str) -> str:
    completo = normalizar(nombre)
    base = " ".join(p for p in completo.split() if p not in GENERICAS)
    return base or completo


def similitud(a: str, b: str) -> float:
    """0–1. `token_set_ratio` premia que un nombre contenga al otro; se castiga: poco si el
    nombre contenido tiene dos palabras o más, mucho si es una sola («Catedral» dentro de
    «Hotel Catedral»)."""
    x, y = base_nombre(a), base_nombre(b)
    if not x or not y:
        return 0.0
    peso = 0.9 if min(len(x.split()), len(y.split())) >= 2 else 0.75
    return max(fuzz.token_sort_ratio(x, y), peso * fuzz.token_set_ratio(x, y)) / 100


_MINUSCULAS = {"de", "del", "la", "el", "los", "las", "y", "en", "a", "con"}


def titulo(texto: str) -> str:
    """Nombres de DENUE (en mayúsculas) a tipo título, con artículos en minúscula."""
    palabras = texto.strip().lower().split()
    return " ".join(
        p if (i and p in _MINUSCULAS) else p[:1].upper() + p[1:] for i, p in enumerate(palabras)
    )


@dataclass
class Poi:
    poi_id: str
    nombre: str
    categoria: str
    subcategoria: str
    lat: float
    lon: float
    municipio_cvegeo: str
    destino_id: str
    corredor_id: str
    direccion: str = ""
    horario_osm: str = ""
    costo_rango: str = "desconocido"
    descripcion: str = ""
    osm_id: str = ""
    denue_id: str = ""
    sic_id: str = ""
    puntajes: list[float] = field(default_factory=list)
    elemento: osm.Elemento | None = None

    def fuentes(self) -> str:
        presentes = {
            osm.FUENTE_ID: bool(self.osm_id),
            sic.FUENTE_ID: bool(self.sic_id),
            denue.FUENTE_ID: bool(self.denue_id),
        }
        return "|".join(f for f in ORDEN_FUENTES if presentes[f])

    def fila(self) -> dict[str, object]:
        return {
            "poi_id": self.poi_id,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "subcategoria": self.subcategoria,
            "destino_id": self.destino_id,
            "corredor_id": self.corredor_id,
            "municipio_cvegeo": self.municipio_cvegeo,
            "lat": f"{self.lat:.6f}",
            "lon": f"{self.lon:.6f}",
            "direccion": self.direccion,
            "horario_osm": self.horario_osm,
            "costo_rango": self.costo_rango,
            "descripcion": self.descripcion,
            "fuentes": self.fuentes(),
            "osm_id": self.osm_id,
            "denue_id": self.denue_id,
            "sic_id": self.sic_id,
            "match_score": round(max(self.puntajes), 4) if self.puntajes else None,
            "is_synthetic": "false",
        }


@dataclass
class Resultado:
    poi: pd.DataFrame
    accesibilidad: pd.DataFrame
    corredores: pd.DataFrame
    oferta: pd.DataFrame
    estadisticas: Counter = field(default_factory=Counter)

    def resumen(self) -> list[str]:
        e = self.estadisticas
        return [
            f"POI: {len(self.poi):,} ({e['poi_corredor']:,} en el corredor)",
            f"Filas de accesibilidad: {len(self.accesibilidad):,}",
            f"Enlaces SIC con OSM: {e['enlaces_sic']:,}; DENUE con POI: {e['enlaces_denue']:,}",
            f"Descartados fuera de Puebla o sin coordenadas: {e['descartados_coordenadas']:,}",
            f"Duplicados fusionados: {e['duplicados_osm'] + e['duplicados_sic']:,}",
        ]


def _ubicar(lat: float, lon: float) -> tuple[str, str, str] | None:
    """(municipio, destino_id, corredor_id) o None si el punto queda fuera de las zonas."""
    corredor_id, destino_pm = zonas.zona_de(lat, lon)
    if not corredor_id and not destino_pm:
        return None
    municipio = geo.municipio_de(lat, lon)
    if corredor_id:
        destino = MUNICIPIO_A_DESTINO_CORREDOR.get(municipio)
        if destino is None:
            return None
        return municipio, destino, corredor_id
    return municipio, destino_pm, ""


def _carpeta(fuente: str, raiz: Path | None) -> Path:
    return (raiz or config.ruta(config.FUENTES, "corredor")) / fuente


def _leer_osm(raiz: Path | None) -> list[osm.Elemento]:
    vistos: dict[str, osm.Elemento] = {}
    for archivo in sorted(_carpeta("osm", raiz).glob("*.json")):
        for e in osm.leer(json.loads(archivo.read_text(encoding="utf-8"))):
            vistos.setdefault(e.osm_id, e)
    orden = {"node": 0, "way": 1, "relation": 2}
    return sorted(vistos.values(), key=lambda e: (orden.get(e.tipo, 3), e.id))


def _fundir(base: osm.Elemento, otro: osm.Elemento) -> osm.Elemento:
    etiquetas = {**otro.etiquetas, **base.etiquetas}
    return osm.Elemento(base.tipo, base.id, base.lat, base.lon, etiquetas, base.fecha)


def _pois_osm(elementos: list[osm.Elemento], est: Counter) -> list[Poi]:
    pois: list[Poi] = []
    por_nombre: dict[tuple[str, str], list[Poi]] = {}
    for e in elementos:
        cat = osm.es_poi(e)
        if e.etiquetas.get("amenity") == "bench":
            est["bancas_osm"] += 1
        if cat is None:
            est["osm_sin_categoria_o_nombre"] += 1
            continue
        if not geo.en_puebla(e.lat, e.lon):
            est["descartados_coordenadas"] += 1
            continue
        ubicacion = _ubicar(e.lat, e.lon)
        if ubicacion is None:
            est["fuera_de_zona"] += 1
            continue
        nombre = osm.nombre(e.etiquetas, cat[0])
        llave = (cat[0], normalizar(nombre))
        duplicado = next(
            (
                p
                for p in por_nombre.get(llave, [])
                if geo.distancia_m(p.lat, p.lon, e.lat, e.lon) < DISTANCIA_DUPLICADO_M
            ),
            None,
        )
        if duplicado is not None and duplicado.elemento is not None:
            duplicado.elemento = _fundir(duplicado.elemento, e)
            est["duplicados_osm"] += 1
            continue
        municipio, destino, corredor_id = ubicacion
        t = e.etiquetas
        pois.append(
            Poi(
                poi_id=e.poi_id,
                nombre=nombre,
                categoria=cat[0],
                subcategoria=cat[1],
                lat=e.lat,
                lon=e.lon,
                municipio_cvegeo=municipio,
                destino_id=destino,
                corredor_id=corredor_id,
                direccion=osm.direccion(t),
                horario_osm=t.get("opening_hours", "").strip(),
                costo_rango=osm.costo(t),
                descripcion=t.get("description", "").strip(),
                osm_id=e.osm_id,
                elemento=e,
            )
        )
        por_nombre.setdefault(llave, []).append(pois[-1])
    for p in pois:  # el horario y el costo pueden venir de un duplicado fundido
        if p.elemento is not None:
            p.horario_osm = p.horario_osm or p.elemento.etiquetas.get("opening_hours", "").strip()
            if p.costo_rango == "desconocido":
                p.costo_rango = osm.costo(p.elemento.etiquetas)
    return pois


@dataclass(frozen=True)
class Registro:
    """Un registro de SIC o DENUE por enlazar."""

    clave: str
    nombre: str
    lat: float
    lon: float
    compatibles: frozenset[str]


CELDA = 0.001  # grados (≈ 110 m): mayor que la distancia de enlace


def _celda(lat: float, lon: float) -> tuple[int, int]:
    return int(lat // CELDA), int(lon // CELDA)


def _indice(pois: list[Poi]) -> dict[tuple[int, int], list[Poi]]:
    indice: dict[tuple[int, int], list[Poi]] = {}
    for p in pois:
        indice.setdefault(_celda(p.lat, p.lon), []).append(p)
    return indice


def _vecinos(indice: dict[tuple[int, int], list[Poi]], lat: float, lon: float) -> list[Poi]:
    i, j = _celda(lat, lon)
    return [p for di in (-1, 0, 1) for dj in (-1, 0, 1) for p in indice.get((i + di, j + dj), [])]


def _enlazar(registros: list[Registro], pois: list[Poi]) -> dict[str, tuple[Poi, float]]:
    """Asignación voraz por mejor puntaje: un POI recibe a lo más un registro de la fuente."""
    indice = _indice(pois)
    candidatos: list[tuple[float, float, str, str, Poi]] = []
    for r in registros:
        for p in _vecinos(indice, r.lat, r.lon):
            if p.categoria not in r.compatibles:
                continue
            d = geo.distancia_m(p.lat, p.lon, r.lat, r.lon)
            if d >= DISTANCIA_ENLACE_M:
                continue
            s = similitud(r.nombre, p.nombre)
            if s >= UMBRAL_ENLACE:
                candidatos.append((-s, d, r.clave, p.poi_id, p))
    candidatos.sort(key=lambda c: (c[0], c[1], c[2], c[3]))
    asignados: dict[str, tuple[Poi, float]] = {}
    usados: set[str] = set()
    for menos_s, _, clave, poi_id, p in candidatos:
        if clave in asignados or poi_id in usados:
            continue
        asignados[clave] = (p, round(-menos_s, 4))
        usados.add(poi_id)
    return asignados


def _integrar_sic(pois: list[Poi], raiz: Path | None, est: Counter) -> list[Poi]:
    recintos: list[sic.Recinto] = []
    for tabla in sic.TABLAS:
        archivo = _carpeta("sic", raiz) / f"{tabla}_puebla.csv"
        if archivo.exists():
            recintos += sic.leer(tabla, archivo.read_text(encoding="utf-8"))
    est["sic_registros"] = len(recintos)
    validos = []
    for r in recintos:
        if r.lat is None or r.lon is None or not geo.en_puebla(r.lat, r.lon):
            est["descartados_coordenadas"] += 1
            est["sic_sin_coordenadas_validas"] += 1
            continue
        if _ubicar(r.lat, r.lon) is None:
            continue
        validos.append(r)
    est["sic_en_zonas"] = len(validos)
    registros = [
        Registro(
            r.sic_id, r.nombre, r.lat, r.lon, frozenset(COMPATIBLES_SIC[sic.TABLAS[r.tabla][0]])
        )
        for r in validos
    ]
    enlaces = _enlazar(registros, [p for p in pois if p.osm_id])
    nuevos: list[Poi] = []
    for r in sorted(validos, key=lambda r: r.sic_id):
        if r.sic_id in enlaces:
            p, s = enlaces[r.sic_id]
            p.sic_id, p.puntajes = r.sic_id, [*p.puntajes, s]
            p.direccion = p.direccion or r.direccion
            p.descripcion = p.descripcion or r.descripcion
            est["enlaces_sic"] += 1
            continue
        cat, sub = sic.TABLAS[r.tabla]
        duplicado = next(
            (
                p
                for p in nuevos
                if normalizar(p.nombre) == normalizar(r.nombre)
                and geo.distancia_m(p.lat, p.lon, r.lat, r.lon) < DISTANCIA_DUPLICADO_M
            ),
            None,
        )
        if duplicado is not None:
            est["duplicados_sic"] += 1
            continue
        municipio, destino, corredor_id = _ubicar(r.lat, r.lon)  # type: ignore[misc]
        nuevos.append(
            Poi(
                poi_id=r.poi_id,
                nombre=r.nombre,
                categoria=cat,
                subcategoria=sub,
                lat=r.lat,
                lon=r.lon,
                municipio_cvegeo=municipio,
                destino_id=destino,
                corredor_id=corredor_id,
                direccion=r.direccion,
                descripcion=r.descripcion,
                sic_id=r.sic_id,
            )
        )
    return pois + nuevos


def _categoria_denue(codigo: str) -> tuple[str, str] | None:
    if codigo.startswith("7211"):
        return "alojamiento", f"scian={codigo}"
    if codigo.startswith("71211"):
        return "museo", f"scian={codigo}"
    if codigo.startswith("71212"):
        return "sitio_historico", f"scian={codigo}"
    if codigo.startswith("71213"):
        return "parque", f"scian={codigo}"
    if codigo.startswith("7121"):
        return "otro", f"scian={codigo}"
    return None  # 7225 y 5615 solo se enlazan o se cuentan


def _integrar_denue(pois: list[Poi], tabla: pd.DataFrame, est: Counter) -> list[Poi]:
    est["denue_en_zonas"] = len(tabla)
    validos = []
    for fila in tabla.itertuples(index=False):
        if pd.isna(fila.lat) or pd.isna(fila.lon) or not geo.en_puebla(fila.lat, fila.lon):
            est["descartados_coordenadas"] += 1
            continue
        if fila.scian_prefijo not in COMPATIBLES_DENUE:
            continue
        if _ubicar(fila.lat, fila.lon) is None:
            continue
        validos.append(fila)
    registros = [
        Registro(
            f.id,
            f.nom_estab,
            float(f.lat),
            float(f.lon),
            frozenset(COMPATIBLES_DENUE[f.scian_prefijo]),
        )
        for f in validos
    ]
    enlaces = _enlazar(registros, pois)
    nuevos: list[Poi] = []
    for f in sorted(validos, key=lambda f: int(f.id)):
        if f.id in enlaces:
            p, s = enlaces[f.id]
            p.denue_id, p.puntajes = f.id, [*p.puntajes, s]
            p.direccion = p.direccion or denue.direccion(pd.Series(f._asdict()))
            est["enlaces_denue"] += 1
            est[f"enlaces_denue_{f.scian_prefijo}"] += 1
            continue
        cat = _categoria_denue(f.codigo_act)
        if cat is None or not f.nom_estab.strip():
            continue
        municipio, destino, corredor_id = _ubicar(float(f.lat), float(f.lon))  # type: ignore[misc]
        nuevos.append(
            Poi(
                poi_id=f"denue-{f.id}",
                nombre=titulo(f.nom_estab),
                categoria=cat[0],
                subcategoria=cat[1],
                lat=float(f.lat),
                lon=float(f.lon),
                municipio_cvegeo=municipio,
                destino_id=destino,
                corredor_id=corredor_id,
                direccion=denue.direccion(pd.Series(f._asdict())),
                denue_id=f.id,
            )
        )
    return pois + nuevos


def _accesibilidad(pois: list[Poi]) -> pd.DataFrame:
    filas = []
    for p in pois:
        if p.elemento is None:
            continue
        for f in osm.accesibilidad(p.elemento, p.categoria):
            filas.append({**f, "poi_id": p.poi_id})
    tabla = pd.DataFrame(filas, columns=COLUMNAS_ACCESIBILIDAD)
    tabla = tabla.drop_duplicates(["poi_id", "atributo"], keep="first")
    return tabla.sort_values(["poi_id", "atributo"]).reset_index(drop=True)


UMBRAL_POSIBLE_DUPLICADO = 0.90
DISTANCIA_POSIBLE_DUPLICADO_M = 300.0
_GRUPOS = {
    "museo": "cultura",
    "centro_cultural": "cultura",
    "sitio_historico": "cultura",
    "zona_arqueologica": "cultura",
    "restaurante": "alimentos",
    "cafe": "alimentos",
}


def _grupo(categoria: str) -> str:
    return _GRUPOS.get(categoria, categoria)


def posibles_duplicados(poi: pd.DataFrame) -> pd.DataFrame:
    """POI de SIC o DENUE sin par en OSM con un POI de OSM de nombre muy parecido y cercano.

    Sirve para revisar a mano: no se funden en automático porque la distancia supera la
    regla de enlace.
    """
    propios = poi[~poi["poi_id"].str.startswith("osm-")]
    de_osm = poi[poi["poi_id"].str.startswith("osm-")]
    celdas: dict[tuple[int, int], list[tuple[str, str, str, float, float]]] = {}
    paso = 0.003
    for f in de_osm.itertuples(index=False):
        lat, lon = float(f.lat), float(f.lon)
        celdas.setdefault((int(lat // paso), int(lon // paso)), []).append(
            (f.poi_id, f.nombre, f.categoria, lat, lon)
        )
    filas = []
    for f in propios.itertuples(index=False):
        lat, lon = float(f.lat), float(f.lon)
        i, j = int(lat // paso), int(lon // paso)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for poi_id, nombre, cat, a, o in celdas.get((i + di, j + dj), []):
                    if _grupo(cat) != _grupo(f.categoria):
                        continue
                    d = geo.distancia_m(lat, lon, a, o)
                    if not (DISTANCIA_ENLACE_M <= d < DISTANCIA_POSIBLE_DUPLICADO_M):
                        continue
                    s = similitud(f.nombre, nombre)
                    if s >= UMBRAL_POSIBLE_DUPLICADO:
                        filas.append(
                            {
                                "poi_id": f.poi_id,
                                "nombre": f.nombre,
                                "poi_id_osm": poi_id,
                                "nombre_osm": nombre,
                                "distancia_m": round(d, 1),
                                "similitud": round(s, 4),
                            }
                        )
    columnas = ["poi_id", "nombre", "poi_id_osm", "nombre_osm", "distancia_m", "similitud"]
    tabla = pd.DataFrame(filas, columns=columnas)
    return tabla.sort_values(["poi_id", "poi_id_osm"]).reset_index(drop=True)


def corredores() -> pd.DataFrame:
    c = zonas.CORREDOR
    return pd.DataFrame(
        [
            {
                "corredor_id": c.corredor_id,
                "nombre": c.nombre,
                "descripcion": c.descripcion,
                "lat_min": c.lat_min,
                "lon_min": c.lon_min,
                "lat_max": c.lat_max,
                "lon_max": c.lon_max,
            }
        ],
        columns=COLUMNAS_CORREDORES,
    )


def construir(raiz: Path | None = None) -> Resultado:
    """Integra sin escribir. `raiz` apunta a otra carpeta de extractos (pruebas)."""
    est: Counter = Counter()
    elementos = _leer_osm(raiz)
    est["osm_elementos"] = len(elementos)
    pois = _pois_osm(elementos, est)
    est["poi_osm"] = len(pois)
    pois = _integrar_sic(pois, raiz, est)

    zonas_csv = _carpeta("denue", raiz) / "denue_21_turismo_zonas.csv"
    estatal_csv = _carpeta("denue", raiz) / "denue_21_turismo_estatal.csv"
    if zonas_csv.exists():
        pois = _integrar_denue(pois, denue.leer(zonas_csv), est)
    oferta = (
        denue.oferta_por_municipio(denue.leer(estatal_csv))
        if estatal_csv.exists()
        else pd.DataFrame(
            columns=["municipio_cvegeo", "scian_prefijo", "rama", "establecimientos", "fuente_id"]
        )
    )

    destinos = {d.destino_id for d in catalogo.cargar()}
    for p in pois:
        assert p.categoria in CATEGORIAS, p
        assert p.destino_id in destinos, p
    tabla = pd.DataFrame([p.fila() for p in pois], columns=COLUMNAS_POI)
    tabla = tabla.sort_values("poi_id").reset_index(drop=True)
    est["poi_corredor"] = int((tabla["corredor_id"] == zonas.CORREDOR_ID).sum())
    return Resultado(tabla, _accesibilidad(pois), corredores(), oferta, est)


def escribir(resultado: Resultado, carpeta: Path | None = None) -> list[Path]:
    carpeta = carpeta or config.ruta(config.CURADO)
    carpeta.mkdir(parents=True, exist_ok=True)
    salidas = {
        "poi.csv": resultado.poi,
        "poi_accesibilidad.csv": resultado.accesibilidad,
        "corredores.csv": resultado.corredores,
        "oferta_denue_municipio.csv": resultado.oferta,
    }
    rutas = []
    for nombre, tabla in salidas.items():
        ruta = carpeta / nombre
        tabla.to_csv(ruta, index=False, float_format="%.4f", lineterminator="\n")
        rutas.append(ruta)
    return rutas


def ejecutar(raiz: Path | None = None, carpeta: Path | None = None) -> Resultado:
    resultado = construir(raiz)
    escribir(resultado, carpeta)
    return resultado
