# GitHub Actions

Workflows em [`.github/workflows/`](../.github/workflows/).

| Workflow | Gatilho | Função |
|----------|---------|--------|
| `ci.yml` | push / PR em `master` ou `main` | `pytest` (sem Neon, sem SEMIL live) |
| `crawler.yml` | cron `:00`/`:30` SP + manual | Coleta + persistência em prod |
| `terraform.yml` | PR ou push com mudanças em `terraform/` | `plan` (PR) / `apply` (push `master`) |
| `migrate.yml` | push em `master` com mudanças em `alembic/versions/` | `alembic upgrade head` em prod |

## Configuração única no GitHub

Repositório → **Settings** → **Secrets and variables** → **Actions**.

### Secrets

| Nome | Usado em | Descrição |
|------|----------|-----------|
| `DATABASE_URL` | `crawler`, `migrate` | `postgresql+psycopg://...` (Neon prod) |
| `NEON_API_KEY` | `terraform` | API key Neon |
| `TF_API_TOKEN` | `terraform` | [User token](https://app.terraform.io/app/settings/tokens) do Terraform Cloud |

### Variables (repository)

| Nome | Usado em | Descrição |
|------|----------|-----------|
| `TF_CLOUD_ORGANIZATION` | `terraform` | Nome da org no [Terraform Cloud](https://app.terraform.io/) |
| `NEON_ORG_ID` | `terraform` | Organization ID do Neon (mesmo valor de `neon_org_id` no `terraform.tfvars`) |

SendGrid (`SENDGRID_*`, `ALERT_EMAIL_*`) — fase 0.8; opcional criar os secrets agora.

## Terraform Cloud (antes do primeiro apply na CI)

1. Criar conta em [app.terraform.io](https://app.terraform.io/)
2. Criar workspace **`ferry-wait`** (mesmo nome do `versions.tf`)
3. Gerar **User API token** → secret `TF_API_TOKEN` no GitHub
4. Definir variable `TF_CLOUD_ORGANIZATION` no GitHub

### Migrar state do bootstrap local

Se você já rodou `terraform apply` local com backend `local`:

```bash
cd terraform/environments/prod
export TF_CLOUD_ORGANIZATION="sua-org"
export TF_API_TOKEN="seu-token"
export NEON_API_KEY="napi_..."

terraform init -migrate-state
# Confirmar migração quando perguntado
```

Depois disso, `make tf-plan` local também usa o state remoto (mesmas env vars).

**Importante:** só faça push do workflow `terraform.yml` **depois** da migração. Caso contrário, um apply na CI com workspace vazio pode tentar **criar um segundo** projeto Neon.

## Validação

### CI

- Abrir um PR → workflow **CI** verde

### Crawler

- **Actions** → **Crawler** → **Run workflow**
- Conferir 8 inserts no Neon; repetir no mesmo slot → sem duplicatas

### Terraform

- PR que altera `terraform/` → job **Terraform** com plan (sem apply)
- Merge em `master` → plan + apply (se houve mudanças em `terraform/`)

### Migrate

- PR com nova revisão em `alembic/versions/` → após merge, workflow **Migrate** aplica em prod

## Cron do crawler

`0,30 * * * *` com `timezone: America/Sao_Paulo` — alinhado aos slots de coleta do SEMIL.
