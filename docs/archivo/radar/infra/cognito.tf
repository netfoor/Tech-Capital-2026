# Acceso a la plataforma con Cognito y su Hosted UI (ADR-0009, FR-010-09).
# Las cuentas las da de alta el equipo; no hay registro abierto.
resource "aws_cognito_user_pool" "plataforma" {
  name                     = "${local.nombre}-usuarios"
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]
  deletion_protection      = "INACTIVE"

  admin_create_user_config {
    allow_admin_create_user_only = true

    invite_message_template {
      email_subject = "Tu acceso al Radar de Atención Turística"
      email_message = "Hola. Ya tienes acceso a la plataforma del Radar de Atención Turística de Puebla en https://${var.dominio}/plataforma/ . Usuario: {username}. Contraseña temporal: {####}. Te pedirá cambiarla al entrar."
      sms_message   = "Usuario {username}, contraseña temporal {####}"
    }
  }

  password_policy {
    minimum_length                   = 12
    require_lowercase                = true
    require_uppercase                = true
    require_numbers                  = true
    require_symbols                  = false
    temporary_password_validity_days = 7
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }
}

resource "aws_cognito_user_pool_domain" "plataforma" {
  domain                = var.cognito_prefijo
  user_pool_id          = aws_cognito_user_pool.plataforma.id
  managed_login_version = 1
}

resource "aws_cognito_user_pool_client" "plataforma" {
  name         = "${local.nombre}-sitio"
  user_pool_id = aws_cognito_user_pool.plataforma.id

  generate_secret                      = false
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  supported_identity_providers         = ["COGNITO"]
  explicit_auth_flows                  = ["ALLOW_REFRESH_TOKEN_AUTH"]
  prevent_user_existence_errors        = "ENABLED"

  callback_urls = [
    "https://${var.dominio}/plataforma/",
    "http://localhost:4321/plataforma/",
  ]
  logout_urls = [
    "https://${var.dominio}/",
    "http://localhost:4321/",
  ]

  id_token_validity      = 8
  access_token_validity  = 8
  refresh_token_validity = 1

  token_validity_units {
    id_token      = "hours"
    access_token  = "hours"
    refresh_token = "days"
  }
}

locals {
  cognito_dominio = "${aws_cognito_user_pool_domain.plataforma.domain}.auth.${var.region}.amazoncognito.com"
}
