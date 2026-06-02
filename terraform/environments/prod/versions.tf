terraform {
  required_version = ">= 1.5"

  required_providers {
    neon = {
      source  = "kislerdm/neon"
      version = "~> 0.13"
    }
  }

  # Remote state via Terraform Cloud (workspace: ferry-wait-prod).
  # Set TF_CLOUD_ORGANIZATION locally and in GitHub repo variables.
  cloud {
    workspaces {
      name = "ferry-wait-prod"
    }
  }
}

provider "neon" {
  # Authenticate via NEON_API_KEY (https://console.neon.tech/app/settings/api-keys).
}
