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
| `TF_TOKEN_app_terraform_io` | `terraform` | [User token](https://app.terraform.io/app/settings/tokens) do Terraform Cloud |

### Variables (repository)

| Nome | Usado em | Descrição |
|------|----------|-----------|
| `TF_CLOUD_ORGANIZATION` | `terraform` | Nome da org no [Terraform Cloud](https://app.terraform.io/) |
| `NEON_ORG_ID` | `terraform` | Organization ID do Neon (mesmo valor de `neon_org_id` no `terraform.tfvars`) |

SendGrid (`SENDGRID_*`, `ALERT_EMAIL_*`) — fase 0.8; opcional criar os secrets agora.

## Terraform Cloud (antes do primeiro apply na CI)

1. Criar conta em [app.terraform.io](https://app.terraform.io/)
2. Criar workspace **`ferry-wait`** (mesmo nome do `versions.tf`)
3. Gerar **User API token** → secret `TF_TOKEN_app_terraform_io` no GitHub
4. Definir variable `TF_CLOUD_ORGANIZATION` no GitHub

### Ajustes no workspace TFC (`ferry-wait`)

No [workspace ferry-wait](https://app.terraform.io/app/ferry-wait/workspaces/ferry-wait):

1. **Settings → General → Execution mode** → **Local**  
   (com **Remote**, o plan roda no TFC e não acha `../../modules/database`.)
2. **Terraform Version** → **Latest** (ou `>= 1.5`) — evite `~> 1.9.0`, que só aceita 1.9.x.

### Debug local

```bash
cp terraform/environments/prod/.env.terraform.example terraform/environments/prod/.env.terraform
# preencher TF_TOKEN_app_terraform_io + NEON_API_KEY
make tf-check-env && make tf-init && make tf-plan
```

### Migrar state do bootstrap local

Se você já rodou `terraform apply` local com backend `local`:

```bash
cd terraform/environments/prod
export TF_CLOUD_ORGANIZATION="sua-org"
export TF_TOKEN_app_terraform_io="seu-token"
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
