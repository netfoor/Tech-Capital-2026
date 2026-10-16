"""Conexión a PostgreSQL + PostGIS."""

from collections.abc import Iterator

from sqlalchemy import create_engine, pool, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import ajustes

_opciones = {"poolclass": pool.NullPool} if ajustes().db_sin_pool else {}
motor = create_engine(ajustes().database_url, pool_pre_ping=True, **_opciones)
SesionLocal = sessionmaker(bind=motor, autoflush=False, expire_on_commit=False)


def sesion() -> Iterator[Session]:
    with SesionLocal() as s:
        yield s


def base_disponible() -> bool:
    try:
        with motor.connect() as conexion:
            conexion.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
