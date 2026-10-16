from logging.config import fileConfig

from alembic import context
from geoalchemy2 import alembic_helpers
from sqlalchemy import engine_from_config, pool

import app.models  # noqa: F401  registra los modelos en Base.metadata
from app.config import ajustes
from app.models.base import Base

config = context.config
# Las pruebas fijan su propia URL (base pueblaviva_test); si no, se usa la del entorno.
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", ajustes().database_url.replace("%", "%%"))
if config.config_file_name is not None and config.attributes.get("configurar_registros", True):
    fileConfig(config.config_file_name, disable_existing_loggers=False)

objetivo = Base.metadata
ESQUEMAS_PROPIOS = {"core", "private", "analytics", "audit"}


def _incluir(objeto, nombre, tipo, reflejado, comparar_con):
    # PostGIS crea tablas propias (spatial_ref_sys, tiger…); no se administran aquí.
    if tipo == "table" and reflejado and comparar_con is None:
        return False
    if tipo == "table" and getattr(objeto, "schema", None) not in ESQUEMAS_PROPIOS:
        return False
    return alembic_helpers.include_object(objeto, nombre, tipo, reflejado, comparar_con)


def _opciones() -> dict:
    return {
        "target_metadata": objetivo,
        "include_schemas": True,
        "include_object": _incluir,
        "process_revision_directives": alembic_helpers.writer,
        "render_item": alembic_helpers.render_item,
    }


def correr_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"), literal_binds=True, **_opciones()
    )
    with context.begin_transaction():
        context.run_migrations()


def correr_online() -> None:
    motor = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with motor.connect() as conexion:
        context.configure(connection=conexion, **_opciones())
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    correr_offline()
else:
    correr_online()
