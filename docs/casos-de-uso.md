# Especificação de Casos de Uso

Casos de uso do **Antimicrobiano Inteligente**, derivados dos [requisitos](requisitos.md). Na iteração 1 todos os casos de uso são realizados pela API REST (Swagger UI em `/docs`); os códigos HTTP indicados nos fluxos de exceção fazem parte do contrato.

## 1. Atores

| Ator | Tipo | Descrição | Casos de uso |
|---|---|---|---|
| **Farmacêutico clínico** | Primário (humano) | Membro do PGA responsável pela triagem diária das prescrições de antimicrobianos e pelo registro das intervenções. | UC01, UC02, UC03, UC05 |
| **Médico infectologista** | Primário (humano) | Coordena clinicamente o PGA: reavalia tratamentos, corrige terapias inadequadas e decide descalonamentos. | UC02, UC03, UC05, UC06 |
| **Analista de microbiologia** | Primário (humano) | Profissional do laboratório que registra as culturas, os microrganismos isolados e os antibiogramas. | UC04 |
| **Gestor da CCIH** | Primário (humano) | Mantém a padronização do catálogo e acompanha o perfil local de resistência. | UC01, UC06 |
| **Motor de regras** | Secundário (sistema) | Componente interno que avalia as prescrições ativas em uma data de referência e produz os alertas. É acionado sempre que o painel é consultado. | UC05 |

## 2. Diagrama de casos de uso

```mermaid
flowchart LR
    farm["«ator»<br/>Farmacêutico clínico"]
    infecto["«ator»<br/>Médico infectologista"]
    lab["«ator»<br/>Analista de microbiologia"]
    gestor["«ator»<br/>Gestor da CCIH"]
    motor["«sistema»<br/>Motor de regras"]

    subgraph sistema["Antimicrobiano Inteligente"]
        direction TB
        UC01(["UC01 Manter catálogo de antimicrobianos"])
        UC02(["UC02 Registrar e acompanhar prescrição"])
        UC03(["UC03 Reavaliar e encerrar prescrição"])
        UC04(["UC04 Registrar cultura e antibiograma"])
        UC05(["UC05 Consultar painel de alertas"])
        UC06(["UC06 Gerar antibiograma cumulativo"])
        AVAL(["Avaliar regras clínicas"])
    end

    farm --- UC01
    farm --- UC02
    farm --- UC03
    farm --- UC05
    infecto --- UC02
    infecto --- UC03
    infecto --- UC05
    infecto --- UC06
    lab --- UC04
    gestor --- UC01
    gestor --- UC06
    UC05 -. "«include»" .-> AVAL
    AVAL --- motor
```

## 3. Resumo

| UC | Nome | Atores primários | Requisitos | Issue |
|---|---|---|---|---|
| UC01 | Manter catálogo de antimicrobianos | Farmacêutico clínico, Gestor da CCIH | RF01, RF02 | #9 |
| UC02 | Registrar e acompanhar prescrição | Farmacêutico clínico, Médico infectologista | RF03, RF04 | #10 |
| UC03 | Reavaliar (time-out) e encerrar prescrição | Médico infectologista, Farmacêutico clínico | RF05 | #11 |
| UC04 | Registrar cultura e antibiograma | Analista de microbiologia | RF06 | #12 |
| UC05 | Consultar painel de alertas inteligentes | Farmacêutico clínico, Médico infectologista | RF07 a RF13 | #13 a #16 |
| UC06 | Gerar antibiograma cumulativo | Gestor da CCIH, Médico infectologista | RF14 | #17 |
| UC07 | Consultar indicadores de consumo (planejado) | Gestor da CCIH | RF15 | #21 |
| UC08 | Autenticar usuário (planejado) | Todos | RF17 | #24 |

---

## 4. Especificações

### UC01 — Manter catálogo de antimicrobianos

| Item | Descrição |
|---|---|
| **Objetivo** | Manter a lista padronizada de antimicrobianos do hospital, com a classificação usada pelo motor de regras. |
| **Atores** | Farmacêutico clínico (primário), Gestor da CCIH |
| **Requisitos** | RF01, RF02 · RN01, RN02, RN03 |
| **Pré-condições** | API em execução. |
| **Pós-condições** | Catálogo atualizado; itens inativos deixam de ser aceitos em novas prescrições. |

