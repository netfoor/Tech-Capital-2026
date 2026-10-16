"""Etapa 3: secuenciación (orienteering con ventanas de tiempo).

Dos piezas:

1. ``simular``: dado un orden de lugares, construye la línea de tiempo minuto a
   minuto (caminata, espera, visita, descanso, baño) y decide si es factible:
   cabe en el tiempo, respeta horarios verificados y, en modo inteligente,
   inserta descansos y baños accesibles para no violar las restricciones.
2. ``construir_ruta``: inserción voraz por valor/tiempo más mejora 2-opt.
"""

from __future__ import annotations

import copy
from collections.abc import Callable
from dataclasses import dataclass, field

from .config import Config
from .geo import distancia_caminable_m, haversine_m, minutos_caminando, zona
from .tipos import Parada, POICandidato, Restricciones


@dataclass(frozen=True)
class Evento:
    inicio: int
    fin: int
    tipo: str  # traslado | espera | visita | descanso | banio
    poi_id: str | None = None

    def como_dict(self) -> dict:
        return {"inicio": self.inicio, "fin": self.fin, "tipo": self.tipo, "poi_id": self.poi_id}


@dataclass
class Contexto:
    origen: tuple[float, float] | None
    inicio_min: int
    limite_min: int
    restricciones: Restricciones
    config: Config
    estancias: dict[str, int]
    ventanas: dict[str, list[tuple[int, int]] | None]
    banios: list[POICandidato] = field(default_factory=list)
    con_banio: frozenset[str] = frozenset()
    inteligente: bool = True

    @property
    def descanso_cada(self) -> int | None:
        if not self.inteligente:
            return None
        return self.restricciones.descansos_cada_min

    @property
    def requiere_banio(self) -> bool:
        return self.inteligente and self.restricciones.banio_accesible


@dataclass
class _Estado:
    t: int = 0
    pos: tuple[float, float] | None = None
    desde_descanso: int = 0
    desde_banio: int = 0
    max_hueco_banio: int = 0
    traslado_acum: int = 0
    distancia_m: float = 0.0
    eventos: list[Evento] = field(default_factory=list)
    paradas: list[Parada] = field(default_factory=list)


@dataclass
class Plan:
    secuencia: list[POICandidato]
    paradas: list[Parada]
    eventos: list[Evento]
    total_min: int
    distancia_m: float


