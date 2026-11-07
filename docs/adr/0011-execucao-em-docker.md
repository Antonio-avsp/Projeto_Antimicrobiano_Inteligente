# ADR 0011 — Execução reprodutível com Docker

- **Situação:** Aceita
- **Data:** 07/11/2026
- **Versão:** v1.0.0
- **Issue:** #61

## Contexto

Avaliadores e futuros colaboradores precisam executar o sistema sem preparar o ambiente Python (RNF06).

## Decisão

Imagem `python:3.12-slim` com usuário sem privilégios e healthcheck, e `docker-compose.yml` com o banco SQLite em volume e configuração lida do `.env`. O CI constrói a imagem e verifica o `/health`.

## Alternativas consideradas

- **Somente instalação local:** depende da versão do Python e do sistema de cada pessoa.

## Consequências

- Execução em um comando, igual em qualquer máquina.
- A imagem base é atualizada pelo Dependabot.
- SQLite em volume atende a uma instância; várias instâncias exigiriam PostgreSQL (ADR 0002).
