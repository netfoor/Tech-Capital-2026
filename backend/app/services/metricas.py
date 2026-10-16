"""Indicadores del tablero institucional (spec 019).

Cuatro módulos (§09): Oferta–demanda (serie oficial), Inclusión (catálogo y moderación),
Panorama y Experiencia (agregados de personas, con supresión k). Reglas comunes:

- Ninguna salida trae coordenadas, identificadores de persona ni texto libre de la persona.
- Cada grupo se calcula con filas de un solo tipo (`is_synthetic`) y lo dice (constitución XII).
- Un grupo con menos de k personas distintas sale suprimido y sin valor (constitución XI).
"""

import calendar
import csv
import io
import math
import random
import statistics
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import ajustes
from app.models import (
    AggregateMetric,
    CommunityReport,
    ConfirmedVisit,
    DataLineage,
    DataSource,
    Destination,
    MetricDefinition,
    ModerationCase,
    POIAccessibilityAttribute,
    PointOfInterest,
    Review,
    ReviewDimension,
    TripSession,
    VisitCandidate,
)
from app.models.core import ATRIBUTOS_ACCESIBILIDAD
from app.models.private import DIMENSIONES
from app.services import definiciones

SEMILLA_BOOTSTRAP = 2026
REMUESTREOS = 1000
NIVEL_DESTINO = "destino"
CENTRO_ESTADO = "Estado"
INDICADORES_OFERTA = (
    "cuartos_disponibles",
    "cuartos_ocupados",
    "llegadas_turistas",
    "turistas_noche",
    "afluencia_visitantes",
)
FUENTE_OFICIAL = "sectur-ot-2026-06"


def k_minimo() -> int:
    return ajustes().k_minimo


def ahora_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def redondear(valor: float | None, decimales: int = 4) -> float | None:
    return None if valor is None else round(valor, decimales)


# ---------------------------------------------------------------------------
# Estadística


def hhi(valores: Iterable[float]) -> float | None:
    """Herfindahl-Hirschman en escala 0–10 000: Σ (100 · sᵢ)²."""
    valores = [v for v in valores if v and v > 0]
    total = sum(valores)
    if total <= 0:
        return None
    return sum((100 * v / total) ** 2 for v in valores)


def wilson(exitos: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """Intervalo de Wilson del 95 % para una proporción."""
    if n <= 0:
        return None
    p = exitos / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    margen = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centro - margen), min(1.0, centro + margen)


def bootstrap_media(
    valores: Sequence[float], remuestreos: int = REMUESTREOS, semilla: int = SEMILLA_BOOTSTRAP
) -> tuple[float, float] | None:
    """Intervalo bootstrap percentil del 95 % de la media, determinista."""
    if not valores:
        return None
    generador = random.Random(semilla)
    n = len(valores)
    medias = sorted(sum(generador.choices(valores, k=n)) / n for _ in range(remuestreos))
    return medias[int(0.025 * remuestreos)], medias[int(0.975 * remuestreos) - 1]


def cuantiles(valores: Sequence[float]) -> tuple[float, float, float] | None:
    if not valores:
        return None
    if len(valores) == 1:
        return valores[0], valores[0], valores[0]
    q1, q2, q3 = statistics.quantiles(valores, n=4, method="inclusive")
    return q1, q2, q3


def suprimir(
    grupos: list[dict], k: int, campos: Sequence[str], clave_n: str = "personas"
) -> list[dict]:
    """Marca `suprimido` y vacía `campos` en los grupos con menos de k personas.

    Supresión complementaria (§14): si en la partición queda un único grupo suprimido y hay
    otros, se suprime también el siguiente más pequeño, para que no se deduzca por diferencia.
    """
    for g in grupos:
        g["suprimido"] = g[clave_n] < k
    suprimidos = [g for g in grupos if g["suprimido"]]
    if len(suprimidos) == 1:
        visibles = sorted((g for g in grupos if not g["suprimido"]), key=lambda g: g[clave_n])
        if visibles:
            visibles[0]["suprimido"] = True
            visibles[0]["supresion_complementaria"] = True
    for g in grupos:
        g.setdefault("supresion_complementaria", False)
        if g["suprimido"]:
            for campo in campos:
                g[campo] = None
            # El conteo exacto de personas también delata: solo se dice que no llega a k.
            g[clave_n] = None
    return grupos


# ---------------------------------------------------------------------------
# Fuentes y metadatos


def fuente(s: Session, fuente_id: str) -> dict | None:
    f = s.get(DataSource, fuente_id)
    if f is None:
        return None
    return {
        "fuente_id": f.fuente_id,
        "nombre": f.nombre,
        "institucion": f.institucion,
        "url": f.url,
        "fecha_consulta": f.fecha_consulta.isoformat() if f.fecha_consulta else None,
        "sha256": f.sha256,
    }


