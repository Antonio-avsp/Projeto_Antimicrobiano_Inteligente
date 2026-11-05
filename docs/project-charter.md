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

### 3.2 Fora do escopo (expressamente excluído desta semana)

- ❌ **Integração** com prontuário eletrônico, sistema hospitalar (HIS) ou laboratorial (LIS) — ex.: HL7/FHIR.
- ❌ **Dados reais de pacientes** — o sistema trabalha apenas com códigos pseudonimizados e dados fictícios.
- ❌ **Autenticação e perfis de acesso** — planejado para a v1.0.0 ([#24](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/24)).
- ❌ **Interface web** — nesta iteração a API é operada pelo Swagger UI; painel web planejado ([#26](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/26)).
- ❌ **Indicadores de consumo** (DOT/DDD) e **alerta de duplicidade terapêutica** — planejados ([#21](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/21), [#22](https://github.com/Antonio-avsp/Projeto_Antimicrobiano_Inteligente/issues/22)).
- ❌ Prescrição eletrônica, dispensação, ajuste de dose por função renal e interações medicamentosas.
- ❌ Modelos preditivos / aprendizado de máquina.
- ❌ Notificações (e-mail, SMS, aplicativos de mensagem), aplicativo móvel e operação multi-hospital.
- ❌ Regularização como *Software as a Medical Device* (RDC ANVISA nº 657/2022) e validação clínica para uso assistencial real.
