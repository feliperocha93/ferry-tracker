# GitHub Actions

Workflows em [`.github/workflows/`](../.github/workflows/).

| Workflow | Gatilho | Função |
|----------|---------|--------|
| `ci.yml` | push / PR em `master` ou `main` | `pytest` (sem Neon, sem SEMIL live) |
| `crawler.yml` | [cron-job.org](https://cron-job.org) (30 min) + manual | Coleta + persistência em prod |
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

- **Actions** → **Crawler** → **Run workflow** (manual)
- Ou aguardar disparo do [cron-job.org](#agendamento-do-crawler-cron-joborg)
- Conferir 8 inserts no Neon; repetir no mesmo slot → sem duplicatas

### Terraform

- PR que altera `terraform/` → job **Terraform** com plan (sem apply)
- Merge em `master` → plan + apply (se houve mudanças em `terraform/`)

### Migrate

- PR com nova revisão em `alembic/versions/` → após merge, workflow **Migrate** aplica em prod

## Agendamento do crawler (cron-job.org)

O `schedule` nativo do GitHub Actions foi removido (atrasos e baixa previsibilidade). O workflow `crawler.yml` dispara só via **`workflow_dispatch`**, acionado a cada **30 minutos** pelo [cron-job.org](https://cron-job.org).

### Por que não GitHub `schedule`?

- Runs podem atrasar vários minutos (ou falhar em fila alta)
- Só roda na branch padrão; repositório inativo pausa o cron
- [cron-job.org](https://cron-job.org) chama a API do GitHub com horário mais estável (acompanhar nos primeiros dias)

### 1. Token fine-grained (GitHub)

1. **Settings** → **Developer settings** → **Fine-grained personal access tokens**
2. Repositório: `ferry-tracker` (ajuste se o nome no GitHub for outro)
3. Permissões: **Actions** → Read and write; **Contents** → Read
4. Guardar o token — usar só no cron-job.org (não commitar)

### 2. Job no cron-job.org

| Campo | Valor |
|-------|--------|
| **URL** | `https://api.github.com/repos/feliperocha93/ferry-tracker/actions/workflows/crawler.yml/dispatches` |
| **Método** | `POST` |
| **Schedule** | A cada 30 min (ex.: `*/30 * * * *`, timezone `America/Sao_Paulo`) |
| **Body** | `{"ref":"master"}` |

**Headers:**

```text
Accept: application/vnd.github+json
Authorization: Bearer <seu-token>
X-GitHub-Api-Version: 2022-11-28
Content-Type: application/json
```

**Sucesso:** HTTP **204** (sem corpo). Conferir em **Actions** → **Crawler** → evento `workflow_dispatch`.

### 3. Teste manual (curl)

```bash
curl -sS -o /dev/null -w "%{http_code}\n" -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Content-Type: application/json" \
  -d '{"ref":"master"}' \
  https://api.github.com/repos/feliperocha93/ferry-tracker/actions/workflows/crawler.yml/dispatches
```

Esperado: `204`.

### Slots no banco

O horário do cron-job.org **não** define `collected_at`. O job calcula o slot `:00` ou `:30` (America/Sao_Paulo) no momento da execução (`current_collection_slot()`). Pequenos atrasos do cron-job ou do GHA ainda caem no slot correto se rodarem antes do próximo meia-hora.