**Fluxo principal — cadastrar antimicrobiano**

1. O ator envia `POST /antimicrobianos` com nome, classe, categoria AWaRe e indicação de uso restrito.
2. O sistema valida os campos obrigatórios e a categoria AWaRe.
3. O sistema normaliza o nome e verifica a unicidade (RN01).
4. O sistema grava o antimicrobiano como **ativo** e responde `201 Created` com o registro e seu identificador.

**Fluxos alternativos**

- **FA01 — Listar com filtros:** o ator envia `GET /antimicrobianos` com filtros opcionais (`categoria_aware`, `uso_restrito`, `ativo`, `busca`). O sistema responde `200` com os itens ordenados por nome (por padrão, somente ativos).
- **FA02 — Consultar:** `GET /antimicrobianos/{id}` responde `200` com o item, mesmo que inativo.
- **FA03 — Atualizar:** `PATCH /antimicrobianos/{id}` com os campos alterados. Se o nome mudar, a RN01 é verificada novamente. Resposta `200`.
- **FA04 — Inativar:** `DELETE /antimicrobianos/{id}` marca o item como inativo, preservando o histórico (RN03). Resposta `204`.

**Fluxos de exceção**

- **FE01 — Nome duplicado (RN01):** `409 Conflict` com a mensagem "Já existe um antimicrobiano com este nome".
- **FE02 — Dados inválidos** (nome vazio, categoria inexistente): `422 Unprocessable Entity` indicando o campo.
- **FE03 — Antimicrobiano inexistente** em FA02, FA03 ou FA04: `404 Not Found`.

---

### UC02 — Registrar e acompanhar prescrição

| Item | Descrição |
|---|---|
| **Objetivo** | Registrar as prescrições de antimicrobianos para que sejam monitoradas pelo motor de regras. |
| **Atores** | Farmacêutico clínico (primário), Médico infectologista |
| **Requisitos** | RF03, RF04 · RN02, RN04 a RN08 · RNF04 |
| **Pré-condições** | Antimicrobiano cadastrado e ativo no catálogo (UC01). |
| **Pós-condições** | Prescrição registrada com status `ATIVA` e incluída na avaliação do painel (UC05). |

**Fluxo principal — registrar prescrição**

1. Na revisão diária do prontuário, o farmacêutico identifica um novo tratamento com antimicrobiano.
2. O ator envia `POST /prescricoes` com o código pseudonimizado do paciente, setor, antimicrobiano, dose, intervalo, via, indicação, diagnóstico, data de início, duração prevista e, se houver, a justificativa.
3. O sistema valida o código do paciente (RN04), a data de início (RN05) e os limites de duração e intervalo (RN06).
4. O sistema verifica se o antimicrobiano existe e está ativo (RN02).
5. O sistema grava a prescrição com status `ATIVA` e responde `201 Created`, incluindo o dia de terapia atual.

**Fluxos alternativos**

- **FA01 — Listar com filtros:** `GET /prescricoes?status=ATIVA&setor=UTI Adulto&paciente_codigo=PAC-0001` responde `200` com as prescrições ordenadas da data de início mais recente para a mais antiga.
- **FA02 — Consultar detalhe:** `GET /prescricoes/{id}` responde `200` com o antimicrobiano, as reavaliações e o dia de terapia.
- **FA03 — Atualizar prescrição ativa:** `PATCH /prescricoes/{id}` (ex.: inclusão da justificativa) responde `200`.
- **FA04 — Restrito sem justificativa:** o registro é aceito (RN07) e o alerta `RESTRITO_SEM_JUSTIFICATIVA` passa a aparecer no painel (UC05) até a justificativa ser registrada (FA03).

**Fluxos de exceção**

- **FE01 — Código de paciente fora do padrão** (ex.: um nome): `422` indicando `paciente_codigo`.
- **FE02 — Antimicrobiano inexistente:** `404`; **antimicrobiano inativo:** `422` com a mensagem "Antimicrobiano inativo não pode ser prescrito".
- **FE03 — Data de início futura, duração ou intervalo fora dos limites:** `422`.
- **FE04 — Prescrição inexistente** em FA02 ou FA03: `404`.
- **FE05 — Atualização de prescrição encerrada (RN08):** `409 Conflict`.
