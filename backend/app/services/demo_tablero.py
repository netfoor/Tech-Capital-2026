"""Semilla de demostración del tablero (spec 019).

Crea la cuenta de analista (DEMO_ANALISTA_CORREO y DEMO_ANALISTA_CONTRASENA del entorno) y un
conjunto SINTÉTICO de personas, visitas, reseñas y reportes, todos con `is_synthetic = true`,
sobre los lugares del catálogo. Lo real nunca se toca. Idempotente: borra el conjunto anterior.

Uso:
    uv run python -m app.services.demo_tablero
"""

import random
import sys
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.config import ajustes
from app.models import (
    CommunityReport,
    ConfirmedVisit,
    ModerationCase,
    PointOfInterest,
    Review,
    ReviewDimension,
    TripSession,
    User,
    VisitCandidate,
)
from app.models.private import DIMENSIONES
from app.services.moderacion import ATRIBUTO_POR_TIPO
from app.services.seguridad import hash_contrasena

DOMINIO = "@demo-sintetico.invalid"
SEMILLA = 2026
# Personas por destino: dos con n ≥ 10, uno que cae en supresión complementaria y uno con n < k.
PERSONAS_POR_DESTINO = (15, 13, 11, 4)
TIPOS = ("escalones", "rampa_bloqueada", "sin_banio_accesible", "superficie", "senalizacion")


class ErrorDemo(Exception):
    pass


def asegurar_analista(s: Session) -> User:
    correo = ajustes().demo_analista_correo.strip().lower()
    contrasena = ajustes().demo_analista_contrasena
    if not correo or len(contrasena) < 8:
        raise ErrorDemo(
            "Define DEMO_ANALISTA_CORREO y DEMO_ANALISTA_CONTRASENA (8 caracteres o más) en .env"
        )
    usuario = s.scalar(select(User).where(User.correo == correo))
    if usuario is None:
        usuario = User(correo=correo, hash_contrasena="", rol="analista")
        s.add(usuario)
    usuario.hash_contrasena = hash_contrasena(contrasena)
    usuario.rol = "analista"
    usuario.nombre_visible = "Analista de demostración"
    return usuario


def borrar_conjunto(s: Session) -> None:
    s.execute(delete(ModerationCase).where(ModerationCase.is_synthetic.is_(True)))
    # ON DELETE CASCADE borra sesiones, visitas, reseñas y reportes de estas personas.
    s.execute(delete(User).where(User.correo.like(f"%{DOMINIO}")))


def _destinos(s: Session) -> list[tuple[str, list[str]]]:
    filas = s.execute(
        select(PointOfInterest.destino_id, func.array_agg(PointOfInterest.poi_id))
        .group_by(PointOfInterest.destino_id)
        .order_by(func.count().desc(), PointOfInterest.destino_id)
        .limit(len(PERSONAS_POR_DESTINO))
    ).all()
    return [(d, sorted(pois)) for d, pois in filas]


