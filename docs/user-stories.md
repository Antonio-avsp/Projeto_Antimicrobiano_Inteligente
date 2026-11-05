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

---

## Microbiologia

### US06 — Registrar cultura e antibiograma

> **Como** analista do laboratório de microbiologia, **quero** registrar a coleta e o resultado das culturas com o antibiograma **para que** a equipe ajuste a terapia com base em evidências.

```gherkin
# language: pt
Funcionalidade: Culturas e antibiogramas

  Cenário: Registrar coleta
    Quando eu registrar uma cultura de "SANGUE" do paciente "PAC-0001" coletada hoje
    Então o sistema deve responder 201 com status "PENDENTE"

  Cenário: Resultado positivo com antibiograma
    Dado que a cultura 1 está "PENDENTE"
    Quando eu registrar o resultado "POSITIVA" com microrganismo "Escherichia coli" e antibiograma Ceftriaxona=R e Gentamicina=S
    Então a cultura deve passar a "POSITIVA" exibindo o antibiograma

  Cenário: Resultado positivo sem microrganismo
    Quando eu registrar o resultado "POSITIVA" sem microrganismo
    Então o sistema deve responder 422

  Cenário: Antimicrobiano repetido no antibiograma
    Quando eu informar a "Gentamicina" duas vezes no mesmo antibiograma
    Então o sistema deve responder 422

  Cenário: Resultado negativo com antibiograma
    Quando eu registrar o resultado "NEGATIVA" informando microrganismo ou antibiograma
    Então o sistema deve responder 422

  Cenário: Listar culturas por paciente
    Dado que o paciente "PAC-0001" possui 2 culturas
    Quando eu listar culturas filtrando por paciente "PAC-0001"
    Então as 2 culturas devem ser retornadas da coleta mais recente para a mais antiga
```

---

## Motor de regras (alertas inteligentes)

> Nos cenários abaixo, "consultar os alertas" significa `GET /alertas` com a data de referência indicada (padrão: hoje).

### US07 — Alerta de time-out de 72 horas

> **Como** farmacêutico clínico, **quero** ser alertado quando uma prescrição completar 72 horas sem reavaliação **para que** o time-out recomendado pelo PGA seja garantido.

```gherkin
# language: pt
Funcionalidade: Alerta de time-out

  Cenário: Prescrição com 72h sem reavaliação
    Dado uma prescrição ativa iniciada em 01/11/2026 sem reavaliação
    Quando eu consultar os alertas com data de referência 04/11/2026
    Então deve existir um alerta "TIMEOUT_REAVALIACAO" de severidade "MEDIA"

  Cenário: Prescrição reavaliada
    Dado que a prescrição recebeu reavaliação em 03/11/2026
    Quando eu consultar os alertas com data de referência 04/11/2026
    Então não deve existir alerta "TIMEOUT_REAVALIACAO" para ela

  Cenário: Antes de 72h
    Dado uma prescrição ativa iniciada em 02/11/2026 sem reavaliação
    Quando eu consultar os alertas com data de referência 04/11/2026
    Então não deve existir alerta "TIMEOUT_REAVALIACAO"
```

### US08 — Alertas de duração e profilaxia

> **Como** farmacêutico clínico, **quero** ser alertado sobre tratamentos que ultrapassaram a duração prevista e profilaxias planejadas por mais de 24 horas **para que** a exposição desnecessária a antimicrobianos seja evitada.

```gherkin
# language: pt
Funcionalidade: Alertas de duração

  Cenário: Duração excedida
    Dado uma prescrição ativa iniciada em 01/11/2026 com duração prevista de 3 dias
    Quando eu consultar os alertas com data de referência 05/11/2026
    Então deve existir um alerta "DURACAO_EXCEDIDA" informando o dia de terapia 5

  Cenário: Dentro da duração prevista
    Dado uma prescrição ativa iniciada em 01/11/2026 com duração prevista de 7 dias
    Quando eu consultar os alertas com data de referência 05/11/2026
    Então não deve existir alerta "DURACAO_EXCEDIDA"

  Cenário: Profilaxia prolongada
    Dado uma prescrição ativa com indicação "PROFILAXIA" e duração prevista de 3 dias
    Quando eu consultar os alertas
    Então deve existir um alerta "PROFILAXIA_PROLONGADA" recomendando suspensão em até 24 horas

  Cenário: Prescrições encerradas não geram alertas
    Dado uma prescrição "CONCLUIDA"
    Quando eu consultar os alertas
    Então nenhum alerta deve ser gerado para ela
```