class _Simulador:
    def __init__(self, ctx: Contexto):
        self.ctx = ctx

    # --- actividades básicas -------------------------------------------------
    def _avanzar(self, e: _Estado, dur: int, tipo: str, poi_id: str | None) -> None:
        if dur <= 0:
            return
        e.eventos.append(Evento(e.t, e.t + dur, tipo, poi_id))
        e.t += dur
        e.desde_banio += dur
        e.max_hueco_banio = max(e.max_hueco_banio, e.desde_banio)
        if tipo == "descanso":
            e.desde_descanso = 0
        else:
            e.desde_descanso += dur
        if tipo == "traslado":
            e.traslado_acum += dur

    def _descanso_parada(self, e: _Estado) -> None:
        dur = self.ctx.config.duracion_descanso_min
        llegada = e.t
        traslado = e.traslado_acum
        self._avanzar(e, dur, "descanso", None)
        e.paradas.append(
            Parada(
                orden=0,
                poi_id="descanso",
                nombre="Descanso",
                llegada_min=llegada,
                estancia_min=dur,
                traslado_min=traslado,
                motivo=(
                    f"Descanso de {dur} min: pediste descansar cada "
                    f"{self.ctx.restricciones.descansos_cada_min} min. "
                    "Busca una banca o un lugar con sombra."
                ),
            )
        )
        e.traslado_acum = 0

    def _actividad(self, e: _Estado, dur: int, tipo: str, poi_id: str | None) -> int:
        """Agrega una actividad partiéndola con descansos si hace falta.

        Devuelve cuántas pausas internas se insertaron (solo en visitas)."""
        limite = self.ctx.descanso_cada
        pausas = 0
        if not limite:
            self._avanzar(e, dur, tipo, poi_id)
            return 0
        restante = dur
        while restante > 0:
            hueco = limite - e.desde_descanso
            if hueco <= 0:
                if tipo in ("visita", "banio"):
                    self._avanzar(e, self.ctx.config.duracion_descanso_min, "descanso", poi_id)
                    pausas += 1
                else:
                    self._descanso_parada(e)
                continue
            tramo = min(restante, hueco)
            self._avanzar(e, tramo, tipo, poi_id)
            restante -= tramo
        return pausas

    # --- tramos ----------------------------------------------------------------
    def _caminar(self, e: _Estado, destino: tuple[float, float]) -> None:
        if e.pos is None:
            e.pos = destino
            return
        minutos = minutos_caminando(e.pos, destino, self.ctx.config)
        e.distancia_m += distancia_caminable_m(e.pos, destino, self.ctx.config)
        self._actividad(e, minutos, "traslado", None)
        e.pos = destino

    def _visitar(
        self, e: _Estado, poi: POICandidato, estancia: int, tipo: str, motivo: str
    ) -> bool:
        self._caminar(e, (poi.lat, poi.lon))
        traslado = e.traslado_acum
        llegada = e.t
        # Ventana de horario verificable.
        ventanas = self.ctx.ventanas.get(poi.poi_id)
        advertencias: list[str] = []
        elegida: tuple[int, int] | None = None
        if ventanas is not None:
            reloj = self.ctx.inicio_min + e.t
            for ini, fin in ventanas:
                if max(reloj, ini) + estancia <= fin:
                    elegida = (ini, fin)
                    break
            if elegida is None:
                return False
            espera = max(0, elegida[0] - reloj)
            if espera:
                if espera >= self.ctx.config.duracion_descanso_min:
                    self._avanzar(e, espera, "descanso", poi.poi_id)
                else:
                    self._actividad(e, espera, "espera", poi.poi_id)
                advertencias.append(f"Espera {espera} min a que abra")
        if poi.poi_id in self.ctx.con_banio:
            e.desde_banio = 0  # el baño se puede usar en cuanto abre el lugar
        pausas = self._actividad(e, estancia, tipo, poi.poi_id)
        if elegida is not None and self.ctx.inicio_min + e.t > elegida[1]:
            return False
        if pausas:
            advertencias.append(
                f"Incluye {pausas} pausa(s) de {self.ctx.config.duracion_descanso_min} min "
                "dentro de la visita"
            )
        if poi.poi_id in self.ctx.con_banio:
            e.desde_banio = 0
        e.paradas.append(
            Parada(
                orden=0,
                poi_id=poi.poi_id,
                nombre=poi.nombre,
                llegada_min=llegada,
                estancia_min=e.t - llegada,
                traslado_min=traslado,
                motivo=motivo,
                advertencias=advertencias,
            )
        )
        e.traslado_acum = 0
        return e.t <= self.ctx.limite_min

    def _tramo(self, e: _Estado, poi: POICandidato) -> bool:
        ok = self._visitar(e, poi, self.ctx.estancias[poi.poi_id], "visita", "")
        if not ok:
            return False
        if self.ctx.requiere_banio and e.max_hueco_banio > self.ctx.config.intervalo_banio_min:
            return False
        return True

    def _tramo_con_banio(self, e: _Estado, poi: POICandidato) -> _Estado | None:
        if not self.ctx.requiere_banio:
            return e if self._tramo(e, poi) else None
        prueba = copy.deepcopy(e)
        if self._tramo(prueba, poi):
            return prueba
        if not self.ctx.banios:
            return None
        desde = e.pos or (poi.lat, poi.lon)
        destino = (poi.lat, poi.lon)
        opciones = sorted(
            self.ctx.banios,
            key=lambda b: (
                haversine_m(desde, (b.lat, b.lon)) + haversine_m((b.lat, b.lon), destino),
                b.poi_id,
            ),
        )[:5]
        for b in opciones:
            prueba = copy.deepcopy(e)
            motivo = (
                "Baño accesible verificado en el camino: pediste baño accesible "
                f"al menos cada {self.ctx.config.intervalo_banio_min} min."
            )
            if not self._visitar(prueba, b, self.ctx.config.estancia_banio_min, "banio", motivo):
                continue
            if prueba.max_hueco_banio > self.ctx.config.intervalo_banio_min:
                continue
            if self._tramo(prueba, poi):
                return prueba
        return None

    def simular(self, secuencia: list[POICandidato]) -> Plan | None:
        e = _Estado(pos=self.ctx.origen)
        for poi in secuencia:
            siguiente = self._tramo_con_banio(e, poi)
            if siguiente is None:
                return None
            e = siguiente
        for i, p in enumerate(e.paradas, start=1):
            p.orden = i
        return Plan(
            secuencia=list(secuencia),
            paradas=e.paradas,
            eventos=e.eventos,
            total_min=e.t,
            distancia_m=e.distancia_m,
        )


