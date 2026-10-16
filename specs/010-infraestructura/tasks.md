# Tareas 010 · Infraestructura

- [x] T010-01 Andamiaje de Terraform (`versions`, `providers`, `variables`, `sitio`, `certificado`, `outputs`) y `desplegar.sh`. Verificación: `terraform fmt -check` y `terraform validate`.
- [ ] T010-02 `terraform init` y `apply` del certificado con el perfil `Fortino-IAM-Admin`. Verificación: salida con el CNAME de validación.
- [ ] T010-03 Registro de validación en Cloudflare y certificado emitido. Verificación: `aws acm describe-certificate` con `Status: ISSUED`.
- [ ] T010-04 `terraform apply` completo y CNAME del subdominio en Cloudflare. Verificación: `curl -I https://techcapital.foor.dev` responde 200 con HSTS después del primer despliegue.
- [ ] T010-05 Prueba de seguridad: acceso directo a un objeto de S3 rechazado y cabeceras presentes. Verificación: `curl` a la URL de S3 da 403.
- [ ] T010-06 [P] Estimación de costos mensuales (sitio, más APIs por corrida desde T006-12) en `modelo-de-operacion.md`. Verificación: tabla de costos con fuente y fecha.
- [ ] T010-07 [P] (P2) Bucket de datos, Lambda, Scheduler y SSM según el plan. Verificación: ejecución manual de la Lambda con un tope de 5 corridas.
