data "aws_caller_identity" "actual" {}

data "aws_cloudfront_cache_policy" "optimizada" {
  name = "Managed-CachingOptimized"
}

# Bucket privado: solo CloudFront lo lee (FR-010-02).
resource "aws_s3_bucket" "sitio" {
  bucket = "${local.nombre}-sitio-${data.aws_caller_identity.actual.account_id}"
}

resource "aws_s3_bucket_public_access_block" "sitio" {
  bucket = aws_s3_bucket.sitio.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "sitio" {
  bucket = aws_s3_bucket.sitio.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "sitio" {
  bucket = aws_s3_bucket.sitio.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

data "aws_iam_policy_document" "sitio" {
  statement {
    sid       = "LecturaDesdeCloudFront"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.sitio.arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.sitio.arn]
    }
  }

  statement {
    sid       = "SoloConTLS"
    effect    = "Deny"
    actions   = ["s3:*"]
    resources = [aws_s3_bucket.sitio.arn, "${aws_s3_bucket.sitio.arn}/*"]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "sitio" {
  bucket = aws_s3_bucket.sitio.id
  policy = data.aws_iam_policy_document.sitio.json

  depends_on = [aws_s3_bucket_public_access_block.sitio]
}

resource "aws_cloudfront_origin_access_control" "sitio" {
  name                              = "${local.nombre}-sitio"
  description                       = "Acceso de CloudFront al bucket del sitio"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_function" "indice" {
  name    = "${local.nombre}-indice"
  runtime = "cloudfront-js-2.0"
  comment = "Agrega index.html a las rutas de carpeta"
  publish = true
  code    = file("${path.module}/funciones/indice.js")
}

# Cabeceras de seguridad (FR-010-03). El sitio no usa scripts ni estilos en línea ni recursos externos.
resource "aws_cloudfront_response_headers_policy" "seguridad" {
  name    = "${local.nombre}-cabeceras"
  comment = "Cabeceras de seguridad del sitio"

  security_headers_config {
    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      preload                    = false
      override                   = true
    }

    content_type_options {
      override = true
    }

    frame_options {
      frame_option = "SAMEORIGIN"
      override     = true
    }

    referrer_policy {
      referrer_policy = "strict-origin-when-cross-origin"
      override        = true
    }

    content_security_policy {
      content_security_policy = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'self'"
      override                = true
    }
  }

  custom_headers_config {
    items {
      header   = "Permissions-Policy"
      value    = "camera=(), microphone=(), geolocation=()"
      override = true
    }
  }
}

resource "aws_cloudfront_distribution" "sitio" {
  enabled             = true
  comment             = "Sitio de ${var.proyecto}"
  aliases             = [var.dominio]
  default_root_object = "index.html"
  http_version        = "http2and3"
  is_ipv6_enabled     = true
  price_class         = "PriceClass_100"

  origin {
    origin_id                = "s3-sitio"
    domain_name              = aws_s3_bucket.sitio.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.sitio.id
  }

  default_cache_behavior {
    target_origin_id           = "s3-sitio"
    viewer_protocol_policy     = "redirect-to-https"
    allowed_methods            = ["GET", "HEAD"]
    cached_methods             = ["GET", "HEAD"]
    compress                   = true
    cache_policy_id            = data.aws_cloudfront_cache_policy.optimizada.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.seguridad.id

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.indice.arn
    }
  }

  # Sin permiso de listado, S3 responde 403 a lo que no existe: se muestra como 404.
  custom_error_response {
    error_code            = 403
    response_code         = 404
    response_page_path    = "/404.html"
    error_caching_min_ttl = 60
  }

  custom_error_response {
    error_code            = 404
    response_code         = 404
    response_page_path    = "/404.html"
    error_caching_min_ttl = 60
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.sitio.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
}
