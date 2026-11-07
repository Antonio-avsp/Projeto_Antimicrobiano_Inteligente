# ADR 0001 — Python e FastAPI na API REST

- **Situação:** Aceita
- **Data:** 05/11/2026
- **Versão:** v0.1.0
- **Issue:** #6

## Contexto

A API precisa validar entradas com rigor (RNF05), gerar documentação interativa sem esforço extra (RNF03) e ser simples de testar, com uma equipe de uma pessoa e prazo de uma semana.

## Decisão

Usar **Python 3.11+** com **FastAPI**: os contratos são classes Pydantic, que validam a entrada e a saída e geram o OpenAPI (`/docs`, `/redoc`) automaticamente.

## Alternativas consideradas

- **Flask:** exigiria bibliotecas extras para validação e OpenAPI.
- **Django REST Framework:** estrutura maior que o necessário para o escopo.
- **Node.js/Express:** a validação e a documentação seriam montadas à mão.

## Consequências

- Documentação sempre igual ao código.
- Tipagem facilita os testes e a manutenção.
- Dependência do ecossistema FastAPI/Starlette, acompanhada pelo Dependabot.