def crear_conjunto(s: Session) -> dict[str, int]:
    destinos = _destinos(s)
    if not destinos:
        raise ErrorDemo("No hay lugares en el catálogo: corre primero app.services.semilla")
    azar = random.Random(SEMILLA)
    base = datetime(2026, 9, 1, 10, tzinfo=UTC)
    cuenta = {"personas": 0, "visitas": 0, "resenas": 0, "reportes": 0}
    hash_demo = hash_contrasena(f"sin-acceso-{azar.random()}")
    numero = 0
    for (_destino, pois), personas in zip(destinos, PERSONAS_POR_DESTINO, strict=False):
        # Rasgo del destino para que la demo muestre diferencias (no es un dato real).
        estancia = azar.uniform(25, 90)
        senal = azar.choice((2, 3, 4))
        for _ in range(personas):
            numero += 1
            persona = User(
                correo=f"persona-{numero:03d}{DOMINIO}",
                hash_contrasena=hash_demo,
                rol="visitante",
                is_synthetic=True,
            )
            s.add(persona)
            s.flush()
            cuenta["personas"] += 1
            viaje = TripSession(
                user_id=persona.id,
                version_consentimiento="2026-10",
                estado="detenida",
                inicio=base,
                is_synthetic=True,
            )
            s.add(viaje)
            s.flush()
            for poi_id in azar.sample(pois, k=min(len(pois), azar.randint(1, 3))):
                inicio = base + timedelta(days=azar.randint(0, 44), hours=azar.randint(0, 8))
                minutos = max(5.0, azar.gauss(estancia, estancia / 3))
                candidato = VisitCandidate(
                    session_id=viaje.id,
                    poi_id=poi_id,
                    inicio=inicio,
                    fin=inicio + timedelta(minutes=minutos),
                    duracion_min=round(minutos, 1),
                    estado="visita_probable",
                    fuente_evidencia="gps",
                    precision_m=round(azar.uniform(5, 30), 1),
                    confianza=round(azar.uniform(0.6, 0.95), 2),
                    confirmada=True,
                    is_synthetic=True,
                )
                s.add(candidato)
                s.flush()
                s.add(
                    ConfirmedVisit(
                        user_id=persona.id,
                        poi_id=poi_id,
                        candidate_id=candidato.id,
                        fecha=inicio,
                        fuente_evidencia="gps_confirmado",
                        precision_m=candidato.precision_m,
                        confianza=candidato.confianza,
                        confirmada=True,
                        is_synthetic=True,
                    )
                )
                cuenta["visitas"] += 1
                resena = Review(
                    user_id=persona.id, poi_id=poi_id, creado_en=inicio, is_synthetic=True
                )
                s.add(resena)
                s.flush()
                for dimension in DIMENSIONES:
                    centro = senal if dimension == "senalizacion" else 4
                    puntaje = min(5, max(1, round(azar.gauss(centro, 0.9))))
                    s.add(
                        ReviewDimension(review_id=resena.id, dimension=dimension, puntaje=puntaje)
                    )
                cuenta["resenas"] += 1
            # Una de cada tres personas reporta una barrera.
            if numero % 3 == 0:
                tipo = azar.choice(TIPOS)
                poi_id = azar.choice(pois)
                creado = base + timedelta(days=azar.randint(0, 40), hours=azar.randint(0, 12))
                reporte = CommunityReport(
                    user_id=persona.id,
                    poi_id=poi_id,
                    tipo=tipo,
                    descripcion="Reporte sintético de demostración",
                    creado_en=creado,
                    is_synthetic=True,
                )
                s.add(reporte)
                s.flush()
                abierto = cuenta["reportes"] % 3 == 0
                decision = None if abierto else azar.choice(("aceptar", "aceptar", "rechazar"))
                estado = (
                    "abierto" if abierto else ("aceptado" if decision == "aceptar" else "rechazado")
                )
                reporte.estado = {"abierto": "en_moderacion"}.get(estado, estado)
                s.add(
                    ModerationCase(
                        community_report_id=reporte.id,
                        poi_id=poi_id,
                        tipo=tipo,
                        atributo=ATRIBUTO_POR_TIPO.get(tipo, (None,))[0],
                        estado=estado,
                        decision=decision,
                        nota="Decisión sintética de demostración" if decision else None,
                        decidido_en=(
                            None if abierto else creado + timedelta(hours=azar.uniform(2, 96))
                        ),
                        creado_en=creado,
                        is_synthetic=True,
                    )
                )
                cuenta["reportes"] += 1
    return cuenta


def main() -> int:
    from app.db import SesionLocal

    try:
        with SesionLocal() as s:
            analista = asegurar_analista(s)
            borrar_conjunto(s)
            cuenta = crear_conjunto(s)
            s.commit()
    except ErrorDemo as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"Analista de demostración: {analista.correo}")
    print("DATOS SINTÉTICOS DE DEMOSTRACIÓN creados:")
    for clave, valor in cuenta.items():
        print(f"  {clave}: {valor}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
