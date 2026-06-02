terraform {
  required_version = ">= 1.5"

  required_providers {
    neon = {
      source  = "kislerdm/neon"
      version = "~> 0.13"
    }
  }

  # Local state for solo MVP. For team use, switch to remote backend (S3, Terraform Cloud, etc.).
  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "neon" {
  # Authenticate via NEON_API_KEY (https://console.neon.tech/app/settings/api-keys).
}
