# Roadmap

## Visão das fases

```text
Fase 0a  →  Crawler MVP (1–2 semanas)
Fase 0b  →  Coleta contínua (2–3 meses)
Fase 1   →  Analytics históricos (API)
Fase 2   →  Validação de previsibilidade
Fase 3   →  Modelos estatísticos
Fase 4   →  Machine Learning (se justificado)
```

**Foco atual:** Fase 0a.

---

## Fase 0a — Crawler MVP

**Objetivo:** coletor funcional em produção, persistindo dados reais.

**Entregáveis:**

- [ ] Parser HTML para as 4 rotas (8 sentidos) — `src/crawler/parsers/`
- [ ] Modelo `wait_time_observations` + migração Alembic — `src/core/`
- [ ] Job de coleta com retry e `scrape_status` — `src/crawler/jobs/`
- [x] Persistência local (`save_observations`) — `src/core/database/repository.py`
- [x] GitHub Actions: crawler (cron :00/:30) + CI (`pytest`) — [`docs/github-actions.md`](./github-actions.md)
- [x] GHA `terraform plan` em PRs com mudanças em `terraform/`
- [x] GHA `terraform apply` no merge em `master` (infra prod)
- [x] GHA `alembic upgrade head` no merge em `master` quando `alembic/versions/` mudar
- [x] Neon PostgreSQL provisionado (Terraform prod) — ver [`terraform/README.md`](../terraform/README.md)
- [ ] Docker Compose para dev local
- [ ] Testes de parser com fixtures HTML — `src/crawler/tests/`
- [ ] Alertas por e-mail (parse error + DB stale) — `src/core/utils/`

**Duração estimada:** 1–2 semanas de implementação.

Detalhes técnicos: [architecture.md](./architecture.md)

---

## Fase 0b — Coleta Contínua e Qualidade

**Objetivo:** acumular histórico confiável antes de qualquer analytics.

**Entregáveis:**

- [ ] 30 dias de coleta estável (critérios de sucesso atingidos)
- [ ] `scripts/quality_report.py` — relatório (taxa de sucesso, gaps, distribuição de `wait_minutes`)
- [ ] Ajustes de parser se layout mudar (`src/crawler/parsers/`)

**Duração sugerida:** 2 a 3 meses de coleta antes de qualquer decisão sobre ML.

**Perguntas a responder:**

* Os dados são consistentes?
* Existem falhas de coleta sistemáticas?
* O site realmente atualiza a cada 30 minutos?
* Existe sazonalidade visível (mesmo com poucos meses)?

### Critérios de sucesso (Fase 0)

* ≥ 95% dos slots esperados coletados com `success` em 30 dias consecutivos
* Zero duplicatas não explicadas
* Spot-check manual: 10 amostras aleatórias batem com o site ao vivo
* Alertas de e-mail funcionando para parse error e DB stale (testados manualmente)

---

## Fase 1 — Analytics Históricos

**Objetivo:** responder perguntas usando apenas consultas históricas.

**Entregáveis:**

* API FastAPI com endpoints para melhor horário, médias, percentis (p50, p90), piores janelas
* Definição de contratos de API, autenticação e caching *(detalhar antes de implementar — ver [api.md](./api.md))*

Ainda sem Machine Learning.

---

## Fase 2 — Validação de Previsibilidade

**Objetivo:** descobrir se existe sinal suficiente para previsão.

**Análises:** sazonalidade semanal/diária, variabilidade por horário, correlação temporal, estabilidade dos padrões.

**Pergunta principal:** é possível prever melhor do que uma simples média histórica?

Metodologia de avaliação (holdout temporal, baselines, MAE) — **definir antes de iniciar** (ver [ml-notes.md](./ml-notes.md)).

Se a resposta for não, não seguir para ML.

---

## Fase 3 — Modelos Estatísticos

**Objetivo:** criar previsões sem ML complexo.

Avaliar: média móvel, média ponderada, modelos sazonais, Prophet.

**Métrica principal:** MAE.

Detalhes: [ml-notes.md](./ml-notes.md)

---

## Fase 4 — Machine Learning

**Objetivo:** avaliar se modelos supervisionados melhoram as previsões.

Primeira opção: XGBoost. Comparar contra média histórica e Prophet.

O modelo só deve ser adotado se superar **significativamente** os métodos mais simples.

Detalhes: [ml-notes.md](./ml-notes.md)

---

## Pendências (definir nas fases respectivas)

| Tópico | Quando |
|--------|--------|
| Metodologia de avaliação (MAE, holdout, baselines) | Antes da Fase 2 |
| Contratos da API, auth, caching | Antes da Fase 1 |
| Regras de validação de dados (range, outliers, duplicatas) | Início da Fase 1 |
| Contexto de calendário (feriados SP, férias escolares) | Fase 2 ou 3 |
| Formato final do produto (API pública, app, ferramenta pessoal) | Após Fase 1 |
| Validação cruzada com ground truth alternativo | Futuro |

---

## Documentação relacionada

* [Visão do produto](./vision.md)
* [Arquitetura](./architecture.md)
* [API (futuro)](./api.md)
* [Notas de ML](./ml-notes.md)
