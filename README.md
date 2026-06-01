# ferry-wait

Coleta e previsão de tempo de espera em travessias de balsa do [SEMIL/DERSA](https://semil.sp.gov.br/travessias/travessias-automoveis/sao-sebastiao-ilhabela/) (São Paulo).

Documentação completa em [`docs/`](docs/).

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/) (gerenciamento de dependências)
- [Docker](https://www.docker.com/) (PostgreSQL local)
- Python 3.12+

Instalar uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# ou: pip install uv
```

Docker (Engine + Compose plugin, sem Docker Desktop):

```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose-plugin
sudo usermod -aG docker $USER   # depois, sair e entrar na sessão
```

`make db-up` usa `docker/.docker/config.json` para não depender do credential helper do Docker Desktop. Se `docker pull` falhar fora do Makefile com `docker-credential-desktop: not found`, remova `"credsStore": "desktop"` de `~/.docker/config.json` (comum após desinstalar o Desktop).

## Setup local

```bash
# 1. Instalar dependências
make install

# 2. Configurar variáveis de ambiente
cp .env.example .env

# 3. Subir PostgreSQL local
make db-up

# 4. Aplicar migrações (cria wait_time_observations)
make migrate

# 5. Verificar
make test
```

## Comandos

```bash
make help          # lista todos os alvos
make install       # uv sync
make test          # pytest
make db-up         # sobe Postgres (docker)
make db-down       # para Postgres
make migrate       # aplica migrações (requer .env e Postgres)
make crawl-dry     # coleta sem persistir (fase 0.4+)
make crawl         # coleta + persistência (fase 0.5+)
```

## Variáveis de ambiente

| Variável | Descrição |
|----------|-----------|
| `DATABASE_URL` | Connection string PostgreSQL |
| `SENDGRID_API_KEY` | API key SendGrid (alertas, fase 0.8) |
| `ALERT_EMAIL_FROM` | Remetente dos alertas |
| `ALERT_EMAIL_PARSE` | Destino: falhas de parse |
| `ALERT_EMAIL_FRESHNESS` | Destino: DB sem update |

Ver [`.env.example`](.env.example).

## Estrutura

```text
ferry-wait/
├── src/
│   ├── core/      # models, database, utils
│   ├── crawler/   # coleta e parse HTML
│   └── api/       # FastAPI (fase 1+)
├── ml/            # notebooks e experimentos (fase 2+)
├── scripts/       # utilitários operacionais
├── docker/        # Docker Compose (Postgres local)
├── docs/          # documentação do projeto
└── terraform/     # infra prod (fase 0.6+)
```

Detalhes em [`docs/architecture.md`](docs/architecture.md).

## Fase atual

**0.2 — Modelo de dados:** tabela `wait_time_observations`, Alembic em `src/core/database/`.

Próximo: [Fase 0.3](docs/roadmap.md) — parser HTML SEMIL.
