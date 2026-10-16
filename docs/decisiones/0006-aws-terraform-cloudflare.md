# ADR-0006 · AWS con Terraform y DNS en Cloudflare

**Estado:** aceptada · 2026-10-15

## Contexto

El equipo trabaja con AWS y Terraform. La zona `foor.dev` está en Cloudflare, y un sitio previo del equipo (`agrocebada.foor.dev`) usa S3 con CloudFront detrás de un CNAME.

## Decisión

- La infraestructura de `infra/` se define con Terraform: bucket S3 privado, CloudFront con OAC y política de cabeceras de seguridad, y certificado ACM en `us-east-1`.
- Se aplica con el perfil `Fortino-IAM-Admin`.
- El subdominio por defecto es `techcapital.foor.dev`, configurable con una variable.
- Los registros DNS (validación del certificado y CNAME) se crean en Cloudflare a mano, a partir de las salidas de Terraform. Opcionalmente se gestionan con el proveedor de Cloudflare si hay un token.

## Consecuencias

- Se reutiliza un patrón probado y el costo de operación es mínimo.
- La creación del certificado espera a que exista el registro de validación en Cloudflare: es un paso manual que aparece en `infra/README.md`.
