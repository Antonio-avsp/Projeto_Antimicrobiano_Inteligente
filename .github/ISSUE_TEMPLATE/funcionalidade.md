---
name: Funcionalidade
about: Nova funcionalidade derivada de um requisito e de uma história de usuário
title: "feat: "
labels: feature
---

## Descrição

**História USxx** — Como [ator], quero [ação] para que [valor de negócio].

## Critérios de aceite

```gherkin
# language: pt
Cenário: 
  Dado 
  Quando 
  Então 
```

## Rastreabilidade
- Requisitos: RFxx, RNxx
- Caso de uso: UCxx · História: USxx
- Release alvo: `vX.Y.Z`

## Definição de pronto
- [ ] Branch `feature/issue-NN-descricao` a partir de `develop`
- [ ] Testes automatizados cobrindo todos os cenários
- [ ] README e matriz de rastreabilidade atualizados
- [ ] Pull Request para `develop` com `Closes #NN`
