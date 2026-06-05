# Arquitetura

## Visão geral (MVP)

```text
cron-job.org (30 min) → GitHub Actions workflow_dispatch
        ↓
PostgreSQL (Neon)
        ↑
FastAPI (Render ou Railway — fase futura)
```

| Componente | Hospedagem | Custo |
|------------|------------|-------|
| Crawler | GitHub Actions (free tier) | $0 |
| Banco | Neon (free tier) | $0 |
| API | Render / Railway (fase futura) | $0 ou próximo |

**Agendamento:** [cron-job.org](https://cron-job.org) dispara o workflow via API a cada 30 min (ver [github-actions.md](./github-actions.md)). O `schedule` nativo do GHA não é usado.

**Desenvolvimento local:** Docker Compose com PostgreSQL local.

---

## Stack tecnológica

| Camada | Tecnologia | Fase |
|--------|------------|------|
| Linguagem | Python 3.12+ | Atual |
| Banco de dados | PostgreSQL (Neon) | Atual |
| ORM | SQLAlchemy | Atual |
| Migrações | Alembic | Atual |
| Coleta | `httpx` + BeautifulSoup | Atual |
| Agendamento | cron-job.org → GHA `workflow_dispatch` | Atual |
| Testes | Pytest | Atual |
| Containerização | Docker Compose (local), Dockerfile | Atual |
| IaC | Terraform (somente prod) | Atual |
| API | FastAPI | Futura |
| Processamento | Pandas | Futura |
| ML | Ver [ml-notes.md](./ml-notes.md) | Futura |

### Terraform (prod)

Objetivos:

* Provisionar Neon
* Provisionar ambiente de execução da API
* Gerenciar variáveis de ambiente
* Permitir recriação completa do ambiente

Local usa Docker Compose — sem Terraform.

---

## Organização do código (`src/`)

Código de aplicação vive em **`src/`**. Infra, docs e código exploratório ficam na raiz.

| Local | Conteúdo | Motivo |
|-------|----------|--------|
| `src/core/` | Models, database, utils | Domínio transversal (ex-`shared/`) |
| `src/crawler/` | Collectors, parsers, jobs | Coleta SEMIL |
| `src/api/` | Routes, services, schemas *(fase 1)* | API FastAPI |
| `ml/` | Notebooks, experiments *(fase 2+)* | Exploratório — fora do pacote instalável |
| `scripts/` | Wrappers operacionais | Chamam módulos via `uv run python -m ...` |
| `docs/`, `docker/`, `terraform/`, `.github/` | Infra e documentação | Não é código de domínio |

**Imports:** pacotes top-level `core` e `crawler` (com `src/` no `PYTHONPATH` / config do pytest).

**Testes:** co-located em `src/<pacote>/tests/` (ex.: `src/crawler/tests/`).

**CLI:** `python -m crawler.jobs.run` (Makefile: `make crawl`, `make crawl-dry`).

**Alembic:** `src/core/database/alembic.ini` (Makefile: `make migrate`).

---

## Crawler

> **Prioridade atual do projeto.** Tudo mais depende da qualidade e continuidade desta coleta.

### Fonte

* **URL única de coleta:** `https://semil.sp.gov.br/travessias/travessias-automoveis/sao-sebastiao-ilhabela/`
* **Estratégia:** 1 GET por execução — o widget no topo da página exibe o resumo de **todas** as travessias (8 sentidos) em uma única resposta HTML
* Tipo: HTML estático (sem Playwright no MVP)
* Operador: SEMIL / DERSA (Governo de São Paulo)

> Alertas por rota (ex.: maré baixa) podem não aparecer no widget resumido. Se necessário no futuro, complementar com páginas individuais — fora do escopo do MVP.

### O que coletar por rota/sentido

| Campo | Origem |
|-------|--------|
| `wait_minutes` | "Tempo de Espera: X minutos" |
| `number_of_ships` | Contagem de embarcações em operação (ex.: `3` no header da rota) |
| `weather_alert` | Alertas exibidos no site (ex.: maré baixa, instabilidade do sistema) |
| `raw_payload` | HTML para re-parse — só em `parse_error`, uma linha por job |

Identificadores de rota: ver [data-model.md](./data-model.md).

### Agendamento

* **Frequência:** a cada 30 minutos (cron-job.org → `workflow_dispatch`)
* **Slots no DB:** `:00` e `:30` em `America/Sao_Paulo` (calculados na execução, não pelo cron externo)
* **Persistência:** `collected_at` truncado ao slot `:00` ou `:30` em `America/Sao_Paulo`, convertido para UTC antes do INSERT
* **Política de falha:**
  1. Primeira tentativa falha → **1 retry** imediato (backoff curto, ex.: 30s)
  2. Retry falha → registrar **8 linhas** com `scrape_status = site_down`
  3. Não tentar backfill de slots perdidos

### Valores de `scrape_status`

| Valor | Quando |
|-------|--------|
| `success` | Coleta e parse OK |
| `parse_error` | Site respondeu, mas o parser não extraiu os dados esperados |
| `site_down` | Site indisponível após retry |

### Fluxo de execução

```text
1. cron-job.org chama a API do GitHub → workflow Crawler inicia
2. GET único na URL de coleta
3. Parse HTML → extrair dados dos 8 sentidos + alertas globais
4. INSERT de 8 linhas em wait_time_observations (uma por ferry_route_id)
5. Fim do job (sem alertas por e-mail no MVP)
```

### GitHub Actions

Workflow: `.github/workflows/crawler.yml`

```yaml
on:
  workflow_dispatch:   # agendado via cron-job.org (POST /actions/workflows/crawler.yml/dispatches)

jobs:
  crawl:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    # steps: setup-uv → uv sync → uv run python -m crawler.jobs.run --save
```

Detalhes do cron-job.org: [github-actions.md](./github-actions.md).

**Secrets:**

| Secret | Uso |
|--------|-----|
| `DATABASE_URL` | Connection string Neon (prod) |

### Monitoramento e alertas (fora do MVP)

**SendGrid foi considerado e descartado por enquanto.** Avaliamos e-mail transacional (alerta stale: janela 06:00–06:15 SP, sem `success` nas últimas 12 h), mas o trial do SendGrid não atendeu (plano pago após 60 dias, projeto ainda cru). Preferimos validar coleta e dados antes de pagar provedor de e-mail.

**Monitoramento no MVP:**

* Logs do workflow GitHub Actions
* Consultas manuais ao Neon (Beekeeper, SQL Editor)
* `scripts/quality_report.py` (fase 0b) para gaps e taxa de `success`

**Reavaliar depois:** SendGrid, Resend, Brevo ou Amazon SES quando a coleta estiver estável e alertas forem prioridade.

### Idempotência

* Constraint única: `(ferry_route_id, collected_at)` — slot em `America/Sao_Paulo`, armazenado em UTC
* `raw_payload`: HTML completo apenas na **primeira** linha com `parse_error` do job; `success` e `site_down` ficam com `null`

### Riscos conhecidos

* **Instabilidade do site:** aviso global em `global_alert` do job; persistido em `raw_payload` apenas se houver `parse_error`
* **Limites GitHub Actions:** ~720 min/mês necessários (48 runs/dia × ~30s) — folga confortável no free tier
* **Mudança de layout HTML:** `raw_payload` permite re-parse; testes com fixtures HTML salvas

---

## Estrutura de pastas

```text
ferry-wait/
│
├── src/                         # código de aplicação
│   ├── core/                    # models, database, utils
│   │   ├── database/            # session, alembic, repository
│   │   ├── models/
│   │   └── utils/               # time_slots
│   ├── crawler/
│   │   ├── collectors/
│   │   ├── parsers/
│   │   │   └── fixtures/
│   │   ├── jobs/
│   │   └── tests/
│   └── api/                     # fase 1
│       ├── routes/
│       ├── services/
│       ├── schemas/
│       ├── repositories/
│       └── tests/
│
├── ml/                          # fase 2+ (fora de src/)
│   ├── notebooks/
│   ├── experiments/
│   ├── training/
│   └── evaluation/
│
├── scripts/                     # utilitários operacionais
│
├── docs/
│   ├── vision.md
│   ├── architecture.md
│   ├── roadmap.md
│   ├── api.md
│   ├── data-model.md
│   └── ml-notes.md
│
├── terraform/
│   ├── environments/
│   │   └── prod/
│   ├── modules/
│   │   ├── database/
│   │   └── app/
│   └── README.md
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── crawler.yml
│       ├── terraform.yml
│       └── migrate.yml
│
├── docker/
│   └── docker-compose.yml
│
├── pyproject.toml
├── uv.lock
├── Makefile
└── README.md
```

---

## Documentação relacionada

* [Visão do produto](./vision.md)
* [Modelo de dados](./data-model.md)
* [Roadmap](./roadmap.md)