def ficha_resumen(metric_id: str) -> dict:
    """Lo que el tablero muestra junto a cada gráfico."""
    f = definiciones.fichas().get(metric_id, {})
    return {
        "metric_id": metric_id,
        "nombre": f.get("nombre", metric_id),
        "pregunta": f.get("pregunta"),
        "formula": f.get("formula"),
        "unidad": f.get("unidad"),
        "denominador": f.get("denominador"),
        "fuentes": f.get("fuentes", []),
        "limitaciones": f.get("limitaciones"),
        "procedencia": f.get("procedencia"),
        "version": f.get("version"),
        "k_minimo": f.get("k_minimo"),
        "decision_potencial": f.get("decision_potencial"),
    }


# ---------------------------------------------------------------------------
# Oferta–demanda


@dataclass(frozen=True)
class FilaOficial:
    centro_ot: str
    destino_id: str | None
    nivel: str
    periodo: str
    indicador: str
    valor: float | None


def dias_del_periodo(periodo: str) -> int:
    anio, mes = (int(p) for p in periodo.split("-"))
    return calendar.monthrange(anio, mes)[1]


def _suma(datos: dict, periodos: Iterable[str], indicador: str) -> tuple[float, int]:
    total, meses = 0.0, 0
    for p in periodos:
        v = datos.get(p, {}).get(indicador)
        if v is not None:
            total += v
            meses += 1
    return total, meses


def _hoteleros(datos: dict, periodos: Sequence[str]) -> dict:
    """Ocupación ponderada, cuartos libres por día y estadía en los meses con ambos datos."""
    meses_cuartos = [
        p
        for p in periodos
        if datos.get(p, {}).get("cuartos_disponibles") is not None
        and datos.get(p, {}).get("cuartos_ocupados") is not None
    ]
    disponibles, _ = _suma(datos, meses_cuartos, "cuartos_disponibles")
    ocupados, _ = _suma(datos, meses_cuartos, "cuartos_ocupados")
    dias = sum(dias_del_periodo(p) for p in meses_cuartos)
    llegadas, meses_llegadas = _suma(datos, periodos, "llegadas_turistas")
    noches, _ = _suma(datos, periodos, "turistas_noche")
    afluencia, _ = _suma(datos, periodos, "afluencia_visitantes")
    return {
        "ocupacion_pct": 100 * ocupados / disponibles if disponibles > 0 else None,
        "cuartos_libres_dia": (disponibles - ocupados) / dias if dias > 0 else None,
        "estadia_noches": noches / llegadas if llegadas > 0 else None,
        "llegadas": llegadas,
        "afluencia_estimada": afluencia or None,
        "meses_con_dato": len(meses_cuartos),
        "meses_llegadas": meses_llegadas,
    }


CAMPOS_OFERTA = [
    {"campo": "ocupacion_pct", "metric_id": "ocupacion_12m", "procedencia": "medido"},
    {"campo": "cuartos_libres_dia", "metric_id": "cuartos_libres_dia_12m", "procedencia": "medido"},
    {"campo": "estadia_noches", "metric_id": "estadia_12m", "procedencia": "medido"},
    {
        "campo": "crecimiento_llegadas_pct",
        "metric_id": "crecimiento_llegadas_12m",
        "procedencia": "medido",
    },
    {
        "campo": "participacion_pct",
        "metric_id": "participacion_llegadas_12m",
        "procedencia": "medido",
    },
    {"campo": "llegadas", "metric_id": "llegadas_turistas", "procedencia": "medido"},
    {"campo": "afluencia_estimada", "metric_id": "afluencia_12m", "procedencia": "derivado"},
    {"campo": "poi_catalogo", "metric_id": "poi_catalogo_destino", "procedencia": "medido"},
    {"campo": "candidato", "metric_id": "candidato_destino_alternativo", "procedencia": "medido"},
]


