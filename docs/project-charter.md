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
