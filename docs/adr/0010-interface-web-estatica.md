# ADR 0010 — Interface web estática servida pela própria API

- **Situação:** Aceita
- **Data:** 07/11/2026
- **Versão:** v1.0.0
- **Issue:** #26

## Contexto

A equipe do PGA precisava usar o painel sem o Swagger (RF18), mas o projeto não tem frontend nem processo de build de JavaScript.

## Decisão

Uma página HTML com CSS e JavaScript puros, servida em `/painel` pelo FastAPI, que faz login e consome a mesma API com o token. O conteúdo vindo da API é sempre inserido como texto.

## Alternativas consideradas

- **SPA com React/Vue:** exige toolchain de build e outra pasta para manter.
- **Templates renderizados no servidor:** duplicaria a lógica de autenticação da API.

## Consequências

- Nenhuma dependência nova e um único processo para implantar.
- A interface usa exatamente a API documentada.
- Para telas mais complexas, um frontend dedicado pode substituir a página sem mudar a API.
