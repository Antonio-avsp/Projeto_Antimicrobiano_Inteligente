# Changelog

Todas as mudanças relevantes do **Antimicrobiano Inteligente** são registradas neste arquivo.

O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto adota o [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

## [0.3.0] - 2026-11-06

Motor de regras inteligente, painel de alertas, antibiograma cumulativo e dados de demonstração.

### Adicionado

- Motor de regras explicável no padrão *Strategy*, com alertas de time-out de 72 horas, duração excedida e profilaxia prolongada em `GET /alertas` (RF07, RF08 — [#13](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/13)).
- Alertas de antimicrobiano de uso restrito sem justificativa e de WATCH/RESERVE empírico sem cultura (RF09, RF12 — [#14](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/14)).
- Alertas de resistência com alternativas sensíveis e sugestão de descalonamento pela hierarquia AWaRe (RF10, RF11 — [#15](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/15)).
- Painel de alertas com filtros por tipo, severidade, setor e paciente, resumo por severidade e tipo, e teste de desempenho com 1.000 prescrições ativas (RF13, RNF01 — [#16](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/16)).
- Antibiograma cumulativo institucional com primeiro isolado por paciente e sinalização de amostra insuficiente (RF14 — [#17](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/17)).
- Carga de dados fictícios para demonstração com `python -m antimicrobiano.seed` ([#19](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/19)).

### Alterado

- Parâmetros clínicos (time-out, limite de profilaxia, janela de culturas e mínimo de isolados) centralizados em `ParametrosClinicos` e configuráveis por variáveis de ambiente `AMI_*` (RNF11 — [#18](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/18)).

## [0.2.0] - 2026-11-06

Cadastros essenciais da API: catálogo, prescrições, intervenções do PGA e microbiologia.

### Adicionado

- Catálogo de antimicrobianos com classificação AWaRe, nome único sem diferenciar maiúsculas/acentos, filtros e inativação lógica (RF01, RF02 — [#9](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/9)).
- Registro, consulta e atualização de prescrições com código de paciente pseudonimizado e cálculo do dia de terapia (RF03, RF04 — [#10](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/10)).
- Reavaliação (time-out) e encerramento de prescrições, com bloqueio de alterações em prescrições encerradas (RF05 — [#11](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/11)).
- Culturas microbiológicas, resultados e antibiogramas S/I/R (RF06 — [#12](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/12)).
- Branches `bugfix/` documentadas no fluxo Git Flow ([#37](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/37)).

### Corrigido

- A mensagem das tags de versão passa a preservar os títulos de seção do CHANGELOG ([#37](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/37)).

## [0.1.1] - 2026-11-05

Hotfix do processo de versionamento.

### Corrigido

- Publicação das tags de versão: o workflow `tag-versao.yml` cria a tag anotada `vX.Y.Z` com as notas do CHANGELOG sempre que uma versão é integrada na `main`, e permite marcar versões anteriores por execução manual. Corrige a ausência da tag `v0.1.0`, cujo push manual foi recusado pelo GitHub (HTTP 403) ([#35](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/35)).

## [0.1.0] - 2026-11-05

Documentação de planejamento e fundação técnica do projeto.

### Adicionado

- Termo de Abertura do Projeto com justificativa, visão, objetivos SMART, escopo, stakeholders, riscos e marcos ([#1](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/1)).
- Especificação de requisitos funcionais (RF01–RF18), não funcionais (RNF01–RNF12), regras de negócio (RN01–RN21) e glossário ([#2](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/2)).
- Casos de uso UC01–UC06 com fluxos principal, alternativos e de exceção ([#3](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/3)).
- Histórias de usuário US01–US18 e HT01 com critérios de aceite em Gherkin ([#4](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/4)).
- Arquitetura C4, modelo de dados (DER, dicionário e classes) e matriz de rastreabilidade ([#5](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/5)).
- Estrutura da API em FastAPI + SQLite com endpoint `GET /health`, testes com pytest, licença MIT, guia de contribuição e templates de issue/PR ([#6](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/6)).
- Pipeline de CI no GitHub Actions com testes em Python 3.11, 3.12 e 3.13 ([#7](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/7)).
- README com badges, guia de execução, quadro de funcionalidades e fluxo Git Flow ([#8](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/8)).

[Não lançado]: https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/compare/v0.3.0...develop
[0.3.0]: https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/tree/v0.1.0
