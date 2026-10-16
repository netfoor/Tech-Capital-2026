terraform {
  required_version = ">= 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # Estado local y fuera de git durante el hackathon (FR-010-06).
  # Para el piloto: backend "s3" con use_lockfile = true.
}
