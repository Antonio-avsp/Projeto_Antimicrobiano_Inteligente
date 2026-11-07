# ADR 0009 — Logs estruturados em JSON com identificador da requisição

- **Situação:** Aceita
- **Data:** 07/11/2026
- **Versão:** v1.0.0
- **Issue:** #59

## Contexto

Sem logs estruturados, não era possível relacionar um erro relatado pelo usuário ao que aconteceu no servidor.

## Decisão

Um middleware atribui a cada requisição um identificador (`X-Request-ID`), devolve-o na resposta e no corpo dos erros e registra método, rota, status e duração em JSON com o `logging` da biblioteca padrão.

## Alternativas consideradas

- **structlog ou loguru:** dependência extra para uma necessidade simples.
- **Logs de acesso em texto do Uvicorn:** difíceis de filtrar e sem o identificador.

## Consequências

- Um erro relatado pode ser localizado pelo identificador.
- Logs prontos para ferramentas de agregação.
- O log de acesso do Uvicorn deve ser desligado (`--no-access-log`) para evitar duplicidade.
