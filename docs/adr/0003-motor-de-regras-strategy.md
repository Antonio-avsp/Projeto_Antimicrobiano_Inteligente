# ADR 0003 — Motor de regras próprio no padrão Strategy

- **Situação:** Aceita
- **Data:** 06/11/2026
- **Versão:** v0.3.0
- **Issue:** #13

## Contexto

As regras clínicas do PGA mudam e crescem (a v1.0.0 incluiu a duplicidade terapêutica) e cada alerta precisa explicar o porquê (RNF10).

## Decisão

Cada regra é uma classe que herda de `Regra` e devolve alertas com mensagem, recomendação e evidências. O `MotorDeRegras` aplica todas às prescrições ativas usando um `ContextoAvaliacao` pré-carregado, sem acessar o banco.

## Alternativas consideradas

- **Motor de regras de terceiros:** curva de aprendizado e regras menos legíveis.
- **Aprendizado de máquina:** não há dados reais para treinar e o resultado não seria explicável.

## Consequências

- Regra nova sem alterar as existentes (aberto/fechado — RNF07).
- Regras testadas isoladamente, sem banco (RNF08).
- Os dados do contexto precisam ser carregados antes; cada nova regra pode exigir um campo novo no contexto.
