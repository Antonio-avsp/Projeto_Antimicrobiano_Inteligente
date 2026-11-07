# ADR 0002 — SQLite com SQLAlchemy 2.0

- **Situação:** Aceita
- **Data:** 05/11/2026
- **Versão:** v0.1.0
- **Issue:** #6

## Contexto

O projeto roda em máquinas de estudantes e avaliadores, sem servidor de banco, mas precisa de persistência relacional com integridade referencial (RNF02, RNF09).

## Decisão

Persistir em **SQLite** pelo ORM **SQLAlchemy 2.0**, com chaves estrangeiras habilitadas. A URL vem de `AMI_DATABASE_URL`.

## Alternativas consideradas

- **PostgreSQL:** exige instalar e configurar um servidor.
- **Arquivos JSON:** sem transações nem integridade referencial.

## Consequências

- Zero configuração (RNF06).
- Migrar para PostgreSQL é trocar a URL, porque o ORM gera SQL portável.
- Não há ferramenta de migração: mudanças de esquema exigem recriar a base (registrado no modelo de dados).
