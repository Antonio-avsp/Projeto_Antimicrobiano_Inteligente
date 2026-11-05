# 🧫 Antimicrobiano Inteligente

[![Versão](https://img.shields.io/github/v/tag/Antonio-avsp/Projeto_Antimicrobiano_Inteligente?label=vers%C3%A3o&sort=semver)](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/tags)
[![CI](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/actions/workflows/ci.yml)
[![Licença](https://img.shields.io/github/license/Antonio-avsp/Projeto_Antimicrobiano_Inteligente?label=licen%C3%A7a)](LICENSE)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-FE5196?logo=conventionalcommits&logoColor=white)](https://www.conventionalcommits.org/pt-br/v1.0.0/)
[![Git Flow](https://img.shields.io/badge/branching-Git%20Flow-F05032?logo=git&logoColor=white)](CONTRIBUTING.md)

**API REST de apoio ao Programa de Gerenciamento do Uso de Antimicrobianos (PGA / *antimicrobial stewardship*)**. Centraliza prescrições, culturas e antibiogramas de pacientes internados e usa um **motor de regras explicável** para alertar a equipe do PGA sobre tratamentos que precisam de intervenção: reavaliação de 72 horas, duração excedida, uso restrito sem justificativa, microrganismo resistente, oportunidade de descalonamento e mais.

> ⚠️ **Projeto acadêmico.** Ferramenta de **apoio à decisão** que não substitui o julgamento clínico. Utilize apenas dados fictícios.

## Sumário

- [O problema](#o-problema)
- [A solução](#a-solução)
- [Funcionalidades](#funcionalidades)
- [Stack tecnológica](#stack-tecnológica)
- [Como executar localmente](#como-executar-localmente)
- [Exemplos de uso](#exemplos-de-uso)
- [Documentação do projeto](#documentação-do-projeto)
- [Fluxo de trabalho (Git Flow, commits e versões)](#fluxo-de-trabalho-git-flow-commits-e-versões)
- [Roadmap e versões](#roadmap-e-versões)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Autor e licença](#autor-e-licença)

## O problema

A **resistência antimicrobiana** esteve diretamente associada a cerca de **1,27 milhão de mortes** no mundo em 2019 (*The Lancet*, 2022), e **30% a 50%** das prescrições hospitalares de antimicrobianos são consideradas desnecessárias ou inadequadas. Em hospitais de pequeno e médio porte, a equipe do PGA acompanha os tratamentos manualmente, em planilhas, o que causa:

- tratamentos que passam de **72 horas sem reavaliação** ou **excedem a duração prevista**;
- **terapias inadequadas** não detectadas (microrganismo resistente ao antimicrobiano em uso);
- **oportunidades de descalonamento** perdidas;
- critérios pouco padronizados e intervenções sem registro estruturado.

## A solução

O **Antimicrobiano Inteligente** cruza automaticamente prescrições, culturas e antibiogramas e gera, para cada data de referência, um **painel priorizado de alertas**. Cada alerta informa a regra aplicada, a severidade, as **evidências** usadas e a **recomendação** de conduta.

| Alerta | Quando dispara | Severidade |
|---|---|---|
| `TIMEOUT_REAVALIACAO` | Prescrição ativa há 72 h ou mais sem reavaliação | 🟡 MEDIA |
| `DURACAO_EXCEDIDA` | Dia de terapia maior que a duração prevista | 🟡 MEDIA |
| `PROFILAXIA_PROLONGADA` | Profilaxia planejada por mais de 24 h | 🟡 MEDIA |
| `RESTRITO_SEM_JUSTIFICATIVA` | Antimicrobiano de uso restrito sem justificativa | 🔴 ALTA |
| `SEM_CULTURA` | Antimicrobiano WATCH/RESERVE empírico sem cultura coletada | 🟡 MEDIA |
| `RESISTENCIA` | Cultura do paciente resistente (`R`) ao antimicrobiano prescrito | 🔴 ALTA |
| `DESCALONAMENTO` | Antibiograma permite opção de categoria AWaRe inferior | 🔵 BAIXA |

As regras seguem diretrizes reconhecidas — classificação **AWaRe** da OMS, diretriz nacional de PGA da **ANVISA**, recomendações **IDSA/SHEA** e norma **CLSI M39** — e estão detalhadas nas [regras de negócio](docs/requisitos.md#3-regras-de-negócio-rn).
