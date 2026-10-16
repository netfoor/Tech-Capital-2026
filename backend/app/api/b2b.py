"""Tablero institucional con agregados protegidos (spec 019).

Lectura para los roles viewer, analista y admin. Solo salen agregados: sin coordenadas, sin
identificadores de persona y con supresión k en todo lo que viene de personas.
"""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.deps import Sesion
from app.models import User
from app.services import metricas
from app.services.seguridad import requiere_rol

router = APIRouter(prefix="/b2b", tags=["tablero"])
router_metricas = APIRouter(prefix="/metrics", tags=["tablero"])

Lector = Annotated[User, Depends(requiere_rol("viewer", "analista", "admin"))]
Formato = Annotated[Literal["json", "csv"], Query(description="json (por omisión) o csv")]


def _csv(nombre: str, datos: dict, filas: list[dict], extra: dict | None = None) -> Response:
    fichas = datos.get("fichas", [])
    fuentes = datos.get("fuentes", [])
    metadatos = {
        "modulo": datos["modulo"],
        "indicadores": "|".join(f"{f['metric_id']} v{f['version']}" for f in fichas),
        "fuentes": "|".join(
            f"{f['fuente_id']} ({f.get('url') or 'sin URL'}; sha256 {f.get('sha256') or '—'})"
            for f in fuentes
        ),
        "k_minimo": datos.get("k_minimo", "no aplica (no describe personas)"),
        "is_synthetic": (
            "contiene filas sintéticas marcadas en la columna is_synthetic"
            if datos.get("hay_sinteticos")
            else str(datos.get("is_synthetic", False)).lower()
        ),
        **(extra or {}),
        "aviso": datos.get("aviso", ""),
        "calculado_en": datos["calculado_en"],
    }
    return Response(
        content=metricas.a_csv(metadatos, filas),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nombre}.csv"'},
    )


@router.get("/supply-demand", summary="Oferta–demanda con la serie oficial")
def oferta_demanda(s: Sesion, _lector: Lector, formato: Formato = "json"):
    datos = metricas.oferta_demanda(s)
    if formato == "csv":
        filas = [
            {
                "destino_id": d["destino_id"],
                "centro_ot": d["centro_ot"],
                "nombre": d["nombre"],
                "ocupacion_pct": d["ocupacion_pct"],
                "cuartos_libres_dia": d["cuartos_libres_dia"],
                "estadia_noches": d["estadia_noches"],
                "crecimiento_llegadas_pct": d["crecimiento_llegadas_pct"],
                "participacion_pct": d["participacion_pct"],
                "llegadas": d["llegadas"],
                "afluencia_estimada_derivado": d["afluencia_estimada"],
                "meses_con_dato": d["meses_con_dato"],
                "poi_catalogo_real": d["poi_catalogo"]["real"],
                "poi_catalogo_sintetico": d["poi_catalogo"]["sintetico"],
                "candidato_destino_alternativo": d["candidato"],
            }
            for d in datos["destinos"]
        ]
        v = datos["ventana"]
        return _csv(
            "oferta-demanda",
            datos,
            filas,
            {
                "ventana": f"{v['desde']} a {v['hasta']} ({v['meses']} meses)",
                "hhi_llegadas_12m": f"{datos['hhi']['ventana_12m'] or 0:.4f}",
                "procedencia": "medido salvo afluencia_estimada_derivado (derivado por la fuente)",
            },
        )
    return datos


@router.get("/accessibility-gaps", summary="Brechas de información de accesibilidad")
def brechas(
    s: Sesion,
    _lector: Lector,
    corredor_id: str | None = None,
    formato: Formato = "json",
):
    datos = metricas.brechas_accesibilidad(s, corredor_id)
    if formato == "csv":
        filas = [
            {k: v for k, v in g.items() if k != "nombre"} | {"nombre": g["nombre"]}
            for g in datos["por_destino"]
        ]
        return _csv("brechas-accesibilidad", datos, filas, {"corredor_id": corredor_id or "todos"})
    return datos


@router.get("/metrics", summary="Panorama o Experiencia con supresión k")
def indicadores(
    s: Sesion,
    _lector: Lector,
    modulo: Literal["panorama", "experiencia"],
    periodo: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}$")] = None,
    formato: Formato = "json",
):
    if modulo == "panorama":
        datos = metricas.panorama(s, periodo)
        filas = [
            {
                k: v
                for k, v in g.items()
                if k not in ("permanencia", "por_fuente_evidencia", "supresion_complementaria")
            }
            | {
                "permanencia_mediana_min": g["permanencia"]["mediana_min"],
                "permanencia_p25_min": g["permanencia"]["p25_min"],
                "permanencia_p75_min": g["permanencia"]["p75_min"],
                "permanencia_n": g["permanencia"]["n"],
                "permanencia_suprimida": g["permanencia"]["suprimido"],
            }
            for g in datos["grupos"]
        ]
    else:
        datos = metricas.experiencia(s)
        filas = [
            {k: v for k, v in g.items() if k != "supresion_complementaria"} for g in datos["grupos"]
        ]
    if formato == "csv":
        return _csv(modulo, datos, filas, {"periodo": periodo or "todos"})
    return datos


@router_metricas.get("/{metric_id}/lineage", summary="Ficha y linaje de un indicador")
def linaje(metric_id: str, s: Sesion, _lector: Lector):
    datos = metricas.linaje(s, metric_id)
    if datos is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Indicador no encontrado")
    return datos
