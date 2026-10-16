"""Pruebas contra PostGIS real, en una base aparte (`pueblaviva_test`).

La base se crea si no existe, se migra una vez por sesión y se trunca antes de cada prueba.
"""

import os
from pathlib import Path

from sqlalchemy import make_url

from app.config import Ajustes

URL_BASE = make_url(Ajustes().database_url)
# BASE_PRUEBAS permite que varias ramas corran pruebas a la vez sin pisarse.
URL_PRUEBAS = URL_BASE.set(database=os.environ.get("BASE_PRUEBAS", "pueblaviva_test"))
os.environ["DATABASE_URL"] = URL_PRUEBAS.render_as_string(hide_password=False)
os.environ.setdefault("JWT_SECRETO", "secreto-solo-para-pruebas-" + "x" * 32)
os.environ.setdefault("DIRECTORIO_MEDIA", str(Path(__file__).parent / ".media"))

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402

from app.config import ajustes  # noqa: E402

ajustes.cache_clear()

from app.db import SesionLocal, motor  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402
from app.services import semilla  # noqa: E402
from tests.utiles import DATOS_PRUEBA, crear_usuario  # noqa: E402

RAIZ_BACKEND = Path(__file__).resolve().parents[1]


def _crear_base() -> None:
    admin = create_engine(URL_BASE, isolation_level="AUTOCOMMIT")
    with admin.connect() as conexion:
        existe = conexion.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": URL_PRUEBAS.database}
        )
        if not existe:
            conexion.execute(text(f'CREATE DATABASE "{URL_PRUEBAS.database}"'))
    admin.dispose()


def _migrar() -> None:
    config = Config(str(RAIZ_BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(RAIZ_BACKEND / "alembic"))
    config.set_main_option(
        "sqlalchemy.url", URL_PRUEBAS.render_as_string(hide_password=False).replace("%", "%%")
    )
    config.attributes["configurar_registros"] = False
    command.upgrade(config, "head")


@pytest.fixture(scope="session", autouse=True)
def base_de_pruebas():
    _crear_base()
    _migrar()
    yield
    motor.dispose()


def _truncar() -> None:
    # DELETE en orden de dependencias: con tablas pequeñas es mucho más rápido que TRUNCATE.
    with motor.begin() as conexion:
        for tabla in reversed(Base.metadata.sorted_tables):
            conexion.execute(tabla.delete())


@pytest.fixture(autouse=True)
def limpia(base_de_pruebas):
    _truncar()
    yield


@pytest.fixture
def sesion():
    with SesionLocal() as s:
        yield s


@pytest.fixture
def cliente():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def catalogo(sesion):
    """Destinos reales, fuentes reales y el fixture sintético de POI (sin la serie oficial)."""
    return semilla.cargar(sesion, curado=DATOS_PRUEBA, indicadores=False)


@pytest.fixture
def ana(sesion):
    return crear_usuario(sesion, "ana@ejemplo.mx")


@pytest.fixture
def beto(sesion):
    return crear_usuario(sesion, "beto@ejemplo.mx")


@pytest.fixture
def analista(sesion):
    return crear_usuario(sesion, "analista@ejemplo.mx", "analista")
