# Spec 010 · Infraestructura

| | |
|---|---|
| Contexto | Plataforma |
| Prioridad | P0 (hospedaje del sitio) · P2 (recolección programada y carga del panel) |
| Estado | En curso: andamiaje de Terraform en `infra/` |
| Depende de | — |
| Habilita | 009 (despliegue y acceso a la plataforma) |

## Bases que atiende

FIN-01 (versión funcional accesible), ENT-07 (arquitectura), RUB-04 (solidez técnica) y RUB-06 (viabilidad: infraestructura y costos).

## Objetivo

Publicar el sitio con HTTPS en un subdominio de foor.dev, con costo mínimo, sin buckets públicos y con infraestructura reproducible; dar acceso a la plataforma con cuentas de Cognito. Además, dejar diseñada la operación del piloto (recolección mensual).

## Historias de usuario

**H1 (P0).** Como equipo, quiero desplegar el sitio con un comando.
- Dada la infraestructura aplicada, cuando corro `make desplegar`, entonces `web/dist/` se sincroniza con S3, se invalida CloudFront y el sitio responde en `https://techcapital.foor.dev` (o el subdominio de la variable `dominio`).

**H2 (P0).** Como responsable de seguridad, quiero que el contenido no sea accesible fuera de CloudFront y que tenga cabeceras seguras.
- Dado el bucket, cuando intento leer un objeto directo de S3, entonces se rechaza. Las respuestas de CloudFront incluyen HSTS, `X-Content-Type-Options`, `X-Frame-Options` y `Referrer-Policy`.

**H4 (P0).** Como equipo, quiero dar de alta cuentas para la plataforma sin abrir un registro público.
- Dado el grupo de usuarios de Cognito, cuando corro el comando de alta de `infra/README.md` con un correo, entonces la persona recibe una contraseña temporal, entra por la Hosted UI y la cambia en su primer inicio.

**H3 (P2).** Como Secretaría en el piloto, quiero que la medición se repita cada mes sin intervención.
- Dada una regla de EventBridge Scheduler mensual, cuando se dispara, entonces una Lambda ejecuta las etapas de YouTube y asistentes y guarda los resultados en el bucket de datos.

## Requisitos funcionales

- **FR-010-01** Terraform ≥ 1.9, proveedor AWS ~> 6.0, con el perfil `Fortino-IAM-Admin` (variable `perfil_aws`) y región principal `us-east-1` (variable).
- **FR-010-02** Bucket del sitio privado (bloqueo de acceso público, cifrado SSE-S3 y propietario forzado).
- **FR-010-03** CloudFront con OAC, `default_root_object = "index.html"`, HTTP/2 y HTTP/3, compresión, política de caché administrada `CachingOptimized` y política de cabeceras de seguridad propia.
- **FR-010-04** Certificado ACM en `us-east-1` con validación por DNS. Las salidas de Terraform muestran el registro CNAME de validación y el destino de CloudFront para crearlos en Cloudflare (sin proxy).
- **FR-010-05** Script `infra/desplegar.sh`: `aws s3 sync web/dist s3://<bucket> --delete` con `cache-control` largo para `_astro/*`, `no-cache` para HTML y JSON, e invalidación `/*`.
- **FR-010-06** Estado de Terraform local y fuera de git durante el hackathon. Para el piloto, backend S3 con bloqueo nativo (`use_lockfile = true`).
- **FR-010-09** Cognito (ADR-0009): grupo de usuarios con correo como usuario, alta solo por administradores, contraseña de al menos 12 caracteres y recuperación por correo; dominio de prefijo con Hosted UI clásica (`managed_login_version = 1`); cliente público sin secreto, flujo `code` con PKCE, alcances `openid email profile`, regreso a `https://<dominio>/plataforma/` y `http://localhost:4321/plataforma/`, y salida a la raíz de ambos.
- **FR-010-10** La política de contenido de CloudFront permite `connect-src` hacia el dominio de Cognito. `make web-config` escribe `web/.env` con el dominio y el id de cliente a partir de las salidas de Terraform.
- **FR-010-07** (P2) Bucket de datos privado con versionado; Lambda y EventBridge Scheduler para la recolección mensual; secretos en SSM Parameter Store.
- **FR-010-08** Estimación de costos mensuales en `docs/entregables/modelo-de-operacion.md`, con la calculadora de precios de AWS y el uso esperado.

## Requisitos no funcionales

- `terraform fmt -check` y `terraform validate` pasan.
- Ningún recurso es público salvo la distribución de CloudFront y la Hosted UI de Cognito.
- Etiquetas `proyecto = "radar-atencion-turistica"` y `entorno` en todos los recursos.

## Fuera de alcance

- Dominio propio de la Secretaría (sería parte del piloto).
- WAF (opcional en el piloto).

## Preguntas abiertas

- ¿Se gestiona el DNS de Cloudflare con Terraform (proveedor `cloudflare`, token con permiso de DNS en la zona foor.dev) o a mano? Por defecto, a mano.
