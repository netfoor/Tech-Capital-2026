"""Configuración leída del entorno. Las llaves nunca se escriben en el código."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Ajustes(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://pueblaviva:pueblaviva@localhost:5433/pueblaviva"
    k_minimo: int = 10
    origenes_permitidos: list[str] = ["http://localhost:5173"]


@lru_cache
def ajustes() -> Ajustes:
    return Ajustes()
