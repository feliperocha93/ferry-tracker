# Arquitetura

## Visão geral (MVP)

```text
GitHub Actions (cron, :00 e :30 America/Sao_Paulo)
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

**Fallback do crawler:** se GitHub Actions free tier não for suficiente (limites de minutos, confiabilidade), avaliar Render Cron ou Railway.

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
| Agendamento | GitHub Actions (cron) | Atual |
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
| `raw_payload` | Resposta HTML para reprocessamento |

Identificadores de rota: ver [data-model.md](./data-model.md).

### Agendamento

* **Frequência:** a cada 30 minutos, alinhado a `:00` e `:30` no horário de São Paulo
* **Cron (GitHub Actions):** `0,30 * * * *` com `timezone: America/Sao_Paulo`
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
1. GitHub Actions dispara no :00 ou :30 (America/Sao_Paulo)
2. GET único na URL de coleta
3. Parse HTML → extrair dados dos 8 sentidos + alertas globais
4. INSERT de 8 linhas em wait_time_observations (uma por ferry_route_id)
5. Se parse_error em qualquer rota → e-mail de alerta (parse)
6. Ao final do job, verificar freshness global → e-mail se DB sem update
```

### GitHub Actions

Workflow: `.github/workflows/crawler.yml`

```yaml
on:
  schedule:
    - cron: '0,30 * * * *'
      timezone: America/Sao_Paulo

jobs:
  crawl:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    env:
      TZ: America/Sao_Paulo
```

**Secrets:**

| Secret | Uso |
|--------|-----|
| `DATABASE_URL` | Connection string Neon (prod) |
| `ALERT_EMAIL_PARSE` | Destino para falhas de parse |
| `ALERT_EMAIL_FRESHNESS` | Destino para DB sem update |
| SMTP / SendGrid | Envio de e-mails |

### Monitoramento e alertas (e-mail)

| Alerta | Condição | Destinatário |
|--------|----------|--------------|
| **Parse failure** | Qualquer rota com `scrape_status = parse_error` no job | `ALERT_EMAIL_PARSE` |
| **DB stale** | Nenhuma linha com `scrape_status = success` nos últimos 45 min | `ALERT_EMAIL_FRESHNESS` |

### Idempotência

* Constraint única: `(ferry_route_id, collected_at)` — slot em `America/Sao_Paulo`, armazenado em UTC
* `raw_payload`: resposta HTML completa por job (replicada nas 8 linhas ou apenas na primeira — definir na implementação)

### Riscos conhecidos

* **Instabilidade do site:** avisos de sistema instável — registrar em `weather_alert` / `raw_payload`; não tratar como parse error se a página carregar
* **Limites GitHub Actions:** ~720 min/mês necessários (48 runs/dia × ~30s) — folga confortável no free tier
* **Mudança de layout HTML:** `raw_payload` permite re-parse; testes com fixtures HTML salvas

---

## Estrutura de pastas

```text
ferry-wait/
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
│       └── crawler.yml
│
├── crawler/
│   ├── collectors/
│   ├── parsers/
│   │   └── fixtures/
│   ├── jobs/
│   └── tests/
│
├── api/                         # fase futura
│   ├── routes/
│   ├── services/
│   ├── schemas/
│   ├── repositories/
│   └── tests/
│
├── ml/                          # fase futura
│   ├── notebooks/
│   ├── experiments/
│   ├── training/
│   └── evaluation/
│
├── shared/
│   ├── database/
│   ├── models/
│   └── utils/
│
├── scripts/
│
├── docker/
│   └── docker-compose.yml
│
├── .cursor/
│   └── rules/
│
└── README.md
```

---

## Documentação relacionada

* [Visão do produto](./vision.md)
* [Modelo de dados](./data-model.md)
* [Roadmap](./roadmap.md)
