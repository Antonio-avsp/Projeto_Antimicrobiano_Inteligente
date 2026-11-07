# Matriz de Rastreabilidade

Liga cada requisito à sua origem e ao seu destino: **requisito → caso de uso → história de usuário → regra de negócio → issue → release → teste automatizado**. A coluna *Situação* é atualizada no mesmo Pull Request que implementa o requisito, mantendo a matriz sincronizada com o código.

Legenda: ✅ implementado · 🗓️ planejado

## 1. Requisitos funcionais

| RF | Descrição | UC | US | RN | Issue | Release | Testes automatizados | Situação |
|---|---|---|---|---|---|---|---|---|
| RF01 | Cadastrar antimicrobiano | UC01 | US01 | RN01 | [#9](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/9) | v0.2.0 | `tests/test_antimicrobianos.py` | ✅ |
| RF02 | Listar, consultar, atualizar e inativar antimicrobianos | UC01 | US02 | RN02, RN03 | [#9](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/9) | v0.2.0 | `tests/test_antimicrobianos.py` | ✅ |
| RF03 | Registrar prescrição | UC02 | US03 | RN02, RN04–RN07 | [#10](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/10) | v0.2.0 | `tests/test_prescricoes.py` | ✅ |
| RF04 | Listar, consultar e atualizar prescrições | UC02 | US04 | RN08 | [#10](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/10) | v0.2.0 | `tests/test_prescricoes.py` | ✅ |
| RF05 | Reavaliar (time-out) e encerrar prescrição | UC03 | US05 | RN08, RN09 | [#11](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/11) | v0.2.0 | `tests/test_intervencoes.py` | ✅ |
| RF06 | Registrar culturas e antibiogramas | UC04 | US06 | RN10 | [#12](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/12) | v0.2.0 | `tests/test_culturas.py` | ✅ |
| RF07 | Alerta de time-out de 72 horas | UC05 | US07 | RN11, RN12 | [#13](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/13) | v0.3.0 | `tests/regras/test_regras_temporais.py`, `tests/test_alertas.py` | ✅ |
| RF08 | Alertas de duração excedida e profilaxia prolongada | UC05 | US08 | RN13, RN14 | [#13](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/13) | v0.3.0 | `tests/regras/test_regras_temporais.py`, `tests/test_alertas.py` | ✅ |
| RF09 | Alerta de uso restrito sem justificativa | UC05 | US09 | RN15 | [#14](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/14) | v0.3.0 | `tests/regras/test_regras_politicas.py` | ✅ |
| RF10 | Alerta de resistência | UC05 | US10 | RN17, RN20 | [#15](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/15) | v0.3.0 | `tests/regras/test_regras_microbiologicas.py` | ✅ |
| RF11 | Sugestão de descalonamento | UC05 | US11 | RN18, RN20 | [#15](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/15) | v0.3.0 | `tests/regras/test_regras_microbiologicas.py` | ✅ |
| RF12 | Alerta de WATCH/RESERVE empírico sem cultura | UC05 | US12 | RN16 | [#14](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/14) | v0.3.0 | `tests/regras/test_regras_politicas.py` | ✅ |
| RF13 | Painel de alertas com filtros e resumo | UC05 | US13 | RN11, RN21 | [#13](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/13), [#16](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/16) | v0.3.0 | `tests/test_alertas.py`, `tests/test_desempenho.py` | ✅ |
| RF14 | Antibiograma cumulativo | UC06 | US14 | RN19 | [#17](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/17) | v0.3.0 | `tests/test_relatorios.py` | ✅ |
| RF15 | Indicadores de consumo (DOT) | UC07 | US15 | — | [#21](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/21) | v1.0.0 | — | 🗓️ |
| RF16 | Alerta de duplicidade terapêutica | UC05 | US16 | RN22 | [#22](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/22) | v1.0.0 | `tests/regras/test_regras_politicas.py`, `tests/test_alertas.py` | ✅ |
| RF17 | Autenticação e perfis de acesso | UC08 | US17 | — | [#24](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/24) | v1.0.0 | — | 🗓️ |
| RF18 | Interface web do painel | UC05 | US18 | — | [#26](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/26) | v1.0.0 | — | 🗓️ |

## 2. Requisitos não funcionais

| RNF | Categoria | Issues | Forma de verificação |
|---|---|---|---|
| RNF01 | Desempenho | #16 | `tests/test_desempenho.py` (1.000 prescrições ativas em até 2 s) |
| RNF02 | Persistência | #6 | Configuração `AMI_DATABASE_URL` e testes com banco em memória |
| RNF03 | Usabilidade | #6, #8 | OpenAPI em `/docs`; mensagens de erro em português nos testes de API |
| RNF04 | Privacidade (LGPD) | #10, #19 | Validação de `paciente_codigo` em `tests/test_prescricoes.py` e `tests/test_culturas.py`; seed apenas fictício |
| RNF05 | Segurança | #6, #24 | Testes de validação (422); `.gitignore`; revisão de PR |
| RNF06 | Portabilidade | #6, #7 | Pipeline de CI em Python 3.11, 3.12 e 3.13 |
| RNF07 | Manutenibilidade | #13, #18, #20 | Motor Strategy; ruff |
| RNF08 | Testabilidade | #6, #20 | `pytest --cov` (meta ≥ 80%) |
| RNF09 | Integridade | #9 | Testes de inativação lógica e chaves estrangeiras |
| RNF10 | Transparência clínica | #13, #16 | `tests/test_alertas.py` verifica mensagem, recomendação e evidências |
| RNF11 | Configurabilidade | #18 | `tests/test_config.py` |
| RNF12 | Processo | todas | Histórico do Git, PRs com `Closes #N`, tags SemVer e CHANGELOG |

## 3. Issues de suporte (documentação, configuração e qualidade)

| Issue | Tipo | Entregável | Release |
|---|---|---|---|
| [#1](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/1) | documentation | [`docs/project-charter.md`](project-charter.md) | v0.1.0 |
| [#2](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/2) | documentation | [`docs/requisitos.md`](requisitos.md), [`docs/glossario.md`](glossario.md) | v0.1.0 |
| [#3](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/3) | documentation | [`docs/casos-de-uso.md`](casos-de-uso.md) | v0.1.0 |
| [#4](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/4) | documentation | [`docs/user-stories.md`](user-stories.md) | v0.1.0 |
| [#5](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/5) | documentation | [`docs/arquitetura.md`](arquitetura.md), [`docs/modelo-de-dados.md`](modelo-de-dados.md), este documento | v0.1.0 |
| [#6](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/6) | chore | Estrutura `src/` e `tests/`, `pyproject.toml`, `.gitignore`, `LICENSE`, `CONTRIBUTING.md` | v0.1.0 |
| [#7](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/7) | ci | `.github/workflows/ci.yml` | v0.1.0 |
| [#8](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/8) | documentation | `README.md` | v0.1.0 |
| [#18](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/18) | refactor | `ParametrosClinicos` em `config.py` | v0.3.0 |
| [#19](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/19) | enhancement | `src/antimicrobiano/seed.py` | v0.3.0 |
| [#20](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/20) | ci, enhancement | Gates de qualidade no pipeline | v1.0.0 |

## 4. Objetivos SMART → evidências

| Objetivo ([Termo de Abertura](project-charter.md#2-objetivos-smart-do-software)) | Evidência |
|---|---|
| OBJ-01 — 7 regras de alerta testadas (8 com a duplicidade terapêutica da v1.0.0) | `src/antimicrobiano/regras/` e `tests/regras/` |
| OBJ-02 — cobertura ≥ 80% | Relatório do `pytest --cov` no CI |
| OBJ-03 — painel ≤ 2 s com 1.000 prescrições | `tests/test_desempenho.py` |
| OBJ-04 — 100% dos RFs do MVP rastreados | Seção 1 deste documento |
| OBJ-05 — fluxo profissional | PRs com `Closes #N`, Conventional Commits e tags `v0.1.0`, `v0.2.0`, `v0.3.0` |
