# ADR-0009 · Página pública y plataforma con acceso por Cognito

**Estado:** aceptada · 2026-10-15

## Contexto

El primer andamiaje del sitio era una sola página larga que explica el proyecto sección por sección. Ese formato sirve para contar el problema, pero no se ve como una herramienta que la Secretaría usaría cada mes ni en sus citas del Tianguis. La convocatoria pide un prototipo funcional (§8) y evalúa viabilidad y utilidad (§11).

## Decisión

El sitio tiene dos superficies:

1. **Página pública** (`/`): presenta el problema, qué hace la plataforma, su uso rumbo al Tianguis, el método y las descargas. Es la entrada para el jurado y para quien no tiene cuenta.
2. **Plataforma** (`/plataforma/`): la herramienta, con navegación de aplicación y cuatro vistas (Radar, Fichas, Asistentes y Redes). Pide iniciar sesión.

El acceso se hace con **Amazon Cognito y su Hosted UI** (inicio de sesión alojado por Cognito, versión clásica):
- grupo de usuarios creado con Terraform; las cuentas las da de alta el equipo (no hay registro abierto);
- cliente público con flujo de código de autorización y PKCE, sin secreto, porque el sitio es estático;
- el sitio guarda el token en `sessionStorage` y lo descarta al cerrar sesión o al vencer.

## Consecuencias

- El jurado ve un producto con cuentas de usuario, como lo usaría la Secretaría, y la página pública sigue contando la historia.
- La protección es de experiencia, no de datos: los JSON del sitio y `data/curado/` son públicos por diseño (constitución III, datos verificables). Si el piloto necesita datos restringidos, se valida el token en CloudFront (Lambda@Edge o cookies firmadas) y los datos privados se sirven desde otro prefijo.
- La política de contenido de CloudFront agrega el dominio de Cognito en `connect-src`.
- Sin configuración de Cognito (`web/.env` vacío), la plataforma corre en **modo local** con un aviso visible. Así el equipo puede desarrollar antes de aplicar la infraestructura. `infra/desplegar.sh` se niega a publicar una compilación en modo local.
