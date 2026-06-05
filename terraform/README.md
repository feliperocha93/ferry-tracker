# Neon PostgreSQL (production)

Terraform provisions a **Neon project** for ferry-wait production. Scope: database only (no app hosting).

## Workflow

| Ação | Onde | Quando |
|------|------|--------|
| Bootstrap `apply` | Local (one-time) | Primeira criação do Neon |
| `make tf-plan` | Local | Antes de PR com mudanças em `terraform/` |
| `terraform plan` | GitHub Actions | PRs que alteram `terraform/` |
| `terraform apply` | GitHub Actions | Push em `master` após merge |
| `alembic upgrade head` | GitHub Actions | Push em `master` se `alembic/versions/` mudou |

`make tf-apply` **não existe** — apply de rotina só na CI.

Detalhes dos workflows: [`docs/github-actions.md`](../docs/github-actions.md).

## Prerequisites

1. [Neon account](https://console.neon.tech/) (free tier)
2. [Terraform](https://developer.hashicorp.com/terraform/install) ≥ 1.5
3. [Terraform Cloud](https://app.terraform.io/) — workspace `ferry-wait`
4. Neon **API key** e **Organization ID**

## Layout

```text
terraform/
├── modules/database/
├── environments/prod/    # Terraform Cloud backend
└── README.md
```

## Bootstrap (concluído se Neon já existe)

Referência one-time (apply manual, sem target `make`):

```bash
cd terraform/environments/prod
cp terraform.tfvars.example terraform.tfvars
export NEON_API_KEY="napi_..."
terraform init && terraform plan && terraform apply
```

Configurar GitHub secret `DATABASE_URL` com `postgresql+psycopg://...`.

## Migrar state local → Terraform Cloud

Obrigatório **antes** de confiar no workflow `terraform.yml` na CI:

```bash
cd terraform/environments/prod
export TF_CLOUD_ORGANIZATION="sua-org"
export TF_TOKEN_app_terraform_io="seu-token"
export NEON_API_KEY="napi_..."

terraform init -migrate-state
```

Criar workspace `ferry-wait` na UI do TFC (ou deixar o init criar).

## Day-to-day (local)

Credenciais num arquivo (recomendado — evita export só do `NEON_API_KEY` e esquecer o TFC):

```bash
cd terraform/environments/prod
cp .env.terraform.example .env.terraform
# Editar: TF_TOKEN_app_terraform_io, NEON_API_KEY (TF_CLOUD_ORGANIZATION já é ferry-wait)

cd ../../..
make tf-check-env   # sanity check
make tf-init
make tf-plan
```

Alternativa: `export TF_CLOUD_ORGANIZATION TF_TOKEN_app_terraform_io NEON_API_KEY` **na mesma sessão** antes de `terraform init`. Só `NEON_API_KEY` não basta — o erro *Required token could not be found* é falta de `TF_TOKEN_app_terraform_io` ou `terraform login`.

Na CI, `NEON_ORG_ID` e `TF_CLOUD_ORGANIZATION` vêm das **repository variables** do GitHub; `neon_org_id` não precisa de `terraform.tfvars` no runner.

## `DATABASE_URL` format

| Uso | Prefixo |
|-----|---------|
| App / Alembic / GitHub secret | `postgresql+psycopg://` |
| URI crua do Neon | `postgresql://` — converter antes de usar |

## State and secrets

- State remoto: Terraform Cloud workspace `ferry-wait`
- `terraform.tfstate` local (bootstrap): pode remover **após** `init -migrate-state` bem-sucedido
- Commit `.terraform.lock.hcl`
- Never commit `terraform.tfvars`, API keys, or connection strings

## Free tier notes

- `history_retention_seconds = 21600` (6 h max on free plan)
- Default endpoint autoscaling: 0.25–1 CU
- Cold start após idle — relevante para runs do crawler (cron-job.org)

## Troubleshooting

| Issue | Fix |
|-------|-----|
| *Required token could not be found* | `TF_TOKEN_app_terraform_io` em `.env.terraform` |
| *Incompatible Terraform version* | TFC workspace → versão **Latest** (não `~> 1.9.0`) |
| *Unreadable module directory* | TFC workspace → **Execution mode: Local** |
| CI plan quer **criar** Neon de novo | State não migrado — `make tf-init` e responda `yes` |
| `org_id` required | `NEON_ORG_ID` no GitHub ou `neon_org_id` em `terraform.tfvars` |
| `psycopg2` no migrate | Use `postgresql+psycopg://` em `DATABASE_URL` |
