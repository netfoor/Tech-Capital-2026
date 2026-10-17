# Tareas 010 · Infraestructura

- [x] T010-01 Andamiaje de Terraform (`versions`, `providers`, `variables`, `sitio`, `certificado`, `outputs`) y `desplegar.sh`. Verificación: `terraform fmt -check` y `terraform validate`.
- [x] T010-02 `terraform init` y `apply` del certificado con el perfil `Fortino-IAM-Admin`. Verificación: salida con el CNAME de validación.
- [x] T010-03 Registro de validación en Cloudflare y certificado emitido. Verificación: `aws acm describe-certificate` con `Status: ISSUED`.
- [x] T010-04 `terraform apply` completo y CNAME del subdominio en Cloudflare. Verificación: `curl -I https://techcapital.foor.dev` responde 200 con HSTS después del primer despliegue.
- [x] T010-08 Cognito en Terraform (`cognito.tf`): grupo de usuarios, dominio con Hosted UI y cliente con PKCE; CSP con el dominio de Cognito y `make web-config`. Verificación: `terraform validate`.
- [ ] T010-09 Aplicar Cognito y dar de alta las cuentas del equipo (y la de demostración el día de la presentación). Depende de T010-04. Diferida el 2026-10-17: las demos se hacen sin inicio de sesión (ADR-0009, actualización). Verificación: inicio de sesión real en `https://techcapital.foor.dev/plataforma/`.
- [x] T010-05 Prueba de seguridad: acceso directo a un objeto de S3 rechazado y cabeceras presentes. Verificación: `curl` a la URL de S3 da 403. Hecha el 2026-10-17: S3 responde `AccessDenied` y CloudFront envía HSTS, CSP, `nosniff`, `X-Frame-Options`, `Referrer-Policy` y `Permissions-Policy` (`docs/evidencia/seguridad/`).
- [ ] T010-10 Retirar la excepción `PERMITIR_SIN_ACCESO` de `infra/desplegar.sh` cuando T010-09 esté aplicada. Depende de T010-09. Verificación: `make desplegar` rechaza una compilación en modo local.
- [ ] T010-06 [P] Estimación de costos mensuales (sitio, más APIs por corrida desde T006-12) en `modelo-de-operacion.md`. Verificación: tabla de costos con fuente y fecha.
- [ ] T010-07 [P] (P2) Bucket de datos, Lambda, Scheduler y SSM según el plan. Verificación: ejecución manual de la Lambda con un tope de 5 corridas.
