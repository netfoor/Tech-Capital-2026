"""Contraseñas (argon2), JWT (HS256) y dependencias de rol para FastAPI."""

import secrets
import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Annotated

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import ajustes
from app.db import sesion
from app.models import User

ALGORITMO = "HS256"
_hasher = PasswordHasher()
_portador = HTTPBearer(auto_error=False)


def hash_contrasena(contrasena: str) -> str:
    return _hasher.hash(contrasena)


def verificar_contrasena(hash_guardado: str, contrasena: str) -> bool:
    try:
        return _hasher.verify(hash_guardado, contrasena)
    except (VerificationError, InvalidHashError):
        return False


@lru_cache
def _secreto() -> str:
    return ajustes().jwt_secreto or secrets.token_urlsafe(48)


def emitir_token(usuario: User) -> str:
    ahora = datetime.now(UTC)
    carga = {
        "sub": str(usuario.id),
        "rol": usuario.rol,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=ajustes().jwt_minutos),
    }
    return jwt.encode(carga, _secreto(), algorithm=ALGORITMO)


def _no_autorizado(detalle: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detalle,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _usuario_de_token(token: str, s: Session) -> User:
    try:
        carga = jwt.decode(token, _secreto(), algorithms=[ALGORITMO])
        usuario_id = uuid.UUID(carga["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as error:
        raise _no_autorizado("Token inválido o vencido") from error
    usuario = s.get(User, usuario_id)
    if usuario is None:
        raise _no_autorizado("La cuenta ya no existe")
    return usuario


def usuario_opcional(
    credenciales: Annotated[HTTPAuthorizationCredentials | None, Depends(_portador)],
    s: Annotated[Session, Depends(sesion)],
) -> User | None:
    if credenciales is None:
        return None
    return _usuario_de_token(credenciales.credentials, s)


def usuario_actual(
    credenciales: Annotated[HTTPAuthorizationCredentials | None, Depends(_portador)],
    s: Annotated[Session, Depends(sesion)],
) -> User:
    if credenciales is None:
        raise _no_autorizado("Hace falta iniciar sesión")
    return _usuario_de_token(credenciales.credentials, s)


def requiere_rol(*roles: str) -> Callable[[User], User]:
    def dependencia(usuario: Annotated[User, Depends(usuario_actual)]) -> User:
        if usuario.rol not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Tu rol no permite esta acción")
        return usuario

    return dependencia


Usuario = Annotated[User, Depends(usuario_actual)]
UsuarioOpcional = Annotated[User | None, Depends(usuario_opcional)]
Moderador = Annotated[User, Depends(requiere_rol("analista", "admin"))]
