"""Parámetros del recomendador. Cada valor está documentado en la model card.

Los valores son supuestos de trabajo, no calibraciones: se revisan con la
auditoría del corredor y con retroalimentación de visitantes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

SEMILLA = 2026

# Movilidad peatonal: haversine × factor de desvío a velocidad conservadora.
VELOCIDAD_KMH = 4.5
FACTOR_DESVIO = 1.3

# Confianza mínima para aceptar un atributo «sin_verificar» como cumplido.
CONFIANZA_MINIMA = 0.6

# Descansos y baños.
DURACION_DESCANSO_MIN = 10
INTERVALO_BANIO_MIN = 90
ESTANCIA_BANIO_MIN = 8

# Tamaño de la celda que define una «zona» para medir diversidad.
TAMANO_ZONA_M = 500.0

# Categorías de servicio: no se recomiendan como atractivo, se insertan.
CATEGORIAS_BANIO = frozenset({"banio", "sanitario", "toilets"})
CATEGORIAS_SERVICIO = CATEGORIAS_BANIO | frozenset({"banca", "descanso"})

# Estancia típica por categoría (min). Supuesto de trabajo.
ESTANCIA_POR_CATEGORIA: dict[str, int] = {
    "museo": 60,
    "zona_arqueologica": 75,
    "templo": 25,
    "galeria": 40,
    "mirador": 20,
    "mercado": 40,
    "artesanias": 30,
    "restaurante": 60,
    "cafe": 30,
    "cafeteria": 30,
    "parque": 30,
    "plaza": 20,
    "monumento": 15,
    "teatro": 30,
    "biblioteca": 30,
    "barrio": 40,
}
ESTANCIA_DEFECTO = 30

ORDEN_PRESUPUESTO = {"gratis": 0, "bajo": 1, "medio": 2, "alto": 3}

# Polos saturados cuando el catálogo no trae popularidad (boletín estatal, §02).
POLOS_SATURADOS = frozenset({"puebla", "cholula"})


@dataclass(frozen=True)
class Pesos:
    """Pesos del ranking multiobjetivo (etapa 2).

    puntuacion = pertinencia·w_p + cercania·w_c + diversidad·w_d
                 + calidad·w_q − esfuerzo·w_e
    """

    pertinencia: float = 0.40
    cercania: float = 0.20
    diversidad: float = 0.20
    calidad: float = 0.10
    esfuerzo: float = 0.10
    # Penalizaciones dinámicas al construir la ruta (estilo MMR).
    repetir_zona: float = 0.08
    repetir_categoria: float = 0.10
    # Exponente del costo en tiempo en la regla voraz: utilidad / (Δt + 1)^exp.
    exponente_tiempo: float = 0.5


@dataclass(frozen=True)
class Config:
    pesos: Pesos = field(default_factory=Pesos)
    velocidad_kmh: float = VELOCIDAD_KMH
    factor_desvio: float = FACTOR_DESVIO
    confianza_minima: float = CONFIANZA_MINIMA
    duracion_descanso_min: int = DURACION_DESCANSO_MIN
    intervalo_banio_min: int = INTERVALO_BANIO_MIN
    estancia_banio_min: int = ESTANCIA_BANIO_MIN
    tamano_zona_m: float = TAMANO_ZONA_M
    # Una sola comida o café por ruta de un día: evita rutas de dos restaurantes.
    max_por_categoria: dict[str, int] = field(
        default_factory=lambda: {"restaurante": 1, "cafe": 1, "cafeteria": 1, "mercado": 1}
    )
    max_candidatos: int = 40
    max_alternativos: int = 5
    semilla: int = SEMILLA


CONFIG_DEFECTO = Config()


def es_alternativo(poi) -> bool:
    """Destino alternativo: el dato del catálogo o, si falta, no ser polo saturado."""
    if poi.es_destino_alternativo is not None:
        return bool(poi.es_destino_alternativo)
    return poi.destino_id not in POLOS_SATURADOS


def popularidad(poi) -> float:
    """Popularidad de 0 a 1: el dato del catálogo o, si falta, 0.8 en polos y 0.3 fuera."""
    if poi.popularidad is not None:
        return min(max(float(poi.popularidad), 0.0), 1.0)
    return 0.8 if poi.destino_id in POLOS_SATURADOS else 0.3


def estancia_tipica(categoria: str) -> int:
    return ESTANCIA_POR_CATEGORIA.get((categoria or "").lower(), ESTANCIA_DEFECTO)
