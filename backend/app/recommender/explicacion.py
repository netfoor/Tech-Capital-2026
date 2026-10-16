"""Etapa 4: explicación. Cada parada dice por qué está y la ruta dice qué no sabe."""

from __future__ import annotations

from .config import Config
from .elegibilidad import (
    ATR_PENDIENTE,
    ATR_SIN_ESCALONES,
    CUMPLE,
    evaluar_banio,
    evaluar_pendiente,
    evaluar_sin_escalones,
)
from .horarios import parsear
from .ranking import Puntaje
from .tipos import POICandidato, Restricciones

LIMITACION_TRAYECTOS = (
    "Los tiempos de caminata son estimaciones en línea recta con un factor de desvío de 1.3 "
    "a 4.5 km/h; la pendiente y el estado de las banquetas entre paradas no están medidos."
)


ORIGENES = {
    "equipo": "el equipo verificador",
    "prestador": "el prestador",
    "comunidad": "la comunidad",
    "osm": "OpenStreetMap",
}


def _procedencia(poi: POICandidato, atributo: str) -> str:
    a = poi.accesibilidad[atributo]
    quien = ORIGENES.get(a.origen, a.origen or "una fuente sin nombre")
    if a.estado == "verificado":
        return f"está verificado por {quien}"
    return f"viene de {quien} con confianza {a.confianza:.2f}; aún no lo verifica el equipo"


def motivo_parada(
    poi: POICandidato,
    puntaje: Puntaje | None,
    traslado_min: int,
    es_primera: bool,
    restricciones: Restricciones,
    config: Config,
) -> str:
    razones: list[str] = []
    if puntaje and puntaje.intereses_coincidentes:
        razones.append("coincide con tu interés en " + ", ".join(puntaje.intereses_coincidentes))
    if es_primera:
        razones.append("es un buen punto para empezar")
    elif traslado_min <= 10:
        razones.append(f"está a {traslado_min} min caminando de la parada anterior")
    if poi.es_destino_alternativo:
        razones.append("es un destino alternativo con menos afluencia que los polos saturados")
    if restricciones.sin_escalones and evaluar_sin_escalones(poi, config)[0] == CUMPLE:
        razones.append("su acceso sin escalones " + _procedencia(poi, ATR_SIN_ESCALONES))
    if (
        restricciones.pendiente_max_pct is not None
        and evaluar_pendiente(poi, restricciones.pendiente_max_pct, config)[0] == CUMPLE
    ):
        razones.append(
            f"la pendiente del acceso ({poi.accesibilidad[ATR_PENDIENTE].valor} %) no pasa de "
            f"{restricciones.pendiente_max_pct:g} % y " + _procedencia(poi, ATR_PENDIENTE)
        )
    if restricciones.banio_accesible and evaluar_banio(poi, config)[0] == CUMPLE:
        razones.append("tiene baño accesible")
    if not razones:
        razones.append("cabe en tu tiempo y complementa la ruta")
    return "Te lo recomendamos porque " + "; ".join(razones) + "."


def datos_desconocidos_poi(poi: POICandidato, restricciones: Restricciones) -> list[str]:
    faltan: list[str] = []
    if parsear(poi.horario_osm) is None:
        faltan.append(f"{poi.nombre}: horario sin verificar")
    if not poi.costo_rango:
        faltan.append(f"{poi.nombre}: costo sin verificar")
    if restricciones.pendiente_max_pct is None and ATR_PENDIENTE not in poi.accesibilidad:
        faltan.append(f"{poi.nombre}: pendiente del acceso sin dato")
    if not restricciones.sin_escalones and "acceso_sin_escalones" not in poi.accesibilidad:
        faltan.append(f"{poi.nombre}: acceso sin escalones sin verificar")
    return faltan


def resumen(
    n_paradas: int,
    total_min: int,
    disponible_min: int,
    zonas: int,
    restricciones: Restricciones,
    n_sin_verificar: int,
    n_descansos: int,
    n_banios: int,
) -> str:
    if n_paradas == 0:
        texto = (
            "No encontramos una ruta que cumpla todas tus necesidades con los datos que "
            "tenemos. No relajamos ninguna restricción indispensable."
        )
    else:
        horas, minutos = divmod(total_min, 60)
        texto = (
            f"Ruta de {horas} h {minutos:02d} min de {disponible_min} min disponibles, "
            f"con {n_paradas} lugar(es) en {zonas} zona(s)."
        )
    respeta = []
    if restricciones.sin_escalones:
        respeta.append(
            "sin escalones (solo lugares con acceso verificado o con confianza de al menos 0.6)"
        )
    if restricciones.pendiente_max_pct is not None:
        respeta.append(f"pendiente del acceso de hasta {restricciones.pendiente_max_pct:g} %")
    if restricciones.descansos_cada_min:
        respeta.append(
            f"descansos cada {restricciones.descansos_cada_min} min ({n_descansos} programados)"
        )
    if restricciones.banio_accesible:
        respeta.append(f"baño accesible a lo largo de la ruta ({n_banios} parada[s] de baño)")
    if respeta:
        texto += " Respeta: " + "; ".join(respeta) + "."
    if n_sin_verificar:
        texto += (
            f" {n_sin_verificar} lugar(es) quedaron fuera porque falta verificar su "
            "accesibilidad; los ofrecemos solo como alternativas marcadas «sin verificar»."
        )
    return texto
