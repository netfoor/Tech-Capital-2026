"""Etapa 2: ranking multiobjetivo.

La pertinencia es la similitud coseno TF-IDF entre los intereses (expandidos a
un vocabulario controlado) y el texto del lugar: nombre, categoría (peso
doble), subcategoría y descripción. Es determinista y no llama a servicios.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field

from .config import Config
from .elegibilidad import ATR_BANIO, ATR_PENDIENTE, ATR_SIN_ESCALONES, _numero
from .geo import minutos_caminando
from .horarios import parsear
from .tipos import POICandidato

# Vocabulario controlado: cada interés se expande a términos del catálogo.
VOCABULARIO_INTERESES: dict[str, tuple[str, ...]] = {
    "historia": (
        "historia",
        "historico",
        "museo",
        "colonial",
        "patrimonio",
        "virreinal",
        "revolucion",
        "fuerte",
        "batalla",
    ),
    "arqueologia": ("arqueologia", "zona_arqueologica", "piramide", "prehispanico", "ruinas"),
    "arte": ("arte", "galeria", "pintura", "escultura", "exposicion", "talavera", "museo"),
    "gastronomia": (
        "gastronomia",
        "comida",
        "restaurante",
        "cafe",
        "mercado",
        "mole",
        "dulces",
        "cocina",
        "antojitos",
    ),
    "naturaleza": ("naturaleza", "parque", "jardin", "cerro", "aire", "libre", "arboles"),
    "religion": ("templo", "iglesia", "capilla", "catedral", "convento", "santuario"),
    "arquitectura": ("arquitectura", "barroco", "fachada", "catedral", "convento", "edificio"),
    "compras": ("compras", "artesanias", "mercado", "tienda", "talavera", "artesano"),
    "miradores": ("mirador", "vista", "panoramica", "cerro"),
    "familia": ("parque", "plaza", "interactivo", "ninos", "familia"),
    "cultura": ("cultura", "museo", "teatro", "biblioteca", "galeria", "arte", "historia"),
    "barrios": ("barrio", "callejon", "tradicional", "vecinos", "plaza"),
}

_STOP = frozenset("de del la las el los y en con a al un una por para su sus o que se es".split())


def normalizar(texto: str) -> str:
    sin_acentos = unicodedata.normalize("NFKD", texto or "")
    sin_acentos = "".join(c for c in sin_acentos if not unicodedata.combining(c))
    return sin_acentos.lower()


def tokens(texto: str) -> list[str]:
    salida = []
    for t in re.split(r"[^a-z0-9_]+", normalizar(texto)):
        if len(t) < 3 or t in _STOP:
            continue
        if len(t) > 4 and t.endswith("es") and not t.endswith("ies"):
            t = t[:-2]
        elif len(t) > 4 and t.endswith("s"):
            t = t[:-1]
        salida.append(t)
    return salida


def documento(poi: POICandidato) -> list[str]:
    cat = poi.categoria or ""
    return (
        tokens(poi.nombre)
        + tokens(cat) * 2
        + [normalizar(cat)] * 2
        + tokens(poi.subcategoria or "")
        + tokens(poi.descripcion)
    )


def consulta(interes: str) -> list[str]:
    clave = normalizar(interes).strip()
    expansion = VOCABULARIO_INTERESES.get(clave, ())
    terminos = tokens(interes) + [t for e in expansion for t in (tokens(e) or [e])]
    return terminos


@dataclass
class IndiceTfidf:
    idf: dict[str, float]
    vectores: dict[str, dict[str, float]]

    @classmethod
    def construir(cls, pois: list[POICandidato]) -> IndiceTfidf:
        docs = {p.poi_id: Counter(documento(p)) for p in pois}
        n = max(len(docs), 1)
        df: Counter[str] = Counter()
        for c in docs.values():
            df.update(c.keys())
        idf = {t: math.log((1 + n) / (1 + f)) + 1.0 for t, f in df.items()}
        vectores = {pid: _normalizar_vec(c, idf) for pid, c in docs.items()}
        return cls(idf=idf, vectores=vectores)

    def similitud(self, terminos: list[str], poi_id: str) -> float:
        q = _normalizar_vec(Counter(terminos), self.idf)
        v = self.vectores.get(poi_id, {})
        return sum(peso * v.get(t, 0.0) for t, peso in q.items())


def _normalizar_vec(conteo: Counter[str], idf: dict[str, float]) -> dict[str, float]:
    vec = {t: (1 + math.log(f)) * idf.get(t, 0.0) for t, f in conteo.items() if idf.get(t)}
    norma = math.sqrt(sum(x * x for x in vec.values())) or 1.0
    return {t: x / norma for t, x in vec.items()}


@dataclass
class Puntaje:
    total: float
    pertinencia: float
    cercania: float
    diversidad: float
    calidad: float
    esfuerzo: float
    intereses_coincidentes: list[str] = field(default_factory=list)
    minutos_desde_origen: int | None = None


def calidad_informacion(poi: POICandidato) -> float:
    """0 a 1: confianza de atributos clave más horario interpretable."""
    valores = []
    for atr in (ATR_SIN_ESCALONES, ATR_BANIO, ATR_PENDIENTE):
        a = poi.accesibilidad.get(atr)
        if a is None:
            valores.append(0.0)
        elif a.estado == "verificado":
            valores.append(a.confianza)
        elif a.estado == "sin_verificar":
            valores.append(0.5 * a.confianza)
        else:  # reportado: dato reciente y útil
            valores.append(0.5 * a.confianza)
    horario_ok = 1.0 if parsear(poi.horario_osm) is not None else 0.0
    return 0.8 * (sum(valores) / len(valores)) + 0.2 * horario_ok


def esfuerzo(poi: POICandidato, minutos: int | None) -> float:
    a = poi.accesibilidad.get(ATR_PENDIENTE)
    pend = _numero(a.valor) if a else None
    comp_pend = 0.3 if pend is None else min(max(pend, 0.0) / 15.0, 1.0)
    comp_dist = 0.0 if minutos is None else min(minutos / 60.0, 1.0)
    return 0.5 * comp_pend + 0.5 * comp_dist


def origen_de_referencia(
    pois: list[POICandidato], intereses: list[str], indice: IndiceTfidf
) -> tuple[float, float] | None:
    """Sin punto de partida, el centroide de los 10 lugares más pertinentes."""
    if not pois:
        return None
    terminos = [t for i in intereses for t in consulta(i)]
    orden = sorted(
        pois,
        key=lambda p: (-(indice.similitud(terminos, p.poi_id) if terminos else 0.0), p.poi_id),
    )[:10]
    return (
        sum(p.lat for p in orden) / len(orden),
        sum(p.lon for p in orden) / len(orden),
    )


def puntuar(
    pois: list[POICandidato],
    intereses: list[str],
    origen: tuple[float, float] | None,
    limite_min: int,
    config: Config,
    indice: IndiceTfidf | None = None,
) -> dict[str, Puntaje]:
    indice = indice or IndiceTfidf.construir(pois)
    w = config.pesos
    por_interes = {i: consulta(i) for i in intereses}
    todos = [t for ts in por_interes.values() for t in ts]
    crudas = {p.poi_id: indice.similitud(todos, p.poi_id) if todos else 0.0 for p in pois}
    maximo = max(crudas.values(), default=0.0)
    salida: dict[str, Puntaje] = {}
    radio = max(limite_min / 2, 15)
    for p in pois:
        if todos:
            pert = crudas[p.poi_id] / maximo if maximo > 0 else 0.0
        else:
            pert = 0.5
        coinciden = [
            i for i, ts in por_interes.items() if ts and indice.similitud(ts, p.poi_id) > 0.05
        ]
        minutos = minutos_caminando(origen, (p.lat, p.lon), config) if origen else None
        cerc = 0.5 if minutos is None else max(0.0, 1 - minutos / radio)
        div = 0.5 * (1.0 if p.es_destino_alternativo else 0.0) + 0.5 * (
            1 - min(max(p.popularidad, 0.0), 1.0)
        )
        cal = calidad_informacion(p)
        esf = esfuerzo(p, minutos)
        total = (
            w.pertinencia * pert
            + w.cercania * cerc
            + w.diversidad * div
            + w.calidad * cal
            - w.esfuerzo * esf
        )
        salida[p.poi_id] = Puntaje(
            total=total,
            pertinencia=pert,
            cercania=cerc,
            diversidad=div,
            calidad=cal,
            esfuerzo=esf,
            intereses_coincidentes=coinciden,
            minutos_desde_origen=minutos,
        )
    return salida
