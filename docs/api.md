# API

> **Status:** planejada para a Fase 1. Não implementar antes da coleta estar estável (Fase 0b).

## Objetivo

Expor consultas históricas sobre tempos de espera, permitindo responder perguntas como:

* Qual o melhor horário para atravessar em uma terça-feira?
* Qual o tempo esperado para uma data e horário específicos?
* Qual a distribuição histórica (p50, p90) para um horário?

Sem Machine Learning — apenas agregações sobre `wait_time_observations`.

---

## Stack prevista

* FastAPI
* SQLAlchemy (reutilizando modelos em `shared/`)
* Hospedagem: Render ou Railway (free tier)

---

## Endpoints planejados (rascunho)

Contratos a detalhar **antes da Fase 1**.

### Saúde

```
GET /health
```

Retorna status da API e conectividade com o banco.

### Histórico bruto

```
GET /wait-times/history
  ?ferry_route_id=sao_sebastiao_to_ilhabela
  &from=2026-05-01T00:00:00Z
  &to=2026-05-31T23:59:59Z
```

Lista observações coletadas no período.

### Analytics — melhor slot

```
GET /analytics/best-slot
  ?ferry_route_id=sao_sebastiao_to_ilhabela
  &weekday=tuesday
```

Retorna o horário com menor tempo médio de espera histórico para o dia da semana informado.

### Analytics — distribuição

```
GET /analytics/distribution
  ?ferry_route_id=sao_sebastiao_to_ilhabela
  &weekday=tuesday
  &hour=10
```

Retorna estatísticas (mean, p50, p90, sample_count) para o slot weekday + hour.

### Analytics — resumo

```
GET /analytics/summary
  ?ferry_route_id=sao_sebastiao_to_ilhabela
  &weekday=tuesday
  &hour=10
```

Agregação consolidada para consulta rápida.

### Previsão (Fase 3+)

```
GET /predict
  ?ferry_route_id=sao_sebastiao_to_ilhabela
  &target_at=2026-06-15T10:00:00-03:00
```

Estimativa do tempo de espera *se você chegar no horário alvo*. Contrato e implementação definidos nas Fases 2–3.

---

## Pendências (definir antes da Fase 1)

| Tópico | Opções a avaliar |
|--------|------------------|
| Autenticação | Pública vs API key vs uso pessoal sem auth |
| Versionamento | Prefixo `/v1/` |
| Caching | TTL por endpoint (analytics podem cachear por hora) |
| Paginação | Cursor vs offset para `/history` |
| Timezone | Entrada em `America/Sao_Paulo`, resposta com offset explícito |
| Rate limiting | Necessário se API pública |

---

## Documentação relacionada

* [Visão do produto](./vision.md)
* [Modelo de dados](./data-model.md)
* [Roadmap — Fase 1](./roadmap.md#fase-1--analytics-históricos)
* [Notas de ML — previsão](./ml-notes.md)
