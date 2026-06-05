#!/usr/bin/env bash
# Run Terraform in prod with TFC + Neon credentials from .env.terraform or the shell.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/terraform/environments/prod/.env.terraform"
TF_DIR="$ROOT/terraform/environments/prod"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a
fi

if [[ -z "${TF_TOKEN_app_terraform_io:-}" ]] && [[ ! -f "${HOME}/.terraform.d/credentials.tfrc.json" ]]; then
  echo "ERROR: TF_TOKEN_app_terraform_io não definido." >&2
  echo "  Defina em terraform/environments/prod/.env.terraform" >&2
  echo "  Ou: terraform login" >&2
  exit 1
fi

if [[ -z "${TF_CLOUD_ORGANIZATION:-}" ]]; then
  echo "ERROR: TF_CLOUD_ORGANIZATION não definido (ex.: ferry-wait)." >&2
  exit 1
fi

if [[ -z "${NEON_API_KEY:-}" ]]; then
  echo "ERROR: NEON_API_KEY não definido." >&2
  exit 1
fi

if [[ ! -f "$TF_DIR/terraform.tfvars" ]]; then
  echo "ERROR: $TF_DIR/terraform.tfvars não existe (copie de terraform.tfvars.example)." >&2
  exit 1
fi

if [[ -n "${TF_BIN:-}" ]]; then
  :
elif command -v terraform >/dev/null 2>&1; then
  TF_BIN="$(command -v terraform)"
elif [[ -x "$ROOT/.tools/bin/terraform" ]]; then
  TF_BIN="$ROOT/.tools/bin/terraform"
else
  echo "ERROR: terraform not found in PATH or .tools/bin" >&2
  exit 1
fi

cd "$TF_DIR"
echo "Using $TF_BIN ($("$TF_BIN" version -json 2>/dev/null | grep -o '"terraform_version":"[^"]*"' | cut -d'"' -f4 || "$TF_BIN" version | head -1))" >&2
exec "$TF_BIN" "$@"
