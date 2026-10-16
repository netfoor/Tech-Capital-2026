output "url" {
  description = "Dirección pública del sitio"
  value       = "https://${var.dominio}"
}

output "bucket_sitio" {
  description = "Bucket privado con los archivos del sitio"
  value       = aws_s3_bucket.sitio.bucket
}

output "cloudfront_id" {
  description = "Distribución que se invalida en cada despliegue"
  value       = aws_cloudfront_distribution.sitio.id
}

output "cloudfront_dominio" {
  description = "Destino del CNAME del subdominio"
  value       = aws_cloudfront_distribution.sitio.domain_name
}

output "dns_validacion_certificado" {
  description = "Registro que se crea en Cloudflare (solo DNS, sin proxy) para validar el certificado"
  value = [for opcion in aws_acm_certificate.sitio.domain_validation_options : {
    nombre = opcion.resource_record_name
    tipo   = opcion.resource_record_type
    valor  = opcion.resource_record_value
  }]
}

output "dns_sitio" {
  description = "Registro del subdominio que se crea en Cloudflare (solo DNS, sin proxy)"
  value = {
    nombre = var.dominio
    tipo   = "CNAME"
    valor  = aws_cloudfront_distribution.sitio.domain_name
  }
}
