# Histórias de Usuário

Histórias de usuário do **Antimicrobiano Inteligente**, derivadas dos [requisitos](requisitos.md) e dos [casos de uso](casos-de-uso.md). Cada história alimenta uma issue do backlog no GitHub, onde os mesmos critérios de aceite são copiados.

**Convenções**

- Formato canônico: **Como** [ator], **quero** [ação] **para que** [valor de negócio].
- Critérios de aceite em **BDD/Gherkin em português** (`# language: pt`): *Dado* (contexto), *Quando* (ação) e *Então* (resultado esperado).
- Estimativa em *story points* (sequência de Fibonacci). Prioridade MoSCoW herdada do requisito.
- Critérios **INVEST**: cada história é independente, negociável, valiosa, estimável, pequena e testável.

## Resumo do backlog

| ID | História (resumo) | RF | Prioridade | Pontos | Issue | Release |
|---|---|---|---|---|---|---|
| US01 | Cadastrar antimicrobiano | RF01 | Must | 2 | [#9](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/9) | v0.2.0 |
| US02 | Consultar e manter o catálogo | RF02 | Must | 3 | [#9](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/9) | v0.2.0 |
| US03 | Registrar prescrição | RF03 | Must | 3 | [#10](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/10) | v0.2.0 |
| US04 | Consultar e atualizar prescrições | RF04 | Must | 3 | [#10](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/10) | v0.2.0 |
| US05 | Reavaliar e encerrar prescrição | RF05 | Must | 3 | [#11](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/11) | v0.2.0 |
| US06 | Registrar cultura e antibiograma | RF06 | Must | 5 | [#12](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/12) | v0.2.0 |
| US07 | Alerta de time-out de 72 horas | RF07 | Must | 3 | [#13](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/13) | v0.3.0 |
| US08 | Alertas de duração e profilaxia | RF08 | Must | 3 | [#13](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/13) | v0.3.0 |
| US09 | Alerta de uso restrito sem justificativa | RF09 | Must | 2 | [#14](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/14) | v0.3.0 |
| US10 | Alerta de resistência | RF10 | Must | 5 | [#15](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/15) | v0.3.0 |
| US11 | Sugestão de descalonamento | RF11 | Should | 5 | [#15](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/15) | v0.3.0 |
| US12 | Alerta de amplo espectro sem cultura | RF12 | Should | 3 | [#14](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/14) | v0.3.0 |
| US13 | Painel de alertas filtrável | RF13 | Must | 3 | [#16](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/16) | v0.3.0 |
| US14 | Antibiograma cumulativo | RF14 | Should | 5 | [#17](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/17) | v0.3.0 |
| HT01 | Dados de demonstração (história técnica) | — | Should | 2 | [#19](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/19) | v0.3.0 |
| US15 | Indicadores de consumo (DOT) | RF15 | Could | 5 | [#21](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/21) | v1.0.0 |
| US16 | Alerta de duplicidade terapêutica | RF16 | Could | 2 | [#22](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/22) | v1.0.0 |
| US17 | Autenticação e perfis de acesso | RF17 | Should | 8 | [#24](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/24) | v1.0.0 |
| US18 | Interface web do painel | RF18 | Could | 8 | [#26](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/26) | v1.0.0 |

---

## Catálogo de antimicrobianos

### US01 — Cadastrar antimicrobiano

> **Como** farmacêutico clínico do PGA, **quero** cadastrar antimicrobianos com classe, categoria AWaRe e indicação de uso restrito **para que** o motor de regras avalie as prescrições a partir de um catálogo padronizado.

```gherkin
# language: pt
Funcionalidade: Cadastro de antimicrobianos

  Cenário: Cadastro válido
    Dado que não existe antimicrobiano chamado "Ceftriaxona"
    Quando eu cadastrar "Ceftriaxona", classe "Cefalosporina de 3ª geração", categoria AWaRe "WATCH" e uso restrito falso
    Então o sistema deve responder 201 com o identificador gerado e ativo verdadeiro

  Cenário: Nome duplicado ignorando maiúsculas e acentos
    Dado que "Ceftriaxona" já está cadastrada
    Quando eu tentar cadastrar "CEFTRIAXONA"
    Então o sistema deve responder 409 informando que o nome já existe

  Cenário: Categoria AWaRe inválida
    Quando eu tentar cadastrar um antimicrobiano com categoria "XYZ"
    Então o sistema deve responder 422 indicando o campo "categoria_aware"
```

### US02 — Consultar e manter o catálogo

> **Como** farmacêutico clínico, **quero** listar, filtrar, atualizar e inativar antimicrobianos **para que** o catálogo permaneça alinhado à padronização do hospital.

```gherkin
# language: pt
Funcionalidade: Manutenção do catálogo

  Cenário: Filtrar por categoria e uso restrito
    Dado antimicrobianos ACCESS, WATCH e RESERVE cadastrados
    Quando eu listar com categoria_aware=WATCH e uso_restrito=true
    Então somente os antimicrobianos WATCH de uso restrito devem ser retornados

  Cenário: Atualizar dados
    Dado que "Vancomicina" está cadastrada sem uso restrito
    Quando eu atualizar o campo uso_restrito para verdadeiro
    Então a consulta de "Vancomicina" deve exibir uso_restrito verdadeiro

  Cenário: Inativar sem perder histórico
    Dado que "Cefalotina" está ativa
    Quando eu solicitar DELETE de "Cefalotina"
    Então o sistema deve responder 204
    E "Cefalotina" deve continuar consultável por id com ativo=false
    E não deve aparecer na listagem padrão

  Cenário: Antimicrobiano inexistente
    Quando eu consultar o antimicrobiano de id 999
    Então o sistema deve responder 404
```

---

## Prescrições

### US03 — Registrar prescrição

> **Como** farmacêutico clínico, **quero** registrar as prescrições de antimicrobianos dos pacientes internados **para que** o uso seja monitorado pelo PGA.

```gherkin
# language: pt
Funcionalidade: Registro de prescrições

  Cenário: Registro válido
    Dado que "Ceftriaxona" está ativa no catálogo
    Quando eu registrar uma prescrição para o paciente "PAC-0001", setor "Clínica Médica", indicação "EMPIRICA", início em 01/11/2026 e duração prevista de 7 dias
    Então o sistema deve responder 201 com status "ATIVA"

  Cenário: Código de paciente fora do padrão pseudonimizado
    Quando eu registrar uma prescrição para o paciente "João da Silva"
    Então o sistema deve responder 422 indicando o campo "paciente_codigo"

  Cenário: Antimicrobiano inativo
    Dado que "Cefalotina" está inativa
    Quando eu registrar uma prescrição de "Cefalotina"
    Então o sistema deve responder 422 informando que antimicrobiano inativo não pode ser prescrito

  Cenário: Data de início futura ou duração inválida
    Quando eu registrar uma prescrição com início posterior a hoje ou duração fora do intervalo de 1 a 90 dias
    Então o sistema deve responder 422
```

### US04 — Consultar e atualizar prescrições

> **Como** médico infectologista, **quero** listar, consultar e atualizar as prescrições filtrando por status, setor e paciente **para que** eu priorize a revisão diária.

```gherkin
# language: pt
Funcionalidade: Acompanhamento de prescrições

  Cenário: Filtrar ativas por setor
    Dado prescrições ativas na "UTI Adulto" e na "Clínica Médica"
    Quando eu listar com status=ATIVA e setor="UTI Adulto"
    Então somente as prescrições ativas da "UTI Adulto" devem ser retornadas

  Cenário: Consultar detalhe
    Dado a prescrição 1 iniciada há 3 dias
    Quando eu consultar a prescrição 1
    Então devo ver o antimicrobiano, a categoria AWaRe, as reavaliações e o dia de terapia 4

  Cenário: Atualizar justificativa
    Dado uma prescrição ativa de "Meropenem" sem justificativa
    Quando eu atualizar a justificativa para "Choque séptico com suspeita de ESBL"
    Então a prescrição deve exibir a nova justificativa
```

### US05 — Reavaliar e encerrar prescrição

> **Como** médico infectologista, **quero** registrar a reavaliação (*time-out*) e o encerramento das prescrições **para que** as intervenções do PGA fiquem documentadas e os alertas resolvidos sejam encerrados.

```gherkin
# language: pt
Funcionalidade: Intervenções do PGA

  Cenário: Registrar reavaliação
    Dado que a prescrição 1 está ativa
    Quando eu registrar uma reavaliação com conduta "MANTER" na data de hoje
    Então o sistema deve responder 201
    E a reavaliação deve constar no histórico da prescrição

  Cenário: Encerrar prescrição
    Dado que a prescrição 1 está ativa
    Quando eu encerrar a prescrição com status "CONCLUIDA" e data de término válida
    Então a prescrição deve passar a "CONCLUIDA" com a data de término registrada

  Cenário: Operação em prescrição encerrada
    Dado que a prescrição 1 está "CONCLUIDA"
    Quando eu tentar registrar uma reavaliação, atualizá-la ou encerrá-la novamente
    Então o sistema deve responder 409

  Cenário: Datas inconsistentes
    Quando eu informar data de reavaliação ou de término anterior ao início da prescrição ou posterior a hoje
    Então o sistema deve responder 422
```
