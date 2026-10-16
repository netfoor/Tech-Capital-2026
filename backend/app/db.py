"""Conexión a PostgreSQL + PostGIS."""

from collections.abc import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import ajustes

motor = create_engine(ajustes().database_url, pool_pre_ping=True)
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
