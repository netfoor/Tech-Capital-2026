"""Configuración leída del entorno. Las llaves nunca se escriben en el código."""

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ_REPO = Path(__file__).resolve().parents[2]


class Ajustes(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://pueblaviva:pueblaviva@localhost:5433/pueblaviva"
    # En funciones sin servidor cada instancia abre y cierra su conexión; el pooler de la
    # base (por ejemplo, el de Neon) reparte las conexiones.
    db_sin_pool: bool = False
    k_minimo: int = 10
    origenes_permitidos: list[str] = ["http://localhost:5173"]

    # Sin JWT_SECRETO se usa un secreto aleatorio por proceso (los tokens no sobreviven
    # a un reinicio). En cualquier despliegue se fija en el entorno.
    jwt_secreto: str = ""
    jwt_minutos: int = 60 * 24

    directorio_datos: Path = RAIZ_REPO / "data"
    # Fotos de reportes, sin EXIF. Vive bajo data/privado/, que no se versiona.
    directorio_media: Path = RAIZ_REPO / "data" / "privado" / "media"
    foto_max_bytes: int = 5 * 1024 * 1024

    @field_validator("database_url")
    @classmethod
    def _usar_psycopg(cls, url: str) -> str:
        # Los proveedores entregan postgres:// o postgresql://; SQLAlchemy necesita el driver.
        for prefijo in ("postgres://", "postgresql://"):
            if url.startswith(prefijo):
                return "postgresql+psycopg://" + url.removeprefix(prefijo)
        return url


@lru_cache
def ajustes() -> Ajustes:
    return Ajustes()