def calcular_oferta_demanda(
    filas: Iterable[FilaOficial],
    nombres: dict[str, str] | None = None,
    poi_por_destino: dict[str, dict[str, int]] | None = None,
) -> dict:
    """Cálculo puro sobre la serie oficial. Las pruebas lo comparan contra valores a mano."""
    nombres = nombres or {}
    poi_por_destino = poi_por_destino or {}
    por_centro: dict[tuple[str, str], dict[str, dict[str, float | None]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    destino_de: dict[str, str | None] = {}
    for f in filas:
        por_centro[(f.centro_ot, f.nivel)][f.periodo][f.indicador] = f.valor
        if f.nivel == NIVEL_DESTINO:
            destino_de[f.centro_ot] = f.destino_id

    centros = sorted(c for c, nivel in por_centro if nivel == NIVEL_DESTINO)
    llegadas_por_periodo: dict[str, float] = defaultdict(float)
    for c in centros:
        for p, ind in por_centro[(c, NIVEL_DESTINO)].items():
            llegadas_por_periodo[p] += ind.get("llegadas_turistas") or 0
    publicados = sorted(p for p, v in llegadas_por_periodo.items() if v > 0)
    ventana = publicados[-12:]
    previa = publicados[-24:-12]

    # Estado: la fila agregada de la fuente si existe; si no, la suma de los centros.
    if (CENTRO_ESTADO, "agregado") in por_centro:
        datos_estado = por_centro[(CENTRO_ESTADO, "agregado")]
        estado_origen = "fila «Estado» de la fuente"
    else:
        datos_estado = defaultdict(dict)
        for c in centros:
            for p, ind in por_centro[(c, NIVEL_DESTINO)].items():
                for nombre, v in ind.items():
                    if v is not None:
                        datos_estado[p][nombre] = (datos_estado[p].get(nombre) or 0) + v
        estado_origen = "suma de los centros"
    estado = _hoteleros(datos_estado, ventana)

    destinos = []
    for c in centros:
        datos = por_centro[(c, NIVEL_DESTINO)]
        h = _hoteleros(datos, ventana)
        previas, meses_previa = _suma(datos, previa, "llegadas_turistas")
        crecimiento, motivo = None, None
        if h["meses_llegadas"] == 12 and meses_previa == 12 and previas > 0:
            crecimiento = 100 * (h["llegadas"] / previas - 1)
        else:
            motivo = "sin evidencia suficiente: faltan meses en alguna ventana"
        destino_id = destino_de.get(c)
        destinos.append(
            {
                "destino_id": destino_id,
                "centro_ot": c,
                "nombre": nombres.get(destino_id or "", c),
                **h,
                "crecimiento_llegadas_pct": crecimiento,
                "crecimiento_motivo": motivo,
                "poi_catalogo": poi_por_destino.get(destino_id or "", {"real": 0, "sintetico": 0}),
                "serie_ocupacion": [
                    {
                        "periodo": p,
                        "ocupacion_pct": (
                            100 * datos[p]["cuartos_ocupados"] / datos[p]["cuartos_disponibles"]
                            if datos.get(p, {}).get("cuartos_disponibles")
                            and datos[p].get("cuartos_ocupados") is not None
                            else None
                        ),
                    }
                    for p in ventana
                ],
            }
        )

    total_llegadas = sum(d["llegadas"] for d in destinos)
    for d in destinos:
        d["participacion_pct"] = 100 * d["llegadas"] / total_llegadas if total_llegadas else None

    # Candidatos: ocupación menor que la del Estado y cuartos libres ≥ mediana de los destinos.
    libres = [d["cuartos_libres_dia"] for d in destinos if d["cuartos_libres_dia"] is not None]
    mediana_libres = statistics.median(libres) if libres else None
    candidatos = []
    for d in destinos:
        d["candidato"] = bool(
            estado["ocupacion_pct"] is not None
            and mediana_libres is not None
            and d["ocupacion_pct"] is not None
            and d["cuartos_libres_dia"] is not None
            and d["ocupacion_pct"] < estado["ocupacion_pct"]
            and d["cuartos_libres_dia"] >= mediana_libres
        )
        if d["candidato"]:
            candidatos.append(
                {
                    "destino_id": d["destino_id"],
                    "nombre": d["nombre"],
                    "ocupacion_pct": d["ocupacion_pct"],
                    "cuartos_libres_dia": d["cuartos_libres_dia"],
                    "poi_catalogo": d["poi_catalogo"],
                    "motivo": (
                        f"Ocupación {d['ocupacion_pct']:.1f} % menor que la del Estado "
                        f"({estado['ocupacion_pct']:.1f} %) y {d['cuartos_libres_dia']:.0f} "
                        f"cuartos libres por día (mediana de los destinos: {mediana_libres:.0f})"
                    ),
                }
            )
    candidatos.sort(key=lambda c: -c["cuartos_libres_dia"])
    destinos.sort(key=lambda d: -(d["llegadas"] or 0))

    llegadas_estado = estado["llegadas"]
    serie_anual = []
    for anio in sorted({p[:4] for p in publicados}):
        meses = [p for p in publicados if p.startswith(anio)]
        por_c = [
            _suma(por_centro[(c, NIVEL_DESTINO)], meses, "llegadas_turistas")[0] for c in centros
        ]
        serie_anual.append(
            {
                "anio": int(anio),
                "hhi": hhi(por_c),
                "meses": len(meses),
                "centros": sum(1 for v in por_c if v > 0),
                "parcial": len(meses) < 12,
            }
        )

    return {
        "ventana": {
            "desde": ventana[0] if ventana else None,
            "hasta": ventana[-1] if ventana else None,
            "meses": len(ventana),
        },
        "estado": {**estado, "origen": estado_origen},
        "hhi": {
            "ventana_12m": hhi(d["llegadas"] for d in destinos),
            "centros": sum(1 for d in destinos if d["llegadas"] > 0),
            "cobertura_estado_pct": (
                100 * total_llegadas / llegadas_estado if llegadas_estado else None
            ),
            "serie_anual": serie_anual,
        },
        "mediana_cuartos_libres_dia": mediana_libres,
        "destinos": destinos,
        "candidatos": candidatos,
    }


def oferta_demanda(s: Session) -> dict:
    filas = [
        FilaOficial(*f)
        for f in s.execute(
            select(
                AggregateMetric.centro_ot,
                AggregateMetric.destino_id,
                AggregateMetric.nivel,
                AggregateMetric.periodo,
                AggregateMetric.metric_id,
                AggregateMetric.valor,
            ).where(
                AggregateMetric.metric_id.in_(INDICADORES_OFERTA),
                AggregateMetric.is_synthetic.is_(False),
                AggregateMetric.centro_ot.is_not(None),
            )
        )
    ]
    nombres = dict(s.execute(select(Destination.destino_id, Destination.nombre)).all())
    poi: dict[str, dict[str, int]] = defaultdict(lambda: {"real": 0, "sintetico": 0})
    for destino_id, sintetico, n in s.execute(
        select(PointOfInterest.destino_id, PointOfInterest.is_synthetic, func.count()).group_by(
            PointOfInterest.destino_id, PointOfInterest.is_synthetic
        )
    ):
        poi[destino_id]["sintetico" if sintetico else "real"] = n
    resultado = calcular_oferta_demanda(filas, nombres, dict(poi))
    fuentes_ids = sorted(
        set(
            s.scalars(
                select(AggregateMetric.fuente_id)
                .where(AggregateMetric.metric_id.in_(INDICADORES_OFERTA))
                .distinct()
            )
        )
        - {None}
    )
    calculado = s.scalar(
        select(func.max(AggregateMetric.calculado_en)).where(
            AggregateMetric.metric_id.in_(INDICADORES_OFERTA)
        )
    )
    return {
        "modulo": "oferta_demanda",
        "is_synthetic": False,
        **resultado,
        "campos": CAMPOS_OFERTA,
        "fichas": [
            ficha_resumen(m)
            for m in (
                "ocupacion_12m",
                "cuartos_libres_dia_12m",
                "estadia_12m",
                "crecimiento_llegadas_12m",
                "participacion_llegadas_12m",
                "hhi_llegadas",
                "candidato_destino_alternativo",
                "poi_catalogo_destino",
                "afluencia_12m",
            )
        ],
        "fuentes": [f for f in (fuente(s, i) for i in fuentes_ids) if f],
        "serie_cargada_en": calculado.isoformat() if calculado else None,
        "calculado_en": ahora_iso(),
    }


# ---------------------------------------------------------------------------
# Inclusión


ESTADOS_COBERTURA = ("verificado", "reportado", "en_moderacion", "sin_verificar", "sin_dato")


def _cobertura_poi(atributos: dict[str, tuple[str | None, str]]) -> str:
    verificados = {a for a, (_, estado) in atributos.items() if estado == "verificado"}
    if {"acceso_sin_escalones", "banio_accesible"} <= verificados:
        return "verificada"
    return "parcial" if verificados else "sin_verificar"


def brechas_accesibilidad(s: Session, corredor_id: str | None = None) -> dict:
    k = k_minimo()
    consulta = select(
        PointOfInterest.poi_id,
        PointOfInterest.nombre,
        PointOfInterest.destino_id,
        PointOfInterest.is_synthetic,
    )
    if corredor_id:
        consulta = consulta.where(PointOfInterest.corredor_id == corredor_id)
    pois = {p: (nombre, d, sint) for p, nombre, d, sint in s.execute(consulta)}

    # Atributos del mismo tipo que su lugar: un dato sintético no cuenta en el bloque real.
    atributos: dict[str, dict[str, tuple[str | None, str]]] = defaultdict(dict)
    comunitarios: list[dict] = []
    for poi_id, atributo, valor, estado, origen, sintetico in s.execute(
        select(
            POIAccessibilityAttribute.poi_id,
            POIAccessibilityAttribute.atributo,
            POIAccessibilityAttribute.valor,
            POIAccessibilityAttribute.estado,
            POIAccessibilityAttribute.origen,
            POIAccessibilityAttribute.is_synthetic,
        )
    ):
        if poi_id not in pois:
            continue
        if origen == "comunidad" and estado == "reportado":
            # Lo que toca algo sintético se marca sintético.
            comunitarios.append(
                {
                    "poi_id": poi_id,
                    "nombre": pois[poi_id][0],
                    "atributo": atributo,
                    "valor": valor,
                    "is_synthetic": sintetico or pois[poi_id][2],
                }
            )
        if sintetico != pois[poi_id][2]:
            continue
        atributos[poi_id][atributo] = (valor, estado)

    nombres = dict(s.execute(select(Destination.destino_id, Destination.nombre)).all())
    por_destino: dict[tuple[str, bool], dict] = {}
    por_atributo: dict[tuple[str, bool], dict] = {}
    for poi_id, (_, destino_id, sintetico) in pois.items():
        g = por_destino.setdefault(
            (destino_id, sintetico),
            {
                "destino_id": destino_id,
                "nombre": nombres.get(destino_id, destino_id),
                "is_synthetic": sintetico,
                "poi": 0,
                "con_informacion": 0,
                "verificada": 0,
                "parcial": 0,
                "sin_verificar": 0,
            },
        )
        attrs = atributos.get(poi_id, {})
        g["poi"] += 1
        if any(valor is not None for valor, _ in attrs.values()):
            g["con_informacion"] += 1
        g[_cobertura_poi(attrs)] += 1
        for atributo in ATRIBUTOS_ACCESIBILIDAD:
            a = por_atributo.setdefault(
                (atributo, sintetico),
                {
                    "atributo": atributo,
                    "is_synthetic": sintetico,
                    "poi": 0,
                    "con_valor": 0,
                    **{e: 0 for e in ESTADOS_COBERTURA},
                },
            )
            a["poi"] += 1
            valor, estado = attrs.get(atributo, (None, "sin_dato"))
            if valor is None:
                a["sin_dato"] += 1
            else:
                a["con_valor"] += 1
                a[estado] += 1

    destinos = sorted(por_destino.values(), key=lambda g: (g["is_synthetic"], -g["poi"]))
    for g in destinos:
        g["con_informacion_pct"] = 100 * g["con_informacion"] / g["poi"]
        g["verificada_pct"] = 100 * g["verificada"] / g["poi"]
    por_attr = sorted(
        por_atributo.values(),
        key=lambda a: (a["is_synthetic"], ATRIBUTOS_ACCESIBILIDAD.index(a["atributo"])),
    )
    for a in por_attr:
        a["con_valor_pct"] = 100 * a["con_valor"] / a["poi"]
        a["verificado_pct"] = 100 * a["verificado"] / a["poi"]

    resumen = []
    for sintetico in sorted({g["is_synthetic"] for g in destinos}):
        grupo = [g for g in destinos if g["is_synthetic"] == sintetico]
        total = sum(g["poi"] for g in grupo)
        resumen.append(
            {
                "is_synthetic": sintetico,
                "poi": total,
                "con_informacion_pct": 100 * sum(g["con_informacion"] for g in grupo) / total,
                "verificada_pct": 100 * sum(g["verificada"] for g in grupo) / total,
                "parcial_pct": 100 * sum(g["parcial"] for g in grupo) / total,
                "sin_verificar_pct": 100 * sum(g["sin_verificar"] for g in grupo) / total,
            }
        )

    barreras = _barreras(s, pois, k)
    prioridades = _prioridades(destinos, por_attr, comunitarios)
    return {
        "modulo": "inclusion",
        "corredor_id": corredor_id,
        "k_minimo": k,
        "aviso": (
            "Cobertura de información, no nivel de accesibilidad: la falta de un dato nunca "
            "significa que el lugar sea accesible."
        ),
        "resumen": resumen,
        "por_destino": destinos,
        "por_atributo": por_attr,
        "barreras": barreras,
        "prioridades": prioridades,
        "hay_sinteticos": any(r["is_synthetic"] for r in resumen)
        or any(b["is_synthetic"] for b in barreras),
        "fichas": [
            ficha_resumen(m)
            for m in (
                "cobertura_info_accesibilidad",
                "cobertura_atributo",
                "barreras_reportadas",
                "tiempo_moderacion_mediano_h",
            )
        ],
        "fuentes": [f for f in (fuente(s, "pv360-catalogo"), fuente(s, "pv360-moderacion")) if f],
        "calculado_en": ahora_iso(),
    }


def _barreras(s: Session, pois: dict[str, tuple], k: int) -> list[dict]:
    filas = s.execute(
        select(
            ModerationCase.poi_id,
            ModerationCase.tipo,
            ModerationCase.estado,
            ModerationCase.creado_en,
            ModerationCase.decidido_en,
            ModerationCase.is_synthetic,
            ModerationCase.id,
            CommunityReport.user_id,
        ).outerjoin(CommunityReport, CommunityReport.id == ModerationCase.community_report_id)
    ).all()
    grupos: dict[bool, dict] = {}
    personas: dict[bool, set] = defaultdict(set)
    horas: dict[bool, list[float]] = defaultdict(list)
    for poi_id, tipo, estado, creado, decidido, sintetico, caso_id, user_id in filas:
        if poi_id not in pois:
            continue
        # Un caso sobre un lugar sintético cuenta en el bloque sintético.
        sintetico = sintetico or pois[poi_id][2]
        g = grupos.setdefault(
            sintetico,
            {
                "is_synthetic": sintetico,
                "casos": 0,
                "abiertos": 0,
                "aceptados": 0,
                "rechazados": 0,
                "por_tipo": defaultdict(lambda: {"casos": 0, "aceptados": 0}),
            },
        )
        g["casos"] += 1
        g[{"abierto": "abiertos", "aceptado": "aceptados", "rechazado": "rechazados"}[estado]] += 1
        g["por_tipo"][tipo]["casos"] += 1
        if estado == "aceptado":
            g["por_tipo"][tipo]["aceptados"] += 1
        # Un caso cuya persona borró su cuenta cuenta como una persona más (estimación prudente).
        personas[sintetico].add(user_id or f"caso:{caso_id}")
        if decidido is not None:
            horas[sintetico].append((decidido - creado).total_seconds() / 3600)

    resultado = []
    for sintetico, g in sorted(grupos.items()):
        decididos = g["aceptados"] + g["rechazados"]
        g["por_tipo"] = [{"tipo": t, **v} for t, v in sorted(g["por_tipo"].items())]
        g["tasa_aceptacion"] = g["aceptados"] / decididos if decididos else None
        g["tasa_aceptacion_ic"] = wilson(g["aceptados"], decididos)
        g["tiempo_moderacion_mediano_h"] = (
            statistics.median(horas[sintetico]) if horas[sintetico] else None
        )
        g["personas"] = len(personas[sintetico])
        resultado.append(g)
    # Cada bloque (real o sintético) es su propia partición: no hay complementaria entre ellos.
    for g in resultado:
        suprimir(
            [g],
            k,
            [
                "casos",
                "abiertos",
                "aceptados",
                "rechazados",
                "por_tipo",
                "tasa_aceptacion",
                "tasa_aceptacion_ic",
                "tiempo_moderacion_mediano_h",
            ],
        )
    return resultado


NOMBRE_ATRIBUTO = {
    "acceso_sin_escalones": "acceso sin escalones",
    "rampa": "rampa",
    "banio_accesible": "baño accesible",
    "elevador": "elevador",
    "superficie": "superficie",
    "asientos": "asientos de descanso",
    "estacionamiento_reservado": "estacionamiento reservado",
    "pendiente_pct": "pendiente",
    "numero_escalones": "número de escalones",
}


def _prioridades(destinos: list[dict], atributos: list[dict], comunitarios: list[dict]) -> list:
    """Sugerencias generadas desde los datos. Son para validar con la Secretaría."""
    prioridades = []
    for sintetico in sorted({g["is_synthetic"] for g in destinos}):
        grupo = [g for g in destinos if g["is_synthetic"] == sintetico]
        for g in sorted(grupo, key=lambda g: (g["con_informacion_pct"], -g["poi"]))[:3]:
            prioridades.append(
                {
                    "tipo": "verificar_destino",
                    "is_synthetic": sintetico,
                    "destino_id": g["destino_id"],
                    "sugerencia": (
                        f"Verificar accesibilidad en {g['nombre']}: {g['con_informacion']} de "
                        f"{g['poi']} lugares tienen algún dato ({g['con_informacion_pct']:.0f} %)."
                    ),
                }
            )
        attrs = [a for a in atributos if a["is_synthetic"] == sintetico]
        for a in sorted(attrs, key=lambda a: a["con_valor_pct"])[:2]:
            prioridades.append(
                {
                    "tipo": "levantar_atributo",
                    "is_synthetic": sintetico,
                    "atributo": a["atributo"],
                    "sugerencia": (
                        f"Levantar «{NOMBRE_ATRIBUTO[a['atributo']]}»: solo "
                        f"{a['con_valor_pct']:.0f} % de los lugares tiene el dato."
                    ),
                }
            )
    for c in sorted(comunitarios, key=lambda c: (c["is_synthetic"], c["nombre"]))[:5]:
        prioridades.append(
            {
                "tipo": "atender_barrera",
                "is_synthetic": c["is_synthetic"],
                "poi_id": c["poi_id"],
                "sugerencia": (
                    f"Atender la barrera aceptada en {c['nombre']}: "
                    f"{NOMBRE_ATRIBUTO[c['atributo']]} = «{c['valor']}» (reporte de la comunidad)."
                ),
            }
        )
    return prioridades


# ---------------------------------------------------------------------------
# Panorama


def _periodo(fecha: datetime) -> str:
    return f"{fecha.year:04d}-{fecha.month:02d}"


def panorama(s: Session, periodo: str | None = None) -> dict:
    k = k_minimo()
    nombres = dict(s.execute(select(Destination.destino_id, Destination.nombre)).all())
    poi_destino = dict(
        s.execute(
            select(PointOfInterest.destino_id, func.count()).group_by(PointOfInterest.destino_id)
        ).all()
    )
    visitas = s.execute(
        select(
            PointOfInterest.destino_id,
            ConfirmedVisit.is_synthetic,
            ConfirmedVisit.user_id,
            ConfirmedVisit.poi_id,
            ConfirmedVisit.fecha,
            ConfirmedVisit.confianza,
            ConfirmedVisit.fuente_evidencia,
        )
        .join(PointOfInterest, PointOfInterest.poi_id == ConfirmedVisit.poi_id)
        .where(ConfirmedVisit.confirmada.is_(True))
    ).all()
    estancias = s.execute(
        select(
            PointOfInterest.destino_id,
            VisitCandidate.is_synthetic,
            TripSession.user_id,
            VisitCandidate.inicio,
            VisitCandidate.duracion_min,
        )
        .join(TripSession, TripSession.id == VisitCandidate.session_id)
        .join(PointOfInterest, PointOfInterest.poi_id == VisitCandidate.poi_id)
        .where(VisitCandidate.estado == "visita_probable")
    ).all()

    grupos: dict[tuple[str, bool], dict] = {}
    for destino_id, sintetico, user_id, poi_id, fecha, confianza, fuente_ev in visitas:
        if periodo and _periodo(fecha) != periodo:
            continue
        g = grupos.setdefault(
            (destino_id, sintetico),
            {"usuarios": set(), "pois": set(), "confianzas": [], "fuentes": defaultdict(int)},
        )
        g["usuarios"].add(user_id)
        g["pois"].add(poi_id)
        g["confianzas"].append(confianza)
        g["fuentes"][fuente_ev] += 1
    duraciones: dict[tuple[str, bool], dict] = {}
    for destino_id, sintetico, user_id, inicio, duracion in estancias:
        if periodo and _periodo(inicio) != periodo:
            continue
        d = duraciones.setdefault((destino_id, sintetico), {"usuarios": set(), "valores": []})
        d["usuarios"].add(user_id)
        d["valores"].append(duracion)

    filas = []
    for llave in sorted(set(grupos) | set(duraciones), key=lambda x: (x[1], x[0])):
        destino_id, sintetico = llave
        g = grupos.get(llave)
        d = duraciones.get(llave)
        visitas_n = len(g["confianzas"]) if g else 0
        q = cuantiles(sorted(d["valores"])) if d else None
        filas.append(
            {
                "destino_id": destino_id,
                "nombre": nombres.get(destino_id, destino_id),
                "is_synthetic": sintetico,
                "personas": len(g["usuarios"]) if g else 0,
                "visitas_observadas": visitas_n,
                "confianza_media": statistics.fmean(g["confianzas"]) if g else None,
                "por_fuente_evidencia": (
                    {f: n / visitas_n for f, n in sorted(g["fuentes"].items())} if g else None
                ),
                "cobertura_poi_pct": (
                    100 * len(g["pois"]) / poi_destino[destino_id]
                    if g and poi_destino.get(destino_id)
                    else None
                ),
                "permanencia": {
                    "personas": len(d["usuarios"]) if d else 0,
                    "n": len(d["valores"]) if d else 0,
                    "p25_min": q[0] if q else None,
                    "mediana_min": q[1] if q else None,
                    "p75_min": q[2] if q else None,
                },
            }
        )

    campos = ["visitas_observadas", "confianza_media", "por_fuente_evidencia", "cobertura_poi_pct"]
    for sintetico in (False, True):
        particion = [f for f in filas if f["is_synthetic"] == sintetico]
        suprimir(particion, k, campos)
        permanencias = [f["permanencia"] for f in particion]
        suprimir(permanencias, k, ["n", "p25_min", "mediana_min", "p75_min"])

    # Serie mensual de visitas (todos los destinos), por tipo de dato.
    serie: dict[tuple[str, bool], dict] = {}
    for _, sintetico, user_id, _, fecha, _, _ in visitas:
        p = _periodo(fecha)
        g = serie.setdefault((p, sintetico), {"usuarios": set(), "visitas": 0})
        g["usuarios"].add(user_id)
        g["visitas"] += 1
    por_periodo = [
        {
            "periodo": p,
            "is_synthetic": sint,
            "personas": len(g["usuarios"]),
            "visitas": g["visitas"],
        }
        for (p, sint), g in sorted(serie.items(), key=lambda x: (x[0][1], x[0][0]))
    ]
    for sintetico in (False, True):
        suprimir([f for f in por_periodo if f["is_synthetic"] == sintetico], k, ["visitas"])

    return {
        "modulo": "panorama",
        "periodo": periodo,
        "k_minimo": k,
        "aviso": (
            "Muestra de personas que usan la app con consentimiento; no es el total de turistas."
        ),
        "grupos": filas,
        "por_periodo": por_periodo,
        "hay_reales": any(not f["is_synthetic"] for f in filas),
        "hay_sinteticos": any(f["is_synthetic"] for f in filas),
        "fichas": [
            ficha_resumen(m)
            for m in (
                "visitas_observadas",
                "visitantes_distintos",
                "permanencia_mediana_min",
                "confianza_media_visitas",
            )
        ],
        "fuentes": [f for f in (fuente(s, "pv360-visitas"),) if f],
        "calculado_en": ahora_iso(),
    }


# ---------------------------------------------------------------------------
# Experiencia

TODOS = "todos"


def experiencia(s: Session) -> dict:
    k = k_minimo()
    nombres = dict(s.execute(select(Destination.destino_id, Destination.nombre)).all())
    filas = s.execute(
        select(
            PointOfInterest.destino_id,
            Review.is_synthetic,
            Review.user_id,
            ReviewDimension.dimension,
            ReviewDimension.puntaje,
        )
        .join(Review, Review.id == ReviewDimension.review_id)
        .join(PointOfInterest, PointOfInterest.poi_id == Review.poi_id)
    ).all()
    grupos: dict[tuple[str, str, bool], dict] = {}
    for destino_id, sintetico, user_id, dimension, puntaje in filas:
        for destino in (destino_id, TODOS):
            g = grupos.setdefault((destino, dimension, sintetico), {"usuarios": set(), "p": []})
            g["usuarios"].add(user_id)
            g["p"].append(puntaje)

    salida = []
    for (destino, dimension, sintetico), g in grupos.items():
        n = len(g["p"])
        bajas = sum(1 for p in g["p"] if p <= 2)
        salida.append(
            {
                "destino_id": None if destino == TODOS else destino,
                "nombre": "Todos los destinos"
                if destino == TODOS
                else nombres.get(destino, destino),
                "dimension": dimension,
                "is_synthetic": sintetico,
                "personas": len(g["usuarios"]),
                "n": n,
                "media": statistics.fmean(g["p"]),
                "media_ic95": bootstrap_media(g["p"]),
                "proporcion_baja": bajas / n,
                "proporcion_baja_ic95": wilson(bajas, n),
            }
        )
    orden = {d: i for i, d in enumerate(DIMENSIONES)}
    salida.sort(
        key=lambda f: (
            f["is_synthetic"],
            f["destino_id"] is not None,
            f["nombre"],
            orden.get(f["dimension"], 99),
        )
    )
    campos = ["n", "media", "media_ic95", "proporcion_baja", "proporcion_baja_ic95"]
    # Partición: misma dimensión y tipo de dato, entre destinos; el total va aparte. Con la
    # supresión complementaria, total − visibles solo revela la suma de dos o más suprimidos.
    for sintetico in (False, True):
        for dimension in DIMENSIONES:
            particion = [
                f
                for f in salida
                if f["is_synthetic"] == sintetico
                and f["dimension"] == dimension
                and f["destino_id"] is not None
            ]
            suprimir(particion, k, campos)
            totales = [
                f
                for f in salida
                if f["is_synthetic"] == sintetico
                and f["dimension"] == dimension
                and f["destino_id"] is None
            ]
            suprimir(totales, k, campos)
    return {
        "modulo": "experiencia",
        "k_minimo": k,
        "aviso": "Reseñas de quien decide reseñar (sesgo de autoselección); muestra de la app.",
        "grupos": salida,
        "dimensiones": list(DIMENSIONES),
        "hay_reales": any(not f["is_synthetic"] for f in salida),
        "hay_sinteticos": any(f["is_synthetic"] for f in salida),
        "fichas": [
            ficha_resumen(m)
            for m in ("satisfaccion_media_dimension", "proporcion_calificacion_baja")
        ],
        "fuentes": [f for f in (fuente(s, "pv360-resenas"),) if f],
        "calculado_en": ahora_iso(),
    }


# ---------------------------------------------------------------------------
# Linaje


def linaje(s: Session, metric_id: str) -> dict | None:
    definicion = s.get(MetricDefinition, metric_id)
    ficha = definiciones.fichas().get(metric_id)
    if definicion is None and ficha is None:
        return None
    filas = s.execute(
        select(DataLineage, DataSource)
        .join(DataSource, DataSource.fuente_id == DataLineage.fuente_id)
        .where(DataLineage.entidad == definiciones.ENTIDAD, DataLineage.entidad_id == metric_id)
        .order_by(DataLineage.fuente_id)
    ).all()
    fuentes = [
        {
            **(fuente(s, origen.fuente_id) or {}),
            "metodo": lin.metodo,
            "registrado_en": lin.fecha.isoformat() if lin.fecha else None,
        }
        for lin, origen in filas
    ]
    if not fuentes and definicion is not None and definicion.fuente_id:
        f = fuente(s, definicion.fuente_id)
        if f:
            fuentes = [{**f, "metodo": definicion.formula, "registrado_en": None}]
    almacenado = s.execute(
        select(
            func.count(),
            func.min(AggregateMetric.periodo),
            func.max(AggregateMetric.periodo),
            func.max(AggregateMetric.calculado_en),
        ).where(AggregateMetric.metric_id == metric_id)
    ).one()
    return {
        "metric_id": metric_id,
        "definicion": (
            {
                "nombre": definicion.nombre,
                "descripcion": definicion.descripcion,
                "formula": definicion.formula,
                "version_formula": definicion.version_formula,
                "unidad": definicion.unidad,
                "denominador": definicion.denominador,
                "procedencia": definicion.procedencia,
                "fuente_id": definicion.fuente_id,
                "k_minimo": definicion.k_minimo,
            }
            if definicion
            else None
        ),
        "ficha": ficha,
        "fuentes": fuentes,
        "agregados_guardados": {
            "filas": almacenado[0],
            "periodo_desde": almacenado[1],
            "periodo_hasta": almacenado[2],
            "calculado_en": almacenado[3].isoformat() if almacenado[3] else None,
        },
        "calculo": (
            "Serie guardada en analytics.aggregate_metric"
            if almacenado[0]
            else "Se calcula al pedirlo desde las tablas de origen; solo sale el agregado"
        ),
        "k_minimo_aplicado": k_minimo(),
    }


# ---------------------------------------------------------------------------
# CSV con metadatos


def a_csv(metadatos: dict[str, object], filas: list[dict]) -> str:
    salida = io.StringIO()
    for clave, valor in metadatos.items():
        salida.write(f"# {clave}: {valor}\n")
    if filas:
        columnas = list(filas[0].keys())
        escritor = csv.DictWriter(salida, fieldnames=columnas, lineterminator="\n")
        escritor.writeheader()
        for f in filas:
            escritor.writerow({c: _celda(f.get(c)) for c in columnas})
    return salida.getvalue()


def _celda(valor: object) -> object:
    if isinstance(valor, bool) or valor is None:
        return "" if valor is None else str(valor).lower()
    if isinstance(valor, float):
        return f"{valor:.4f}"
    if isinstance(valor, tuple | list):
        return "|".join(str(_celda(v)) for v in valor)
    if isinstance(valor, dict):
        return "|".join(f"{k}={_celda(v)}" for k, v in valor.items())
    return valor
