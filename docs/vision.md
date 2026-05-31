# Visão do Produto

## Contexto

O [Departamento Hidroviário de São Paulo (SEMIL/DERSA)](https://semil.sp.gov.br/travessias/travessias-automoveis/sao-sebastiao-ilhabela/) mantém um site oficial com o tempo estimado de espera para travessias de balsa. Esse site é a **fonte de verdade** para quem pretende atravessar.

O site é atualizado aproximadamente a cada 30 minutos e exibe o tempo de espera em intervalos de 30 minutos.

O objetivo deste projeto é coletar esse histórico continuamente, armazená-lo e construir um sistema capaz de prever o tempo de espera esperado para uma determinada data e horário.

O produto não deve começar com Machine Learning. A prioridade inicial é coletar dados, validar hipóteses e entender se existe sinal suficiente para justificar um modelo preditivo.

## Escopo de rotas (MVP)

O site lista 8 travessias (16 sentidos ida/volta). Coletaremos apenas 4 pares para o MVP:

| Rota | Sentidos |
|------|----------|
| São Sebastião ↔ Ilhabela | ida e volta |
| Santos ↔ Guarujá | ida e volta |
| Bertioga ↔ Guarujá | ida e volta |
| Santos ↔ Vicente de Carvalho | ida e volta |

Total: **8 `ferry_route_id`** (4 rotas × 2 sentidos).

**Dados históricos:** coleta forward-only a partir do deploy. Não há backfill.

---

## Definições

| Termo | Significado |
|-------|-------------|
| **Estimativa do site** | Valor exibido no momento da coleta — tempo de espera *agora* na fila daquele terminal. |
| **Horário alvo** | Momento em que o usuário pretende *chegar* ao terminal para embarcar. |
| **Previsão (produto)** | Estimativa do tempo de espera *se você chegar no horário alvo X*, derivada do histórico de estimativas coletadas. |
| **`collected_at`** | Timestamp UTC em que o crawler executou a coleta. |
| **Proxy de verdade** | Por enquanto, a estimativa oficial do site é suficiente como ground truth. Validações cruzadas (ex.: câmeras, relatos) ficam para implementações futuras. |

---

## Caso de uso principal

**Planejar viagem com dias de antecedência:** o usuário informa rota, data e horário de chegada e recebe uma estimativa baseada em padrões históricos.

## Perguntas que o sistema deve responder (fases futuras)

* Qual o melhor horário para atravessar em uma terça-feira?
* Qual o melhor horário em um sábado?
* Qual o melhor período durante um final de semana?
* Qual o tempo esperado para uma determinada data e horário?
* Qual a distribuição histórica dos tempos de espera para determinado horário?
* Qual a confiabilidade da previsão?

O produto deve evoluir de análises históricas simples para previsões baseadas em modelos estatísticos e, apenas se fizer sentido, Machine Learning.

**Formato do produto final:** depende do sucesso das fases anteriores (API pública, ferramenta pessoal, ou app). Definir após Fase 1.

---

## Objetivos

### Objetivo principal

Prever o tempo de espera da travessia utilizando histórico de dados coletados automaticamente.

### Objetivos secundários

* Construir uma base histórica confiável.
* Descobrir padrões de sazonalidade.
* Identificar horários de menor congestionamento.
* Validar se o problema é previsível.
* Avaliar se modelos de Machine Learning superam métodos estatísticos simples.

---

## Princípios do Projeto

* Simplicidade acima de sofisticação.
* Não introduzir ML antes de validar a qualidade dos dados.
* Infraestrutura mínima.
* Custos próximos de zero durante o MVP.
* Arquitetura monolítica modular.
* **Foco atual: Crawler** — nada de API ou ML até a coleta estar estável.

---

## Documentação relacionada

* [Arquitetura](./architecture.md)
* [Roadmap](./roadmap.md)
* [Modelo de dados](./data-model.md)
* [API (futuro)](./api.md)
* [Notas de ML (futuro)](./ml-notes.md)
