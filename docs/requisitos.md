# Especificação de Requisitos

Documento de requisitos do **Antimicrobiano Inteligente**. Os termos do domínio estão definidos no [Glossário](glossario.md).

**Convenções**

- Identificadores únicos e estáveis: `RFxx` (funcional), `RNFxx` (não funcional) e `RNxx` (regra de negócio). Um identificador nunca é reutilizado.
- **Prioridade (MoSCoW):** *Must* (obrigatório no MVP), *Should* (importante), *Could* (desejável), *Won't* (não nesta versão).
- **Release alvo:** versão SemVer em que o requisito é entregue. A situação atual de cada requisito está no [README](../README.md#funcionalidades) e na [matriz de rastreabilidade](rastreabilidade.md).

---

## 1. Requisitos Funcionais (RF)

### 1.1 Catálogo de antimicrobianos

| ID | Requisito | Prioridade | Release | Issue |
|---|---|---|---|---|
| **[RF01]** | O sistema deve permitir **cadastrar antimicrobianos** informando nome, classe farmacológica, categoria AWaRe (`ACCESS`, `WATCH` ou `RESERVE`) e se o uso é restrito. | Must | v0.2.0 | [#9](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/9) |
| **[RF02]** | O sistema deve permitir **listar** antimicrobianos com filtros (categoria AWaRe, uso restrito, situação e busca por nome), **consultar**, **atualizar** e **inativar** itens do catálogo. | Must | v0.2.0 | [#9](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/9) |

### 1.2 Prescrições

| ID | Requisito | Prioridade | Release | Issue |
|---|---|---|---|---|
| **[RF03]** | O sistema deve permitir **registrar a prescrição** de um antimicrobiano para um paciente pseudonimizado, com setor, dose, intervalo entre doses, via, indicação, diagnóstico, data de início, duração prevista e justificativa. | Must | v0.2.0 | [#10](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/10) |
| **[RF04]** | O sistema deve permitir **listar** prescrições com filtros (status, setor e paciente), **consultar** seus detalhes (incluindo o dia de terapia) e **atualizar** prescrições ativas (setor, dose, intervalo, via, duração prevista e justificativa). | Must | v0.2.0 | [#10](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/10) |
| **[RF05]** | O sistema deve permitir **registrar reavaliações** (*time-out*) com conduta e observação e **encerrar prescrições** como concluídas ou suspensas, com data de término e motivo. | Must | v0.2.0 | [#11](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/11) |

### 1.3 Microbiologia

| ID | Requisito | Prioridade | Release | Issue |
|---|---|---|---|---|
| **[RF06]** | O sistema deve permitir **registrar a coleta de culturas** (paciente, setor, material e data), **registrar o resultado** (positiva com microrganismo e antibiograma S/I/R, ou negativa) e **listar culturas** por paciente e status. | Must | v0.2.0 | [#12](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/12) |

### 1.4 Motor de regras (alertas inteligentes)

| ID | Requisito | Prioridade | Release | Issue |
|---|---|---|---|---|
| **[RF07]** | O sistema deve gerar alerta de **time-out** para prescrições ativas há 72 horas ou mais sem reavaliação registrada. | Must | v0.3.0 | [#13](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/13) |
| **[RF08]** | O sistema deve gerar alertas de **duração excedida** (dia de terapia maior que a duração prevista) e de **profilaxia prolongada** (profilaxia planejada por mais de 24 horas). | Must | v0.3.0 | [#13](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/13) |
| **[RF09]** | O sistema deve gerar alerta para prescrição ativa de antimicrobiano de **uso restrito sem justificativa**. | Must | v0.3.0 | [#14](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/14) |
| **[RF10]** | O sistema deve gerar alerta de **resistência** quando uma cultura relevante do paciente indicar microrganismo resistente (`R`) ao antimicrobiano prescrito, sugerindo alternativas sensíveis. | Must | v0.3.0 | [#15](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/15) |
| **[RF11]** | O sistema deve **sugerir descalonamento** quando todas as culturas positivas relevantes indicarem sensibilidade (`S`) a antimicrobiano de categoria AWaRe inferior à do prescrito. | Should | v0.3.0 | [#15](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/15) |
| **[RF12]** | O sistema deve gerar alerta quando antimicrobiano `WATCH` ou `RESERVE` for prescrito com indicação **empírica sem cultura** coletada na janela de relevância. | Should | v0.3.0 | [#14](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/14) |
| **[RF13]** | O sistema deve disponibilizar o **painel de alertas** de uma data de referência, ordenado por severidade, com filtros (tipo, severidade, setor e paciente) e resumo de quantidades por severidade e por tipo. | Must | v0.3.0 | [#13](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/13), [#16](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/16) |
| **[RF14]** | O sistema deve gerar o **antibiograma cumulativo** de um período (com filtro opcional por setor), contando o primeiro isolado por paciente e sinalizando combinações com menos de 30 isolados. | Should | v0.3.0 | [#17](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/17) |

### 1.5 Planejados para a iteração 2

| ID | Requisito | Prioridade | Release | Issue |
|---|---|---|---|---|
| **[RF15]** | O sistema deve calcular **indicadores de consumo** em dias de terapia (DOT) por antimicrobiano e por categoria AWaRe. | Could | v1.0.0 | [#21](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/21) |
| **[RF16]** | O sistema deve gerar alerta de **duplicidade terapêutica** (duas prescrições ativas da mesma classe para o mesmo paciente). | Could | v1.0.0 | [#22](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/22) |
| **[RF17]** | O sistema deve exigir **autenticação** e controlar o acesso por perfil (farmacêutico, infectologista, laboratório e gestor). | Should | v1.0.0 | [#24](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/24) |
| **[RF18]** | O sistema deve oferecer **interface web** para o painel de alertas. | Could | v1.0.0 | [#26](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/26) |

---

## 2. Requisitos Não Funcionais (RNF)

| ID | Categoria | Requisito | Critério de verificação |
|---|---|---|---|
| **[RNF01]** | Desempenho | O painel de alertas deve responder em até **2 s** com **1.000 prescrições ativas**; operações de cadastro e consulta em até 500 ms, em ambiente local. | Teste automatizado de desempenho (#16) |
| **[RNF02]** | Persistência | Os dados devem ser persistidos em banco relacional **SQLite** via ORM **SQLAlchemy**, sobrevivendo a reinicializações. A troca de SGBD (ex.: PostgreSQL) deve exigir apenas a alteração da variável `AMI_DATABASE_URL`. | Inspeção da configuração e testes (#6) |
| **[RNF03]** | Usabilidade | A API deve ser documentada automaticamente (OpenAPI) em `/docs` e `/redoc`; recursos, campos e mensagens de erro de negócio devem estar em português; respostas em JSON padronizado. | Inspeção e testes de API (#6, #8) |
| **[RNF04]** | Privacidade (LGPD) | O sistema não deve armazenar dados pessoais identificáveis: o paciente é referenciado exclusivamente por **código pseudonimizado** (`PAC-` + 4 a 10 dígitos) e somente dados fictícios são utilizados. | Teste de validação do código do paciente (#10, #19) |
| **[RNF05]** | Segurança | Validação estrita das entradas (Pydantic), consultas parametrizadas via ORM (prevenção de *SQL injection*) e nenhum segredo versionado (`.env` ignorado). Autenticação planejada no RF17. | Testes de validação e revisão de PR (#6, #24) |
| **[RNF06]** | Portabilidade | Executar em Windows, Linux e macOS com **Python 3.11 ou superior**, sem dependência de serviços externos. | Pipeline de CI em Python 3.11, 3.12 e 3.13 (#7) |
| **[RNF07]** | Manutenibilidade | Arquitetura em camadas (rotas → serviços → modelos) e motor de regras extensível: uma nova regra é uma nova classe, sem alterar as existentes (princípio aberto/fechado). Código no padrão PEP 8 (ruff). | Revisão de PR e ruff (#13, #18, #20) |
| **[RNF08]** | Testabilidade | Cobertura de testes automatizados **≥ 80%**; regras testáveis isoladamente, com data de referência injetável. | `pytest --cov` (#6, #20) |
| **[RNF09]** | Integridade | Integridade referencial entre entidades; antimicrobianos nunca são excluídos fisicamente (inativação lógica); registros com data de criação e de atualização. | Testes de API (#9) |
| **[RNF10]** | Transparência clínica | Cada alerta deve informar tipo, severidade, mensagem, recomendação e as **evidências** usadas pela regra; a API deve exibir aviso de que o sistema é apoio à decisão e não substitui o julgamento clínico. | Testes do painel (#13, #16) |
| **[RNF11]** | Configurabilidade | Os parâmetros clínicos das regras (time-out, limite de profilaxia, janela de culturas e mínimo de isolados) devem ser configuráveis por variáveis de ambiente, com validação dos valores. | Testes de configuração (#18) |
| **[RNF12]** | Processo (organizacional) | O versionamento deve seguir **Git Flow**, **Conventional Commits** e **SemVer**; toda mudança deve entrar via Pull Request com referência à issue; o CHANGELOG deve ser atualizado a cada release. | Histórico do Git e PRs (todas as issues) |
