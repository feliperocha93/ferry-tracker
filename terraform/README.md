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
3. [Terraform Cloud](https://app.terraform.io/) — workspace `ferry-wait-prod`
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
export TF_API_TOKEN="seu-token"
export NEON_API_KEY="napi_..."

terraform init -migrate-state
```

Criar workspace `ferry-wait-prod` na UI do TFC (ou deixar o init criar).

## Day-to-day (local)

```bash
export NEON_API_KEY="napi_..."
export TF_CLOUD_ORGANIZATION="sua-org"
export TF_API_TOKEN="seu-token"
# neon_org_id: terraform.tfvars ou -var

make tf-init
make tf-plan
```

Na CI, `NEON_ORG_ID` e `TF_CLOUD_ORGANIZATION` vêm das **repository variables** do GitHub; `neon_org_id` não precisa de `terraform.tfvars` no runner.

## `DATABASE_URL` format

| Uso | Prefixo |
|-----|---------|
| App / Alembic / GitHub secret | `postgresql+psycopg://` |
| URI crua do Neon | `postgresql://` — converter antes de usar |

## State and secrets

- State remoto: Terraform Cloud workspace `ferry-wait-prod`
- `terraform.tfstate` local (bootstrap): pode remover **após** `init -migrate-state` bem-sucedido
- Commit `.terraform.lock.hcl`
- Never commit `terraform.tfvars`, API keys, or connection strings

## Free tier notes

- `history_retention_seconds = 21600` (6 h max on free plan)
- Default endpoint autoscaling: 0.25–1 CU
- Cold start após idle — relevante para cron do crawler

## Troubleshooting

| Issue | Fix |
|-------|-----|
| CI plan quer **criar** projeto Neon de novo | State não migrado para TFC — rode `terraform init -migrate-state` |
| `org_id` required | `NEON_ORG_ID` no GitHub ou `neon_org_id` em `terraform.tfvars` |
| `psycopg2` no migrate | Use `postgresql+psycopg://` em `DATABASE_URL` |
| TFC login failed | `TF_API_TOKEN` + `TF_CLOUD_ORGANIZATION` |