### US09 — Alerta de uso restrito sem justificativa

> **Como** coordenador do PGA, **quero** ser alertado sobre antimicrobianos de uso restrito prescritos sem justificativa **para que** a política de restrição do hospital seja cumprida.

```gherkin
# language: pt
Funcionalidade: Política de uso restrito

  Cenário: Restrito sem justificativa
    Dado que "Meropenem" é de uso restrito
    E existe uma prescrição ativa de "Meropenem" sem justificativa
    Quando eu consultar os alertas
    Então deve existir um alerta "RESTRITO_SEM_JUSTIFICATIVA" de severidade "ALTA"

  Cenário: Justificativa registrada
    Dado que a prescrição de "Meropenem" possui justificativa preenchida
    Quando eu consultar os alertas
    Então não deve existir alerta "RESTRITO_SEM_JUSTIFICATIVA" para ela
```

### US10 — Alerta de resistência

> **Como** médico infectologista, **quero** ser alertado quando o microrganismo isolado for resistente ao antimicrobiano prescrito **para que** terapias inadequadas sejam corrigidas rapidamente.

```gherkin
# language: pt
Funcionalidade: Descompasso microrganismo x antimicrobiano

  Cenário: Microrganismo resistente
    Dado uma prescrição ativa de "Ceftriaxona" para o paciente "PAC-0001"
    E uma cultura positiva do mesmo paciente com "Klebsiella pneumoniae" resistente à "Ceftriaxona" e sensível ao "Meropenem"
    Quando eu consultar os alertas
    Então deve existir um alerta "RESISTENCIA" de severidade "ALTA"
    E a recomendação deve listar "Meropenem" como alternativa sensível

  Cenário: Cultura fora da janela de relevância
    Dado que a única cultura resistente foi coletada 30 dias antes do início da prescrição
    Quando eu consultar os alertas
    Então não deve existir alerta "RESISTENCIA"
```

### US11 — Sugestão de descalonamento

> **Como** médico infectologista, **quero** receber sugestões de descalonamento quando o antibiograma permitir um antimicrobiano de categoria AWaRe inferior **para que** a pressão seletiva seja reduzida sem perda de eficácia.

```gherkin
# language: pt
Funcionalidade: Descalonamento guiado por antibiograma

  Cenário: Oportunidade de descalonamento
    Dado uma prescrição ativa de "Meropenem" (WATCH) para o paciente "PAC-0002"
    E uma cultura positiva com "Escherichia coli" sensível a "Meropenem" e a "Gentamicina" (ACCESS)
    Quando eu consultar os alertas
    Então deve existir um alerta "DESCALONAMENTO" de severidade "BAIXA" sugerindo "Gentamicina"

  Cenário: Prescrição já na categoria ACCESS
    Dado uma prescrição ativa de "Amoxicilina" (ACCESS)
    Quando eu consultar os alertas
    Então não deve existir alerta "DESCALONAMENTO"

  Cenário: Opção não sensível em todas as culturas
    Dado duas culturas positivas relevantes e "Gentamicina" sensível em apenas uma delas
    Quando eu consultar os alertas
    Então "Gentamicina" não deve ser sugerida
```

### US12 — Alerta de amplo espectro sem cultura

> **Como** farmacêutico clínico, **quero** ser alertado quando um antimicrobiano WATCH ou RESERVE for iniciado empiricamente sem cultura coletada **para que** a coleta de culturas no início da terapia seja estimulada.

