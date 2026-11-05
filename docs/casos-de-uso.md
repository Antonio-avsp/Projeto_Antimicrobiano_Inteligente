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
