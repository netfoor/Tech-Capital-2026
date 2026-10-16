"""Configuración leída del entorno. Las llaves nunca se escriben en el código."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ_REPO = Path(__file__).resolve().parents[2]


class Ajustes(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://pueblaviva:pueblaviva@localhost:5433/pueblaviva"
    k_minimo: int = 10
    origenes_permitidos: list[str] = ["http://localhost:5173"]

    # Sin JWT_SECRETO se usa un secreto aleatorio por proceso (los tokens no sobreviven
    # a un reinicio). En cualquier despliegue se fija en el entorno.
    jwt_secreto: str = ""
    jwt_minutos: int = 60 * 24

    directorio_datos: Path = RAIZ_REPO / "data"
    # Cuenta de analista para la demostración del tablero (spec 019). Sin valores en el repo.
    demo_analista_correo: str = ""
    demo_analista_contrasena: str = ""
    # Fichas semánticas de los indicadores del tablero (spec 019).
    archivo_metricas: Path = RAIZ_REPO / "metrics" / "definitions.yaml"
    # Fotos de reportes, sin EXIF. Vive bajo data/privado/, que no se versiona.
    directorio_media: Path = RAIZ_REPO / "data" / "privado" / "media"
    foto_max_bytes: int = 5 * 1024 * 1024


@lru_cache
def ajustes() -> Ajustes:
    return Ajustes()
