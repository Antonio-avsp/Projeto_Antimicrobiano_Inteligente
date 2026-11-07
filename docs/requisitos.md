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

---

## 3. Regras de Negócio (RN)

### 3.1 Catálogo

| ID | Regra |
|---|---|
| **[RN01]** | O nome do antimicrobiano é **único**, comparado sem diferenciar maiúsculas/minúsculas, acentos e espaços extras (`Ceftriaxona` = `CEFTRIAXONA` = ` ceftriaxona `). |
| **[RN02]** | Antimicrobiano **inativo** continua consultável e presente nos históricos, mas não pode ser usado em novas prescrições. |
| **[RN03]** | A exclusão de antimicrobiano é sempre **lógica** (inativação), preservando o histórico de prescrições e antibiogramas. |

### 3.2 Prescrições

| ID | Regra |
|---|---|
| **[RN04]** | O paciente é identificado apenas pelo código pseudonimizado no formato `PAC-` seguido de 4 a 10 dígitos (ex.: `PAC-0001`). |
| **[RN05]** | A data de início da prescrição não pode ser posterior à data atual. |
| **[RN06]** | A duração prevista deve estar entre **1 e 90 dias** e o intervalo entre doses entre **1 e 168 horas**. |
| **[RN07]** | Antimicrobiano de uso restrito deve ter justificativa. A ausência **não bloqueia** o registro (o sistema é de monitoramento), mas gera o alerta da RN15. |
| **[RN08]** | Prescrição encerrada (`CONCLUIDA` ou `SUSPENSA`) não pode ser atualizada, reavaliada ou encerrada novamente. |
| **[RN09]** | As datas de reavaliação e de término devem estar entre a data de início da prescrição e a data atual. |

### 3.3 Microbiologia

| ID | Regra |
|---|---|
| **[RN10]** | A data de coleta não pode ser futura. Cultura `POSITIVA` exige microrganismo; o antibiograma só é aceito em cultura positiva, com cada antimicrobiano no máximo uma vez e interpretação `S`, `I` ou `R`. Cultura `NEGATIVA` não possui microrganismo nem antibiograma. A data do resultado deve estar entre a data de coleta e a data atual. |

### 3.4 Motor de alertas

| ID | Regra |
|---|---|
| **[RN11]** | As regras são avaliadas somente para prescrições `ATIVA`, em uma **data de referência** (padrão: hoje). **Dia de terapia** = (data de referência − data de início) + 1. Uma cultura é **relevante** para a prescrição quando pertence ao mesmo paciente e foi coletada entre 7 dias antes do início da terapia e a data de referência. |

Cada regra a seguir gera um alerta com tipo, severidade, mensagem, recomendação e evidências (RNF10):

| ID | Tipo do alerta | Severidade | Condição de disparo | Recomendação |
|---|---|---|---|---|
| **[RN12]** | `TIMEOUT_REAVALIACAO` | MEDIA | (data de referência − data de início) ≥ **3 dias (72 h)** e nenhuma reavaliação registrada. | Realizar o time-out: confirmar o diagnóstico, revisar culturas e definir a conduta (manter, ajustar, descalonar ou suspender). |
| **[RN13]** | `DURACAO_EXCEDIDA` | MEDIA | Dia de terapia **maior** que a duração prevista. | Avaliar a suspensão ou registrar nova duração justificada. |
| **[RN14]** | `PROFILAXIA_PROLONGADA` | MEDIA | Indicação `PROFILAXIA` e duração prevista **maior que 1 dia (24 h)**. | Suspender a profilaxia em até 24 horas após o procedimento, salvo exceção justificada. |
| **[RN15]** | `RESTRITO_SEM_JUSTIFICATIVA` | ALTA | Antimicrobiano de uso restrito e justificativa vazia. | Registrar a justificativa clínica e solicitar validação do PGA. |
| **[RN16]** | `SEM_CULTURA` | MEDIA | Indicação `EMPIRICA`, antimicrobiano `WATCH` ou `RESERVE` e **nenhuma cultura relevante** do paciente. | Coletar culturas pertinentes ao sítio de infecção, idealmente antes da próxima dose. |
| **[RN17]** | `RESISTENCIA` | ALTA | Existe cultura positiva relevante com interpretação **`R`** para o antimicrobiano prescrito. | Revisar a terapia. Alternativas: antimicrobianos ativos com `S` em todas as culturas positivas relevantes, ordenados por categoria AWaRe (ACCESS primeiro). |
| **[RN18]** | `DESCALONAMENTO` | BAIXA | Antimicrobiano prescrito `WATCH` ou `RESERVE`, nenhuma cultura relevante com `R` para ele e ao menos um antimicrobiano ativo com `S` em **todas** as culturas positivas relevantes e de **categoria AWaRe inferior**. | Considerar o descalonamento para as opções listadas. |
| **[RN22]** | `DUPLICIDADE_TERAPEUTICA` | MEDIA | O paciente tem outra prescrição `ATIVA`, iniciada até a data de referência, de antimicrobiano da **mesma classe** (comparação sem diferenciar maiúsculas e acentos). Um alerta para cada prescrição envolvida, mesmo que estejam em setores diferentes. | Manter apenas um antimicrobiano da classe, salvo indicação documentada (ex.: transição IV → VO, que exige suspender a via anterior). |

### 3.5 Relatórios e apresentação

| ID | Regra |
|---|---|
| **[RN19]** | **Antibiograma cumulativo:** considera culturas `POSITIVA` coletadas no período (e setor, se informado); conta apenas o **primeiro isolado** (coleta mais antiga) por paciente e microrganismo, comparando o nome do microrganismo sem diferenciar maiúsculas/minúsculas; percentual de sensibilidade = `S` ÷ testados × 100 (uma casa decimal); combinações com **menos de 30 isolados** testados recebem `amostra_suficiente = false` (CLSI M39). |
| **[RN20]** | **Hierarquia AWaRe** usada nas comparações: `ACCESS` (1) < `WATCH` (2) < `RESERVE` (3). |
| **[RN23]** | **Indicadores de consumo (DOT):** cada dia de calendário em que o paciente recebeu o antimicrobiano conta 1 dia de terapia, independentemente do número de doses. Contam os dias entre o início e o término da prescrição (ou hoje, se ainda `ATIVA`) que caem no período (padrão: últimos 30 dias); o mesmo antimicrobiano para o mesmo paciente no mesmo dia conta uma vez. Percentual ACCESS = DOT `ACCESS` ÷ DOT total × 100 (uma casa decimal), comparado à meta de **60%** da OMS. Exemplo de cálculo manual (período D1–D7): PAC-0001 com Ceftriaxona de D1 a D5 = 5; PAC-0002 com Amoxicilina de D0 a D3 = 3 (D0 fica fora); PAC-0003 com Ceftriaxona ativa desde D6 = 2 e Gentamicina ativa desde D7 = 1 → total 11 DOT, ACCESS 4 (36,4%), WATCH 7. |
| **[RN21]** | **Severidades:** `ALTA` = ação imediata; `MEDIA` = ação em até 24 horas; `BAIXA` = oportunidade de otimização. O painel ordena os alertas de `ALTA` para `BAIXA`, depois por tipo e por prescrição. |

> Os limites de 3 dias, 1 dia, 7 dias e 30 isolados são **parâmetros clínicos** configuráveis (RNF11), pois variam entre protocolos institucionais.
