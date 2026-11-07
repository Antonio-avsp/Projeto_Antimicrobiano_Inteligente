# Documentação do Antimicrobiano Inteligente

Índice dos documentos de engenharia, com a versão do produto em que cada um foi revisado pela última vez. A versão atual do software está no [CHANGELOG](../CHANGELOG.md).

## Índice

| Documento | Conteúdo | Revisado na versão | Data |
|---|---|---|---|
| [Termo de Abertura](project-charter.md) | Justificativa, visão, objetivos SMART, escopo, stakeholders, riscos e marcos | v1.0.0 | 07/11/2026 |
| [Requisitos](requisitos.md) | Requisitos funcionais (RF), não funcionais (RNF) e regras de negócio (RN) | v1.0.0 | 07/11/2026 |
| [Glossário](glossario.md) | Termos do domínio usados no código e nos documentos | v1.0.0 | 07/11/2026 |
| [Casos de Uso](casos-de-uso.md) | Atores, diagrama e fluxos principal, alternativos e de exceção (UC01–UC08) | v1.0.0 | 07/11/2026 |
| [Histórias de Usuário](user-stories.md) | Histórias US01–US18 e HT01 com critérios de aceite em Gherkin | v1.0.0 | 07/11/2026 |
| [Arquitetura](arquitetura.md) | Modelo C4, camadas, motor de regras, autenticação, rotas da API e formato de erro | v1.0.0 | 07/11/2026 |
| [Modelo de Dados](modelo-de-dados.md) | DER, dicionário de dados, diagrama de classes e enumerações | v1.0.0 | 07/11/2026 |
| [Rastreabilidade](rastreabilidade.md) | Matriz requisito → caso de uso → história → regra → issue → release → teste | v1.0.0 | 07/11/2026 |

Fora desta pasta: [README](../README.md) (visão geral, execução e exemplos), [Guia de Contribuição](../CONTRIBUTING.md) (Git Flow, commits, PRs e Definição de Pronto) e [CHANGELOG](../CHANGELOG.md).

## Regra de sincronização documentação × código

A documentação é atualizada **no mesmo pull request** que muda o comportamento ou o escopo — nunca depois.

| Quando o PR… | Atualize também |
|---|---|
| cria ou altera um requisito, uma regra de negócio ou um parâmetro clínico | `requisitos.md`, `rastreabilidade.md` (com os testes que o verificam) e o quadro de funcionalidades do README |
| cria ou altera uma rota, um campo de entrada/saída ou o formato de erro | tabela de rotas em `arquitetura.md`, exemplos do README e, se mudar um fluxo, `casos-de-uso.md` |
| altera tabelas, colunas ou enumerações | `modelo-de-dados.md` |
| toma uma decisão de arquitetura (biblioteca, padrão, infraestrutura) | `arquitetura.md` (seção de decisões) |
| introduz um termo novo do domínio | `glossario.md` |
| muda a forma de instalar, configurar ou executar | README e `.env.example` |
| muda o escopo, os riscos ou os marcos | `project-charter.md` |

Ao revisar um documento, atualize a versão e a data no índice acima. O checklist do [template de PR](../.github/pull_request_template.md) inclui esta verificação, e o teste `tests/test_documentacao.py` falha no CI se um documento desta pasta ficar fora do índice ou se um requisito funcional não aparecer na matriz de rastreabilidade.
