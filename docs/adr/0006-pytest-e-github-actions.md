# ADR 0006 — pytest e GitHub Actions com gates de qualidade

- **Situação:** Aceita
- **Data:** 05/11/2026
- **Versão:** v0.1.0 (gates na v1.0.0)
- **Issue:** #7, #20

## Contexto

Cada mudança precisa ser verificada automaticamente em várias versões do Python (RNF06, RNF08) e o código deve manter um padrão (RNF07).

## Decisão

Testes com **pytest** e **pytest-cov** executados no **GitHub Actions** em Python 3.11, 3.12 e 3.13. Na v1.0.0, o CI passou a bloquear o PR se `ruff check`, `ruff format --check` ou `bandit` falharem ou se a cobertura ficar abaixo de 80%, e publica o relatório de cobertura como artefato.

## Alternativas consideradas

- **unittest:** mais verboso e sem o ecossistema de plugins.
- **Outros serviços de CI:** configuração externa ao repositório.

## Consequências

- Gratuito e integrado aos PRs.
- A qualidade mínima não depende da disciplina individual.
- O CI fica mais longo; os jobs rodam em paralelo para compensar.
