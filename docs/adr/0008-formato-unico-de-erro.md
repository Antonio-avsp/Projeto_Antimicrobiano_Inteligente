# ADR 0008 — Formato único de erro com mensagens em português

- **Situação:** Aceita
- **Data:** 07/11/2026
- **Versão:** v1.0.0
- **Issue:** #58

## Contexto

Erros de negócio respondiam `{"detail": "..."}` e erros de validação usavam o formato do framework, em inglês, o que dificultava o consumo pela interface web e contrariava o RNF03.

## Decisão

Todos os erros — de negócio, de validação e do framework — respondem `{codigo, mensagem, campos, id_requisicao}`. As mensagens do Pydantic são traduzidas por tipo de erro, e erros inesperados viram `500` com mensagem genérica.

## Alternativas consideradas

- **Manter `detail` do FastAPI:** dois formatos diferentes para o cliente tratar.
- **RFC 7807 (Problem Details):** mais campos do que o necessário; pode ser adotado no futuro sem mudar os códigos.

## Consequências

- Clientes tratam um único esquema, documentado no OpenAPI.
- Nenhum detalhe interno vaza ao cliente.
- Mudança incompatível para quem lia `detail` (registrada no CHANGELOG da v1.0.0).
