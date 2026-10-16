locals {
  nombre = "${var.proyecto}-${var.entorno}"

  etiquetas = {
    proyecto = var.proyecto
    entorno  = var.entorno
  }
}

provider "aws" {
  profile = var.perfil_aws
  region  = var.region

  default_tags {
    tags = local.etiquetas
  }
}

# CloudFront solo acepta certificados de ACM emitidos en us-east-1.
provider "aws" {
  alias   = "us_east_1"
  profile = var.perfil_aws
  region  = "us-east-1"

  default_tags {
    tags = local.etiquetas
  }
}
