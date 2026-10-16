variable "perfil_aws" {
  description = "Perfil de AWS CLI con el que se aplica la infraestructura"
  type        = string
  default     = "Fortino-IAM-Admin"
}

variable "region" {
  description = "Región principal de los recursos"
  type        = string
  default     = "us-east-1"
}

variable "dominio" {
  description = "Subdominio público del sitio. Su zona DNS está en Cloudflare"
  type        = string
  default     = "techcapital.foor.dev"
}

variable "entorno" {
  description = "Nombre del entorno, usado en nombres y etiquetas"
  type        = string
  default     = "hackathon"
}

variable "proyecto" {
  description = "Nombre del proyecto, usado en nombres y etiquetas"
  type        = string
  default     = "radar-atencion-turistica"
}
