# Termo de Abertura do Projeto (Project Charter)

| Campo | Informação |
|---|---|
| **Projeto** | Antimicrobiano Inteligente — API de apoio ao gerenciamento do uso de antimicrobianos |
| **Gerente do projeto e desenvolvedor** | Antonio-avsp |
| **Patrocinador acadêmico** | Docente da disciplina (atividade "Especificação, Gestão com Issues e SDLC no GitHub") |
| **Data de abertura** | 05/11/2026 |
| **Versão do documento** | 1.0 |
| **Issue de origem** | [#1](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/1) |

> ⚠️ **Aviso:** projeto acadêmico. O software é uma ferramenta de **apoio à decisão** e não substitui o julgamento clínico. Todos os dados utilizados são fictícios.

---

## 1. Justificativa

### 1.1 Contexto

A **resistência antimicrobiana (RAM)** é uma das principais ameaças à saúde pública mundial. O estudo *Global Research on Antimicrobial Resistance* (Murray et al., *The Lancet*, 2022) estimou **1,27 milhão de mortes diretamente atribuíveis** a bactérias resistentes em 2019. O uso inadequado de antimicrobianos é o principal motor desse fenômeno: estudos citados pelo CDC indicam que **30% a 50% das prescrições hospitalares** de antimicrobianos são desnecessárias ou inadequadas (indicação, escolha, dose ou duração).

Para enfrentar o problema, a ANVISA orienta que os serviços de saúde mantenham um **Programa de Gerenciamento do Uso de Antimicrobianos (PGA)** — conhecido internacionalmente como *antimicrobial stewardship* — conduzido por uma equipe multiprofissional (farmacêutico clínico, médico infectologista, microbiologista e membros da CCIH/SCIH).

### 1.2 Problema

Em hospitais de pequeno e médio porte, o acompanhamento do PGA costuma ser feito **manualmente**, com planilhas e revisão diária de prontuários. Isso gera:

- **Atraso nas intervenções:** tratamentos ultrapassam 72 horas sem reavaliação (*time-out*) ou excedem a duração prevista sem que a equipe perceba.
- **Terapias inadequadas não detectadas:** o microrganismo isolado é resistente ao antimicrobiano em uso, mas o cruzamento entre antibiograma e prescrição depende de busca manual.
- **Oportunidades perdidas de descalonamento:** o paciente continua com antimicrobiano de amplo espectro mesmo quando o antibiograma permite uma opção de menor espectro.
- **Baixa padronização e rastreabilidade:** critérios variam entre profissionais e as intervenções não ficam registradas de forma estruturada.

### 1.3 Visão geral do produto

> **Para** equipes de PGA/SCIH de hospitais de pequeno e médio porte, **que** acompanham manualmente as prescrições de antimicrobianos, o **Antimicrobiano Inteligente** é uma **API REST de apoio à decisão** que centraliza prescrições, culturas e antibiogramas e **gera automaticamente alertas explicáveis** (time-out, duração, restrição, resistência e descalonamento). **Diferentemente** das planilhas e da revisão manual, o produto aplica regras baseadas em diretrizes reconhecidas (OMS AWaRe, ANVISA, IDSA/SHEA e CLSI) de forma padronizada, rastreável e auditável.

A "inteligência" desta versão é um **sistema especialista baseado em regras**: cada alerta informa a regra aplicada, a severidade, as evidências utilizadas e a recomendação de conduta. Modelos preditivos (aprendizado de máquina) ficam para trabalhos futuros, quando houver dados reais e validados.

---

## 2. Objetivos SMART do software

Cada objetivo é **E**specífico, **M**ensurável, **A**tingível, **R**elevante e **T**emporal. O prazo da primeira iteração é **07/11/2026**.

| ID | Objetivo | Métrica de verificação | Meta | Prazo |
|---|---|---|---|---|
| **OBJ-01** | Implementar o motor de regras com os alertas de time-out, duração excedida, profilaxia prolongada, uso restrito sem justificativa, ausência de cultura, resistência e descalonamento. | Quantidade de regras com testes automatizados de cenários positivos e negativos | **7 regras** | 07/11/2026 (v0.3.0) |
| **OBJ-02** | Garantir a qualidade do código da aplicação com testes automatizados. | Cobertura de linhas medida pelo `pytest-cov` | **≥ 80%** | 07/11/2026 |
| **OBJ-03** | Gerar o painel de alertas com desempenho adequado ao uso diário. | Tempo de resposta de `GET /alertas` com 1.000 prescrições ativas, medido por teste automatizado em ambiente local | **≤ 2 s** | 07/11/2026 |
| **OBJ-04** | Manter a rastreabilidade completa entre especificação, backlog e código. | % dos RFs do MVP (RF01–RF14) ligados a caso de uso, história de usuário, issue e teste na matriz de rastreabilidade | **100%** | 07/11/2026 |
| **OBJ-05** | Seguir um fluxo de engenharia profissional. | % de mudanças integradas via Pull Request a partir de branches por issue com Conventional Commits; versões SemVer anotadas publicadas | **100%** e **3 tags** (v0.1.0, v0.2.0, v0.3.0) | 07/11/2026 |

**Relevância:** OBJ-01 ataca diretamente os problemas descritos na seção 1.2; OBJ-02 e OBJ-03 reduzem o risco de alertas incorretos ou lentos (que levam a equipe a ignorá-los); OBJ-04 e OBJ-05 atendem aos critérios de rastreabilidade e SDLC da disciplina.

---

## 3. Escopo preliminar

### 3.1 Dentro do escopo desta semana (iteração 1 — MVP, até 07/11/2026)

| Entrega | Descrição | Issues |
|---|---|---|
| Documentação de planejamento | Termo de abertura, requisitos, casos de uso, histórias de usuário, arquitetura, modelo de dados e rastreabilidade | #1 a #5 |
| Fundação técnica | Estrutura FastAPI + SQLite + pytest, pipeline de CI e README | #6 a #8 |
| Catálogo de antimicrobianos | Cadastro com classe, categoria AWaRe da OMS e indicação de uso restrito | #9 |
| Prescrições | Registro, consulta, atualização, reavaliação (*time-out*) e encerramento | #10, #11 |
| Microbiologia | Culturas, resultados e antibiogramas (S/I/R) | #12 |
| Motor de regras inteligente | 7 regras de alerta explicáveis e painel filtrável | #13 a #16 |
| Antibiograma cumulativo | Perfil local de sensibilidade (primeiro isolado por paciente) | #17 |
| Qualidade e demonstração | Parâmetros configuráveis e carga de dados fictícios | #18, #19 |

### 3.2 Entregas da iteração 2 (v1.0.0)

Itens planejados como fora do escopo da iteração 1 e priorizados pela Avaliação Técnica Week_01:

| Entrega | Descrição | Issues |
|---|---|---|
| Duplicidade terapêutica | 8ª regra do motor de alertas | [#22](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/22) |
| Indicadores de consumo | DOT por antimicrobiano, categoria AWaRe e setor, com percentual ACCESS | [#21](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/21) |
| Autenticação e perfis | Login com token JWT, permissões por perfil e autoria das intervenções | [#24](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/24) |
| Interface web | Painel de alertas em `/painel` | [#26](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/26) |
| Qualidade e segurança | Gates de lint, formatação, bandit e cobertura no CI; gitleaks, pip-audit e Dependabot | [#20](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/20), #64, #65 |
| Operação | Formato único de erro, logs JSON com identificador, `.env.example`, Docker e teste ponta a ponta | #58, #59, #60, #61, #63 |
| Documentação | Índice com regra de sincronização, decisões em ADRs e checklist de validação clínica | #66, #67, #68 |

### 3.3 Fora do escopo

- ❌ **Integração** com prontuário eletrônico, sistema hospitalar (HIS) ou laboratorial (LIS) — ex.: HL7/FHIR.
- ❌ **Dados reais de pacientes** — o sistema trabalha apenas com códigos pseudonimizados e dados fictícios.
- ❌ **DDD** (doses diárias definidas) e indicadores por paciente-dia, que exigem o censo de leitos.
- ❌ Login único corporativo (SSO/LDAP) e recuperação de senha por e-mail.
- ❌ Prescrição eletrônica, dispensação, ajuste de dose por função renal e interações medicamentosas.
- ❌ Modelos preditivos / aprendizado de máquina.
- ❌ Notificações (e-mail, SMS, aplicativos de mensagem), aplicativo móvel e operação multi-hospital.
- ❌ Regularização como *Software as a Medical Device* (RDC ANVISA nº 657/2022) e validação clínica para uso assistencial real.

---

## 4. Stakeholders e público-alvo

### 4.1 Stakeholders

| Stakeholder | Papel no projeto | Principal interesse | Influência | Comunicação |
|---|---|---|---|---|
| Docente da disciplina | Patrocinador acadêmico e avaliador | Qualidade da especificação, rastreabilidade e workflow | Alta | Entregas no Teams, repositório, issues e PRs |
| Antonio-avsp | Gerente do projeto e desenvolvedor | Entregar o MVP no prazo com qualidade | Alta | Issues, PRs, CHANGELOG |
| Coordenação do PGA / CCIH (cenário simulado) | Patrocinador de negócio | Reduzir uso inadequado de antimicrobianos e cumprir as diretrizes da ANVISA | Alta | Releases e relatórios |
| Farmacêutico clínico | Usuário principal | Triagem diária rápida das prescrições e registro das intervenções | Média | Painel de alertas |
| Médico infectologista | Usuário principal | Corrigir terapias inadequadas, descalonar e reavaliar tratamentos | Média | Painel de alertas |
| Analista do laboratório de microbiologia | Usuário | Registrar culturas e antibiogramas de forma estruturada | Baixa | API de culturas |
| Gestor da CCIH / qualidade | Usuário de relatórios | Perfil local de resistência (antibiograma cumulativo) e indicadores | Média | Relatórios |
| Corpo clínico prescritor | Afetado indireto | Receber recomendações claras e fundamentadas | Média | Intervenções do PGA |
| Pacientes | Beneficiários indiretos | Tratamento eficaz, seguro e pelo tempo adequado | Baixa | — |
| ANVISA / vigilância sanitária | Órgão regulador (contexto) | Conformidade com as diretrizes nacionais de PGA | Alta | Normas e diretrizes |

### 4.2 Público-alvo

- **Primário:** equipes multiprofissionais de PGA/SCIH de hospitais de pequeno e médio porte (até cerca de 200 leitos) que não possuem software dedicado ao *stewardship* e utilizam planilhas.
- **Secundário:** estudantes e docentes das áreas de saúde e tecnologia, como recurso didático sobre gerenciamento de antimicrobianos e engenharia de software.

---

## 5. Premissas, restrições e riscos

### 5.1 Premissas

- Os usuários da iteração 1 conseguem operar uma API REST pela documentação interativa (Swagger UI).
- As diretrizes clínicas são aplicadas de forma **simplificada** e parametrizável, adequada a um protótipo acadêmico.
- O desenvolvedor dispõe de aproximadamente 20 horas de trabalho na semana.

### 5.2 Restrições

- **Prazo:** entrega da atividade em 07/11/2026 às 23:59.
- **Equipe:** um único desenvolvedor.
- **Custo:** zero — somente ferramentas gratuitas e de código aberto (Python, FastAPI, SQLite, GitHub Free, GitHub Actions).
- **Infraestrutura:** execução local, sem servidores ou serviços pagos.
- **Processo:** Git Flow, Conventional Commits e Versionamento Semântico obrigatórios.

### 5.3 Riscos

| Risco | Probabilidade | Impacto | Resposta |
|---|---|---|---|
| Interpretação clínica equivocada dos alertas | Média | Alto | Aviso explícito de apoio à decisão; alertas com evidências e referências; revisão por especialista antes de qualquer uso real |
| Aumento de escopo (*scope creep*) | Alta | Médio | Priorização MoSCoW, lista explícita de itens fora do escopo e backlog de próximas iterações |
| Prazo curto (1 semana) | Alta | Alto | Entregas incrementais (v0.1.0 → v0.3.0) priorizando o MVP |
| Exposição de dados sensíveis | Baixa | Alto | Apenas códigos pseudonimizados e dados fictícios; `.env` ignorado pelo Git |
| Conhecimento limitado do domínio | Média | Médio | Glossário e referências (OMS, ANVISA, CLSI, IDSA/SHEA) |
| Fadiga de alertas (*alert fatigue*) | Média | Médio | Severidades, filtros no painel e parâmetros configuráveis |
| Acesso indevido aos dados (v1.0.0) | Média | Alto | Token JWT com expiração, perfis com permissões mínimas, senhas em hash scrypt e `AMI_JWT_SEGREDO` obrigatório fora do desenvolvimento |
| Dependências com vulnerabilidades (v1.0.0) | Média | Médio | pip-audit no CI e semanal, Dependabot e bandit |

> Matriz revisada no marco v1.0.0 (07/11/2026): incluídos os riscos de acesso e de dependências. A revisão por especialista das regras clínicas é acompanhada no [checklist de validação clínica](validacao-clinica.md) (#68).

---

## 6. Marcos (milestones) e versões

| Versão (SemVer) | Marco | Prazo | Issues |
|---|---|---|---|
| `v0.1.0` | Documentação de planejamento e fundação técnica (setup, CI, README) | 05/11/2026 | #1 a #8 |
| `v0.2.0` | Cadastros essenciais: catálogo, prescrições, reavaliação/encerramento e culturas | 06/11/2026 | #9 a #12 |
| `v0.3.0` | Motor de regras inteligente, painel de alertas, antibiograma cumulativo e dados de demonstração | 07/11/2026 | #13 a #19 |
| `v1.0.0` | Feedback da Avaliação Técnica Week_01: indicadores DOT, duplicidade terapêutica, autenticação, interface web, gates de qualidade e segurança, Docker e documentação operacional | 07/11/2026 | #20 a #26 e #58 a #68 |

## 7. Critérios de sucesso do projeto

- Todos os objetivos SMART da seção 2 atingidos no prazo.
- Ao menos 15 issues no backlog, com labels e critérios de aceite, todas rastreáveis aos requisitos.
- Nenhum commit direto em `main`; todas as integrações via Pull Request com referência à issue (`Closes #N`).

## 8. Aprovação

| Nome | Papel | Data |
|---|---|---|
| Antonio-avsp | Gerente do projeto | 05/11/2026 |

## Referências

- ANVISA. *Diretriz Nacional para Elaboração de Programa de Gerenciamento do Uso de Antimicrobianos em Serviços de Saúde*. Brasília, 2017.
- WHO. *The WHO AWaRe (Access, Watch, Reserve) antibiotic book*. Genebra, 2022.
- Barlam, T. F. et al. *Implementing an Antibiotic Stewardship Program: Guidelines by IDSA and SHEA*. Clinical Infectious Diseases, 2016.
- Murray, C. J. L. et al. *Global burden of bacterial antimicrobial resistance in 2019*. The Lancet, 2022.
- CLSI. *M39 — Analysis and Presentation of Cumulative Antimicrobial Susceptibility Test Data*.
