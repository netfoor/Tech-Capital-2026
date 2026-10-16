"""Registro e inicio de sesión con JWT. El registro siempre crea el rol «visitante»."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import Sesion
from app.models import User
from app.schemas.cuenta import (
    RespuestaToken,
    SolicitudLogin,
    SolicitudRegistro,
    UsuarioPublico,
)
from app.services.auditoria import registrar
from app.services.seguridad import (
    Usuario,
    emitir_token,
    hash_contrasena,
    verificar_contrasena,
)

router = APIRouter(tags=["cuenta"])


def _respuesta(usuario: User) -> RespuestaToken:
    return RespuestaToken(
        access_token=emitir_token(usuario), usuario=UsuarioPublico.model_validate(usuario)
    )


@router.post("/auth/registro", response_model=RespuestaToken, status_code=status.HTTP_201_CREATED)
def registro(cuerpo: SolicitudRegistro, s: Sesion) -> RespuestaToken:
    correo = cuerpo.correo.lower()
    if s.scalar(select(User.id).where(User.correo == correo)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe una cuenta con ese correo")
    usuario = User(
        correo=correo,
        hash_contrasena=hash_contrasena(cuerpo.contrasena),
        rol="visitante",
        nombre_visible=cuerpo.nombre_visible,
    )
    s.add(usuario)
    s.flush()
    registrar(s, usuario.id, "registro", "user_account", usuario.id)
    s.commit()
    return _respuesta(usuario)


@router.post("/auth/login", response_model=RespuestaToken)
def login(cuerpo: SolicitudLogin, s: Sesion) -> RespuestaToken:
    usuario = s.scalar(select(User).where(User.correo == cuerpo.correo.lower()))
    if usuario is None or not verificar_contrasena(usuario.hash_contrasena, cuerpo.contrasena):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _respuesta(usuario)


@router.get("/me", response_model=UsuarioPublico)
def yo(usuario: Usuario) -> UsuarioPublico:
    return UsuarioPublico.model_validate(usuario)
