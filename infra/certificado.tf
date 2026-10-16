# Certificado del subdominio con validación por DNS. El registro de validación se crea a mano
# en Cloudflare a partir de la salida `dns_validacion_certificado` (ADR-0006).
resource "aws_acm_certificate" "sitio" {
  provider          = aws.us_east_1
  domain_name       = var.dominio
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate_validation" "sitio" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.sitio.arn
  validation_record_fqdns = [for opcion in aws_acm_certificate.sitio.domain_validation_options : opcion.resource_record_name]

  timeouts {
    create = "45m"
  }
}
