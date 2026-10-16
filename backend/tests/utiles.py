"""Utilidades compartidas por las pruebas."""

from pathlib import Path

from app.models import User
from app.services.seguridad import emitir_token, hash_contrasena

DATOS_PRUEBA = Path(__file__).parent / "datos"


def crear_usuario(sesion, correo: str, rol: str = "visitante") -> tuple[User, dict[str, str]]:
    usuario = User(correo=correo, hash_contrasena=hash_contrasena("contrasena-segura"), rol=rol)
    sesion.add(usuario)
    sesion.commit()
    return usuario, {"Authorization": f"Bearer {emitir_token(usuario)}"}
