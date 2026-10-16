import jwt

from app.models import User


def test_registro_crea_visitante_y_devuelve_token(cliente, sesion):
    r = cliente.post(
        "/auth/registro",
        json={"correo": "Ana@Ejemplo.MX", "contrasena": "una-clave-larga", "nombre_visible": "Ana"},
    )
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["token_type"] == "bearer"
    assert cuerpo["usuario"]["rol"] == "visitante"
    assert cuerpo["usuario"]["correo"] == "ana@ejemplo.mx"
    usuario = sesion.query(User).one()
    assert usuario.hash_contrasena.startswith("$argon2")
    assert "una-clave-larga" not in usuario.hash_contrasena
    me = cliente.get("/me", headers={"Authorization": f"Bearer {cuerpo['access_token']}"})
    assert me.status_code == 200 and me.json()["nombre_visible"] == "Ana"


def test_registro_no_permite_elegir_rol(cliente):
    r = cliente.post(
        "/auth/registro",
        json={"correo": "x@ejemplo.mx", "contrasena": "una-clave-larga", "rol": "admin"},
    )
    assert r.status_code == 201
    assert r.json()["usuario"]["rol"] == "visitante"


def test_registro_duplicado_y_validaciones(cliente):
    datos = {"correo": "dup@ejemplo.mx", "contrasena": "una-clave-larga"}
    assert cliente.post("/auth/registro", json=datos).status_code == 201
    assert cliente.post("/auth/registro", json=datos).status_code == 409
    corta = {"correo": "c@ejemplo.mx", "contrasena": "corta"}
    assert cliente.post("/auth/registro", json=corta).status_code == 422
    sin_correo = {"correo": "no-es-correo", "contrasena": "una-clave-larga"}
    assert cliente.post("/auth/registro", json=sin_correo).status_code == 422


def test_login(cliente):
    datos = {"correo": "l@ejemplo.mx", "contrasena": "una-clave-larga"}
    cliente.post("/auth/registro", json=datos)
    r = cliente.post("/auth/login", json={**datos, "correo": "L@ejemplo.mx"})
    assert r.status_code == 200
    carga = jwt.decode(r.json()["access_token"], options={"verify_signature": False})
    assert carga["rol"] == "visitante" and "exp" in carga
    mala = cliente.post("/auth/login", json={**datos, "contrasena": "otra-clave-larga"})
    assert mala.status_code == 401
    nadie = cliente.post("/auth/login", json={"correo": "n@ejemplo.mx", "contrasena": "x" * 9})
    assert nadie.status_code == 401


def test_token_invalido_o_ausente(cliente):
    assert cliente.get("/me").status_code == 401
    assert cliente.get("/me", headers={"Authorization": "Bearer basura"}).status_code == 401
    falso = jwt.encode({"sub": "00000000-0000-0000-0000-000000000000"}, "otro", algorithm="HS256")
    assert cliente.get("/me", headers={"Authorization": f"Bearer {falso}"}).status_code == 401
