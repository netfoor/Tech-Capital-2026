from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import app.models  # noqa: F401  registra los modelos en Base.metadata
from app.config import ajustes
from app.models.base import Base

config = context.config
config.set_main_option("sqlalchemy.url", ajustes().database_url)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

objetivo = Base.metadata


def _incluir(objeto, nombre, tipo, reflejado, comparar_con):
    # PostGIS crea tablas propias (spatial_ref_sys, tiger…); no se administran aquí.
    return not (tipo == "table" and reflejado and comparar_con is None)


def correr_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=objetivo,
        literal_binds=True,
        include_schemas=True,
        include_object=_incluir,
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
        context.configure(
            connection=conexion,
            target_metadata=objetivo,
            include_schemas=True,
            include_object=_incluir,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    correr_offline()
else:
    correr_online()
