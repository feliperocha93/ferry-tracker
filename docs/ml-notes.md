# Notas de Machine Learning

> **Status:** fora do escopo até a Fase 2. Não implementar ML antes de validar qualidade dos dados e previsibilidade.

## Princípio

Adotar sempre o método **mais simples que funcione**. ML só entra se modelos estatísticos simples e Prophet não forem suficientes.

Ordem de avaliação:

1. Estatística simples (média histórica, média por weekday+hour)
2. Prophet
3. XGBoost
4. LightGBM

Não utilizar redes neurais inicialmente.

---

## Onde vive o código ML

Exploração e experimentos ficam em **`ml/`** na raiz do repositório (fora de `src/`), pois não são código de produção no MVP:

```text
ml/
├── notebooks/      # análises ad hoc
├── experiments/    # runs locais
├── training/       # scripts de treino (fase 4)
└── evaluation/     # comparação de modelos
```

Scripts em `ml/` importam dados e tipos de `src/core/` e, se necessário, agregações futuras de `src/api/`.

---

## Fase 2 — Validação de previsibilidade

### Pergunta central

É possível prever melhor do que uma simples média histórica?

### Análises esperadas

* Sazonalidade semanal
* Sazonalidade diária (por hora)
* Variabilidade por horário
* Correlação temporal (autocorrelação)
* Estabilidade dos padrões ao longo do tempo

### Metodologia de avaliação (a definir antes da Fase 2)

| Aspecto | Diretriz provável |
|---------|-------------------|
| **Target** | `wait_minutes` para um `ferry_route_id` em um horário alvo |
| **Horizonte** | Previsão para dias à frente (caso de uso: planejar viagem) |
| **Split** | Holdout temporal — nunca split aleatório em série temporal |
| **Baselines** | Média global; média por weekday+hour; último valor observado |
| **Métrica principal** | MAE (Mean Absolute Error) |
| **Métricas secundárias** | RMSE, erro percentual |
| **Confiabilidade** | Intervalos via percentis históricos (p10–p90) |

Se nenhum método superar a baseline weekday+hour de forma consistente, **não seguir para Fase 3/4**.

---

## Fase 3 — Modelos estatísticos

Candidatos:

* Média móvel
* Média ponderada (slots recentes com mais peso)
* Decomposição sazonal clássica
* [Prophet](https://facebook.github.io/prophet/)

**Métrica de adoção:** MAE vs baselines da Fase 2.

---

## Fase 4 — Machine Learning supervisionado

### Primeira opção: XGBoost

Features candidatas (derivadas — ver [data-model.md](./data-model.md)):

* `hour`, `weekday`, `month`
* `is_holiday`, `is_holiday_eve` *(quando calendário estiver implementado)*
* `number_of_ships` (quando disponível)
* `prev_wait_minutes`, `rolling_avg`
* Lags temporais (wait_minutes em t-1, t-2, …)

### Critério de adoção

Comparar contra:

* Média histórica por weekday+hour (baseline)
* Melhor modelo estatístico da Fase 3 (Prophet)

Adotar ML **somente** se MAE melhorar de forma significativa e estável no holdout temporal.

---

## Features de calendário (implementação posterior)

Relevantes para rotas litorâneas de SP:

* Feriados nacionais e estaduais (São Paulo)
* Vésperas de feriado prolongado
* Férias escolares (jan, jul, dez)
* Restrições operacionais (ex.: caminhões em Ilhabela — contexto externo, não coletado pelo crawler)

Definir na Fase 2 ou 3.

---

## Ground truth futuro

Por enquanto, a estimativa oficial do site é proxy suficiente. Validações futuras possíveis:

* Comparação com relatos de usuários
* Análise de câmeras ao vivo (complexo — fora de escopo)
* Correlacionar `scrape_status = success` com instabilidade declarada no site

---

## Documentação relacionada

* [Visão do produto](./vision.md)
* [Modelo de dados — features derivadas](./data-model.md#features-derivadas-fases-futuras)
* [Roadmap — Fases 2–4](./roadmap.md)
* [API — endpoint de previsão](./api.md#previsão-fase-3)
