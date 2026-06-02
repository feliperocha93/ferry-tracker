# Modelo de Dados

## Tabela principal: `wait_time_observations`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `id` | bigint / UUID | PK | Identificador |
| `ferry_route_id` | text | sim | Um dos 8 sentidos (ver abaixo) |
| `collected_at` | timestamptz | sim | Slot de coleta, **UTC** |
| `wait_minutes` | integer | não* | Tempo de espera em minutos |
| `number_of_ships` | smallint | não | Embarcações em operação |
| `weather_alert` | text | não | Alerta meteorológico/operacional exibido no site |
| `scrape_status` | text | sim | `success`, `parse_error`, `site_down` |
| `raw_payload` | jsonb | não | HTML bruto para debug/re-parse — **somente em `parse_error`**, **uma linha por job** |
| `created_at` | timestamptz | sim | Default `now()` |

\* Obrigatório quando `scrape_status = success`.

### Constraint de idempotência

```sql
UNIQUE (ferry_route_id, collected_at)
```

`collected_at` representa o slot truncado a `:00` ou `:30` em `America/Sao_Paulo`, armazenado em UTC.

---

## Identificadores de rota (`ferry_route_id`)

```text
sao_sebastiao_to_ilhabela
ilhabela_to_sao_sebastiao
santos_to_guaruja
guaruja_to_santos
bertioga_to_guaruja
guaruja_to_bertioga
santos_to_vicente_de_carvalho
vicente_de_carvalho_to_santos
```

---

## Exemplo

| ferry_route_id | collected_at (UTC) | wait_minutes | number_of_ships | scrape_status |
|----------------|-------------------|--------------|-----------------|---------------|
| sao_sebastiao_to_ilhabela | 2026-05-30 11:00:00+00 | 30 | 3 | success |
| ilhabela_to_sao_sebastiao | 2026-05-30 11:00:00+00 | 30 | 3 | success |
| santos_to_guaruja | 2026-05-30 11:30:00+00 | null | null | site_down |

---

## Regras

* Não armazenar apenas agregações — sempre preservar o dado bruto coletado.
* Timestamps sempre em UTC no banco; conversão para `America/Sao_Paulo` apenas na camada de apresentação.
* `raw_payload` preenchido apenas quando `scrape_status = parse_error` (fetch OK, parse falhou), na **primeira** rota com erro (ordem `FERRY_ROUTE_IDS`). Coletas `success` e `site_down` usam `null`.
* Regras de validação de `wait_minutes` (range, outliers) — **definir na Fase 1**.

---

## Features derivadas (fases futuras)

Informações calculadas a partir de `wait_time_observations` — não persistidas no MVP:

| Feature | Descrição |
|---------|-----------|
| `weekday` | Dia da semana (local) |
| `hour` | Hora do slot (local) |
| `month` | Mês |
| `is_holiday` | Feriado *(implementação posterior)* |
| `is_holiday_eve` | Véspera de feriado *(implementação posterior)* |
| `season` | Estação do ano |
| `prev_wait_minutes` | Tempo de espera no slot anterior |
| `rolling_avg` | Média móvel |
| `seasonality_index` | Indicadores de sazonalidade |

Usadas em analytics (Fase 1) e modelos (Fases 2–4). Ver [ml-notes.md](./ml-notes.md).

---

## Implementação

* Model SQLAlchemy: `src/core/models/wait_time_observation.py`
* Constantes de rota: `src/core/models/ferry_routes.py`
* Migrações Alembic: `src/core/database/`

---

## Documentação relacionada

* [Arquitetura — Crawler](./architecture.md#crawler)
* [Arquitetura — Organização do código](./architecture.md#organização-do-código-src)
* [Roadmap](./roadmap.md)
* [API (futuro)](./api.md)