```gherkin
# language: pt
Funcionalidade: Cultura antes do amplo espectro

  Cenário: Empírico de amplo espectro sem cultura
    Dado uma prescrição ativa "EMPIRICA" de "Piperacilina + tazobactam" (WATCH) para "PAC-0003"
    E nenhuma cultura do paciente "PAC-0003" na janela de relevância
    Quando eu consultar os alertas
    Então deve existir um alerta "SEM_CULTURA" de severidade "MEDIA"

  Cenário: Cultura coletada
    Dado uma cultura do paciente "PAC-0003" coletada no dia do início da terapia
    Quando eu consultar os alertas
    Então não deve existir alerta "SEM_CULTURA"

  Cenário: Antimicrobiano ACCESS ou indicação não empírica
    Dado uma prescrição de "Amoxicilina" (ACCESS) ou uma profilaxia sem cultura
    Quando eu consultar os alertas
    Então não deve existir alerta "SEM_CULTURA"
```

### US13 — Painel de alertas filtrável

> **Como** membro da equipe do PGA, **quero** um painel de alertas filtrável por tipo, severidade, setor e paciente, com resumo por severidade, **para que** as intervenções do dia sejam priorizadas.

```gherkin
# language: pt
Funcionalidade: Painel de alertas

  Cenário: Ordenação e resumo
    Dado que existem alertas de severidade ALTA, MEDIA e BAIXA
    Quando eu consultar o painel de alertas
    Então os alertas devem vir ordenados de ALTA para BAIXA
    E o resumo deve informar a quantidade de alertas por severidade e por tipo

  Cenário: Filtros combinados
    Quando eu filtrar o painel por severidade=ALTA e setor="UTI Adulto"
    Então somente alertas de severidade ALTA da "UTI Adulto" devem ser retornados

  Cenário: Filtro por tipo e paciente
    Quando eu filtrar por tipo=RESISTENCIA e paciente_codigo="PAC-0001"
    Então somente alertas de resistência do paciente "PAC-0001" devem ser retornados

  Cenário: Transparência do alerta
    Quando eu consultar qualquer alerta
    Então ele deve conter tipo, severidade, mensagem, recomendação e as evidências usadas pela regra

  Cenário: Data de referência inválida
    Quando eu informar data_referencia em formato inválido
    Então o sistema deve responder 422
```

---

## Relatórios

### US14 — Antibiograma cumulativo

> **Como** gestor da CCIH, **quero** gerar o antibiograma cumulativo do hospital em um período **para que** os protocolos de terapia empírica sejam orientados pelo perfil local de sensibilidade.

```gherkin
# language: pt
Funcionalidade: Antibiograma cumulativo

  Cenário: Percentual de sensibilidade
    Dado 4 culturas positivas de "Escherichia coli" de pacientes distintos no período, com "Gentamicina" S, S, S e R
    Quando eu gerar o antibiograma cumulativo do período
    Então "Escherichia coli" x "Gentamicina" deve apresentar 4 testados e 75,0% de sensibilidade

  Cenário: Primeiro isolado por paciente
    Dado 2 culturas positivas de "Escherichia coli" do mesmo paciente no período
    Quando eu gerar o antibiograma cumulativo
    Então somente o primeiro isolado deve ser contabilizado

  Cenário: Amostra insuficiente
    Quando uma combinação microrganismo x antimicrobiano tiver menos de 30 isolados testados
    Então ela deve ser sinalizada com amostra_suficiente=false

  Cenário: Filtro por setor
    Quando eu gerar o relatório filtrando setor="UTI Adulto"
    Então somente culturas da "UTI Adulto" devem ser consideradas

  Cenário: Período inválido
    Quando eu informar data inicial posterior à data final
    Então o sistema deve responder 422
```

---

## História técnica

### HT01 — Dados de demonstração

> **Como** avaliador do projeto, **quero** carregar dados fictícios de demonstração com um único comando **para que** eu explore a API e o painel de alertas logo após a instalação.