def simular(secuencia: list[POICandidato], ctx: Contexto) -> Plan | None:
    return _Simulador(ctx).simular(secuencia)


def _dos_opt(plan: Plan, ctx: Contexto) -> Plan:
    mejor = plan
    mejoro = True
    while mejoro:
        mejoro = False
        seq = mejor.secuencia
        for i in range(len(seq) - 1):
            for j in range(i + 1, len(seq)):
                nueva = seq[:i] + list(reversed(seq[i : j + 1])) + seq[j + 1 :]
                candidato = simular(nueva, ctx)
                if candidato is None:
                    continue
                if (candidato.total_min, candidato.distancia_m) < (
                    mejor.total_min,
                    mejor.distancia_m - 1e-6,
                ):
                    mejor = candidato
                    mejoro = True
                    break
            if mejoro:
                break
    return mejor


def construir_ruta(
    candidatos: list[POICandidato],
    utilidad: Callable[[POICandidato, list[POICandidato]], float | None],
    ctx: Contexto,
    usar_2opt: bool = True,
) -> tuple[Plan, list[POICandidato]]:
    """Inserción voraz por ``utilidad / (Δt + 1)^exp`` con 2-opt tras cada paso.

    Devuelve el plan y los candidatos que no cupieron en ninguna posición.
    """
    exp = ctx.config.pesos.exponente_tiempo
    plan = simular([], ctx)
    assert plan is not None
    restantes = list(candidatos)
    descartados: list[POICandidato] = []
    while restantes:
        mejor: tuple[float, int, str] | None = None
        mejor_plan: Plan | None = None
        mejor_poi: POICandidato | None = None
        sin_lugar: list[POICandidato] = []
        for c in restantes:
            u_bruta = utilidad(c, plan.secuencia)
            if u_bruta is None:  # no admisible por ahora (p. ej., tope por categoría)
                continue
            u = max(u_bruta, 0.01)
            factible = False
            for pos in range(len(plan.secuencia) + 1):
                nueva = plan.secuencia[:pos] + [c] + plan.secuencia[pos:]
                p = simular(nueva, ctx)
                if p is None:
                    continue
                factible = True
                dt = max(p.total_min - plan.total_min, 0)
                valor = u / (dt + 1) ** exp
                clave = (valor, -dt, c.poi_id)
                if (
                    mejor is None
                    or clave[:2] > mejor[:2]
                    or (clave[:2] == mejor[:2] and c.poi_id < mejor[2])
                ):
                    mejor, mejor_plan, mejor_poi = clave, p, c
            if not factible:
                sin_lugar.append(c)
        for c in sin_lugar:
            restantes.remove(c)
            descartados.append(c)
        if mejor_plan is None or mejor_poi is None:
            break
        restantes.remove(mejor_poi)
        plan = _dos_opt(mejor_plan, ctx) if usar_2opt else mejor_plan
    return plan, descartados


def utilidad_con_diversidad(
    base: dict[str, float], ctx: Contexto
) -> Callable[[POICandidato, list[POICandidato]], float | None]:
    """Penaliza repetir zona o categoría ya presentes en la ruta (estilo MMR) y
    aplica el tope por categoría (por ejemplo, una sola comida por ruta)."""
    w = ctx.config.pesos
    topes = ctx.config.max_por_categoria

    def _u(c: POICandidato, ruta: list[POICandidato]) -> float | None:
        z = zona(c.lat, c.lon, ctx.config)
        misma_zona = sum(1 for r in ruta if zona(r.lat, r.lon, ctx.config) == z)
        misma_cat = sum(1 for r in ruta if r.categoria == c.categoria)
        if c.categoria in topes and misma_cat >= topes[c.categoria]:
            return None
        return base[c.poi_id] - w.repetir_zona * misma_zona - w.repetir_categoria * misma_cat

    return _u
