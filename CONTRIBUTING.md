# Guia de Contribuição

Este guia descreve o fluxo de engenharia adotado no **Antimicrobiano Inteligente**: Git Flow, commits atômicos com Conventional Commits, Pull Requests rastreáveis e Versionamento Semântico.

## 1. Ambiente de desenvolvimento

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
pytest              # testes automatizados
ruff check .        # análise estática
```

## 2. Fluxo de branches (Git Flow)

| Branch | Criada a partir de | Integra em | Finalidade |
|---|---|---|---|
| `main` | — | — | Produção: contém apenas versões liberadas e marcadas com tag `vX.Y.Z`. **Nunca recebe commits diretos.** |
| `develop` | `main` | — | Integração das funcionalidades da próxima versão. |
| `feature/issue-NN-descricao` | `develop` | `develop` (via PR) | Uma branch por issue (funcionalidade, documentação, configuração ou refatoração). |
| `bugfix/issue-NN-descricao` | `develop` | `develop` (via PR) | Correção de defeito ainda não liberado ou não urgente (entra na próxima versão). |
| `release/vX.Y.Z` | `develop` | `main` (via PR) e `develop` | Preparação da versão: número de versão, CHANGELOG e ajustes finais. |
| `hotfix/vX.Y.Z` | `main` | `main` (via PR) e `develop` | Correção urgente de defeito em produção. |

### Passo a passo para resolver uma issue

```bash
git switch develop
git pull origin develop
git switch -c feature/issue-09-catalogo-antimicrobianos
# ... desenvolvimento com commits atômicos ...
git push -u origin feature/issue-09-catalogo-antimicrobianos
```

Em seguida, abra um Pull Request para `develop` usando o template do repositório e incluindo `Closes #9` na descrição.

## 3. Commits — Conventional Commits

Formato: `<tipo>(<escopo opcional>): <descrição no imperativo> (#issue)`

| Tipo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade |
| `fix` | Correção de defeito |
| `docs` | Documentação |
| `test` | Inclusão ou ajuste de testes |
| `refactor` | Mudança interna sem alterar comportamento |
| `chore` | Configuração, dependências e tarefas de manutenção |
| `ci` | Pipeline de integração contínua |
| `perf` | Melhoria de desempenho |

Exemplos:

```text
feat(prescricoes): validar código pseudonimizado do paciente (#10)
docs(requisitos): especificar requisitos não funcionais RNF01 a RNF12 (#2)
refactor(regras): injetar parâmetros clínicos no motor (#18)
```

**Commits atômicos:** cada commit contém **uma** mudança lógica completa, com os testes passando. Prefira vários commits pequenos a um commit grande.

## 4. Pull Requests

- Base: `develop` para branches `feature/*`; `main` para `release/*` e `hotfix/*`.
- Título no padrão Conventional Commits; descrição com `Closes #N`.
- O pipeline de CI deve estar verde.
- Merge com *merge commit* (`--no-ff`), preservando os commits atômicos e a topologia do Git Flow.

> **Fechamento automático de issues:** o GitHub só interpreta `Closes #N` em PRs cuja base é a branch padrão (`main`). Por isso, os PRs de feature para `develop` registram a referência (rastreabilidade) e o PR de release `release/vX.Y.Z → main` lista `Closes #N` de todas as issues da versão, fechando-as no momento em que chegam à produção.

## 5. Versionamento Semântico (SemVer)

- Formato `MAJOR.MINOR.PATCH`: MAJOR para mudanças incompatíveis na API, MINOR para funcionalidades compatíveis e PATCH para correções.
- Enquanto `MAJOR = 0`, o projeto está em desenvolvimento inicial e a API pode mudar.
- Cada release recebe uma **tag anotada** na `main`. A tag é criada **automaticamente** pelo workflow [`tag-versao.yml`](.github/workflows/tag-versao.yml) quando a branch `release/*` ou `hotfix/*` é integrada: ele lê a versão de `src/antimicrobiano/__init__.py` e usa as notas da versão no CHANGELOG como mensagem da tag.
- Para marcar manualmente uma versão anterior, execute o workflow *Tag de versão* (aba **Actions → Run workflow**) informando a versão e o commit. Localmente, o equivalente é:

```bash
git tag -a v0.2.0 <commit-do-merge> -m "v0.2.0 — Cadastros essenciais"
git push origin v0.2.0
```

- As mudanças de cada versão são registradas no [CHANGELOG](CHANGELOG.md), no formato *Keep a Changelog*.

## 6. Definição de Pronto (DoD)

- [ ] Critérios de aceite da issue atendidos
- [ ] Testes automatizados cobrindo os cenários Gherkin da história
- [ ] `pytest` e `ruff check .` sem erros
- [ ] README e documentação em `docs/` atualizados (incluindo a matriz de rastreabilidade)
- [ ] PR mesclado em `develop` com referência à issue