```gherkin
# language: pt
Funcionalidade: Carga de demonstração

  Cenário: Carga em banco vazio
    Dado um banco de dados vazio
    Quando eu executar "python -m antimicrobiano.seed"
    Então o catálogo deve conter ao menos 15 antimicrobianos classificados pela AWaRe
    E o painel de alertas do dia deve apresentar ao menos um alerta de cada tipo implementado

  Cenário: Execução repetida
    Dado que a carga já foi executada
    Quando eu executar a carga novamente sem a opção --reset
    Então nenhum registro duplicado deve ser criado e uma mensagem deve informar que a base já possui dados

  Cenário: Recriar a base
    Quando eu executar "python -m antimicrobiano.seed --reset"
    Então a base deve ser recriada apenas com os dados de demonstração
```

---

## Planejadas para a iteração 2 (v1.0.0)

### US15 — Indicadores de consumo (DOT)

> **Como** gestor da CCIH, **quero** acompanhar os dias de terapia (DOT) por antimicrobiano e por categoria AWaRe **para que** o consumo e as metas do PGA sejam monitorados.

```gherkin
# language: pt
Funcionalidade: Indicadores de consumo

  Cenário: DOT por categoria AWaRe
    Dado prescrições de "Ceftriaxona" (WATCH) por 5 dias e de "Amoxicilina" (ACCESS) por 3 dias no período
    Quando eu consultar os indicadores do período
    Então devo ver WATCH = 5 e ACCESS = 3 dias de terapia
    E o percentual de uso ACCESS deve ser 37,5%

  Cenário: Prescrição parcialmente no período
    Dado uma prescrição iniciada antes do período e encerrada dentro dele
    Quando eu consultar os indicadores
    Então somente os dias dentro do período devem ser contabilizados
```

### US16 — Alerta de duplicidade terapêutica

> **Como** farmacêutico clínico, **quero** ser alertado quando um paciente tiver duas prescrições ativas da mesma classe de antimicrobiano **para que** a duplicidade terapêutica seja evitada.

```gherkin
# language: pt
Funcionalidade: Duplicidade terapêutica

  Cenário: Mesma classe para o mesmo paciente
    Dado duas prescrições ativas da classe "Cefalosporina de 3ª geração" para "PAC-0001"
    Quando eu consultar os alertas
    Então deve existir um alerta "DUPLICIDADE_TERAPEUTICA" para cada prescrição envolvida

  Cenário: Classes diferentes
    Dado prescrições ativas de classes diferentes para o mesmo paciente
    Quando eu consultar os alertas
    Então não deve existir alerta "DUPLICIDADE_TERAPEUTICA"
```

### US17 — Autenticação e perfis de acesso

> **Como** coordenador do PGA, **quero** que apenas usuários autenticados acessem a API, com permissões por perfil, **para que** os dados fiquem protegidos e a autoria das intervenções seja registrada.

```gherkin
# language: pt
Funcionalidade: Controle de acesso

  Cenário: Acesso sem token
    Quando uma requisição a um endpoint protegido for feita sem token
    Então o sistema deve responder 401

  Cenário: Perfil sem permissão
    Dado um usuário com perfil "LABORATORIO"
    Quando ele tentar inativar um antimicrobiano
    Então o sistema deve responder 403
```

### US18 — Interface web do painel

> **Como** farmacêutico clínico, **quero** visualizar o painel de alertas em uma interface web simples **para que** eu use o sistema no dia a dia sem ferramentas técnicas.

```gherkin
# language: pt
Funcionalidade: Painel web

  Cenário: Visualizar painel
    Dado que existem alertas para a data de hoje
    Quando eu abrir a página do painel
    Então devo ver os alertas agrupados por severidade, indicada por cor e por texto
    E o resumo com a quantidade de alertas por severidade

  Cenário: Filtrar por setor
    Quando eu selecionar o setor "UTI Adulto"
    Então somente os alertas da "UTI Adulto" devem ser exibidos
```
