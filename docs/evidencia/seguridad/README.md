# Prueba de seguridad del sitio (T010-05)

Fecha: 17 de octubre de 2026, desde una red externa al proyecto.

| Prueba | Resultado |
|---|---|
| `GET https://<bucket>.s3.amazonaws.com/index.html` | 403 `AccessDenied`: el bucket solo se lee a través de CloudFront |
| `GET https://<bucket>.s3.amazonaws.com/` (listado) | 403 `AccessDenied` |
| `HEAD https://techcapital.foor.dev/` | 200 con `Strict-Transport-Security: max-age=31536000; includeSubDomains` |
| Cabeceras de seguridad | `Content-Security-Policy` (`default-src 'self'`, sin estilos ni scripts en línea), `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(), geolocation=()` |

Pendiente: el inicio de sesión con Cognito (T010-09) no está aplicado; la plataforma se publica en modo local por decisión del 17 de octubre (ADR-0009).

La CSP prohíbe estilos en línea; el revisor del sitio (`web/scripts/revisar.mjs`) sirve las páginas con la misma política para detectar ese error antes de publicar.
