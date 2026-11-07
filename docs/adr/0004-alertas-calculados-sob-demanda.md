# ADR 0004 — Alertas calculados sob demanda

- **Situação:** Aceita
- **Data:** 06/11/2026
- **Versão:** v0.3.0
- **Issue:** #13

## Contexto

Um alerta deixa de valer quando a causa é resolvida (ex.: a reavaliação encerra o time-out). Guardar alertas exigiria sincronizá-los a cada mudança.

## Decisão

Calcular os alertas a cada `GET /alertas`, para a data de referência informada; nada é persistido.

## Alternativas consideradas

- **Persistir alertas em tabela:** risco de alertas desatualizados e necessidade de rotinas de limpeza.

## Consequências

- O painel sempre reflete o estado atual.
- Permite consultar uma data de referência passada.
- O custo cresce com o número de prescrições ativas; o RNF01 (1.000 prescrições em até 2 s) é verificado em teste.
