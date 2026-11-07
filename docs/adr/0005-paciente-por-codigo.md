# ADR 0005 — Paciente identificado apenas por código

- **Situação:** Aceita
- **Data:** 05/11/2026
- **Versão:** v0.2.0
- **Issue:** #10

## Contexto

A LGPD exige minimizar dados pessoais de saúde (RNF04), e o projeto não deve armazenar dados reais.

## Decisão

O paciente é referenciado somente por um código pseudonimizado (`PAC-` + 4 a 10 dígitos), validado na entrada; não existe cadastro de pacientes.

## Alternativas consideradas

- **Cadastro de pacientes com nome e documento:** dado pessoal sensível sem necessidade para as regras.

## Consequências

- Nenhum dado pessoal identificável na base.
- A identificação real fica no prontuário de origem.
- A integração futura com prontuário precisa de uma tabela de correspondência fora deste sistema.
