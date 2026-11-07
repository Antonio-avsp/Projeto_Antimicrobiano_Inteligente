# Validação Clínica das Regras

Checklist para a revisão das regras do motor de alertas e dos relatórios por um **especialista** (médico infectologista ou farmacêutico clínico do PGA) antes de qualquer uso assistencial. O software é uma ferramenta acadêmica de **apoio à decisão** e não substitui o julgamento clínico.

> **Situação:** nenhuma regra foi validada por especialista até a v1.0.0. As fontes abaixo fundamentam a especificação, mas **não equivalem à validação**. A issue correspondente só deve ser fechada depois do registro real da revisão.

## Como registrar a revisão

1. O revisor lê a regra em [requisitos.md](requisitos.md#3-regras-de-negócio-rn), a fonte indicada e o parâmetro em uso, e confere o alerta gerado pela carga de demonstração (`python -m antimicrobiano.seed` e `/painel`).
2. Responde às perguntas de verificação da regra.
3. Preenche **responsável** (nome e registro profissional — CRM ou CRF), **data** e **parecer**: `Aprovada`, `Aprovada com ajustes` ou `Reprovada`.
4. Cada ajuste pedido vira uma issue, vinculada nesta tabela, e a regra só passa a `Aprovada` depois do ajuste.
5. A revisão é feita em um pull request que altera este documento, para ficar registrada no histórico do Git.

## Regras do motor de alertas

| Regra | Alerta (severidade) | Parâmetro em uso | Fonte técnica | Perguntas de verificação | Responsável | Data | Parecer |
|---|---|---|---|---|---|---|---|
| RN12 | `TIMEOUT_REAVALIACAO` (MEDIA) | 3 dias sem reavaliação (`AMI_TIMEOUT_DIAS`) | Barlam et al., IDSA/SHEA 2016 (*antibiotic time-out*); ANVISA, Diretriz Nacional de PGA | O prazo de 72 h corresponde ao protocolo da instituição? A conduta registrada deve ser obrigatória? | — | — | Pendente |
| RN13 | `DURACAO_EXCEDIDA` (MEDIA) | Dia de terapia > duração prevista | Barlam et al., IDSA/SHEA 2016 (menor duração eficaz) | A duração prevista informada na prescrição é confiável como referência? | — | — | Pendente |
| RN14 | `PROFILAXIA_PROLONGADA` (MEDIA) | Profilaxia > 1 dia (`AMI_LIMITE_PROFILAXIA_DIAS`) | Bratzler et al., ASHP/IDSA/SIS/SHEA 2013 (profilaxia cirúrgica) | Há procedimentos com exceção aceita (ex.: cirurgia cardíaca) que devem ser tratados à parte? | — | — | Pendente |
| RN15 | `RESTRITO_SEM_JUSTIFICATIVA` (ALTA) | Antimicrobianos marcados como `uso_restrito` | Barlam et al., IDSA/SHEA 2016 (pré-autorização); ANVISA, Diretriz Nacional de PGA | A lista de restritos do catálogo de demonstração reflete a padronização da instituição? | — | — | Pendente |
| RN16 | `SEM_CULTURA` (MEDIA) | WATCH/RESERVE empírico sem cultura de 7 dias antes até a data (`AMI_JANELA_CULTURA_DIAS`) | Evans et al., Surviving Sepsis Campaign 2021; Barlam et al., IDSA/SHEA 2016 | A janela de 7 dias é adequada? Algum sítio de infecção dispensa cultura? | — | — | Pendente |
| RN17 | `RESISTENCIA` (ALTA) | Interpretação `R` em cultura relevante | BrCAST/EUCAST (pontos de corte) | As alternativas sugeridas (sensíveis em todas as culturas, ACCESS primeiro) são seguras sem avaliar sítio, alergias e função renal? | — | — | Pendente |
| RN18 | `DESCALONAMENTO` (BAIXA) | Opção de categoria AWaRe inferior sensível em todas as culturas | WHO, *The AWaRe antibiotic book*, 2022; Barlam et al., IDSA/SHEA 2016 | A hierarquia AWaRe é critério suficiente ou é preciso considerar o espectro dentro da mesma categoria? | — | — | Pendente |
| RN22 | `DUPLICIDADE_TERAPEUTICA` (MEDIA) | Duas prescrições ativas da mesma classe | Schultz et al., *Infection Control & Hospital Epidemiology*, 2014 (terapia antimicrobiana redundante) | Quais associações da mesma classe são aceitas (ex.: sinergismo) e devem ser exceção? | — | — | Pendente |

## Relatórios

| Regra | Relatório | Parâmetro em uso | Fonte técnica | Perguntas de verificação | Responsável | Data | Parecer |
|---|---|---|---|---|---|---|---|
| RN19 | Antibiograma cumulativo | Primeiro isolado por paciente; mínimo de 30 isolados (`AMI_MINIMO_ISOLADOS`) | CLSI M39 | O agrupamento por nome de microrganismo atende ao laboratório? O período padrão de 12 meses é adequado? | — | — | Pendente |
| RN23 | Indicadores de consumo (DOT) | 1 DOT por paciente, antimicrobiano e dia; meta ACCESS de 60% | CDC/NHSN, *Antimicrobial Use and Resistance Module*; WHO, meta de 60% de consumo ACCESS | Os dados de prescrição (início e término) bastam para o DOT ou é preciso a administração registrada pela enfermagem? | — | — | Pendente |

## Referências

- Barlam, T. F. et al. *Implementing an Antibiotic Stewardship Program: Guidelines by IDSA and SHEA*. Clinical Infectious Diseases, 2016.
- ANVISA. *Diretriz Nacional para Elaboração de Programa de Gerenciamento do Uso de Antimicrobianos em Serviços de Saúde*. Brasília, 2017.
- Bratzler, D. W. et al. *Clinical practice guidelines for antimicrobial prophylaxis in surgery*. American Journal of Health-System Pharmacy, 2013.
- Evans, L. et al. *Surviving Sepsis Campaign: International Guidelines for Management of Sepsis and Septic Shock 2021*. Critical Care Medicine, 2021.
- BrCAST / EUCAST. *Tabelas de pontos de corte para interpretação de CIMs e diâmetros de halos* (versão vigente).
- WHO. *The WHO AWaRe (Access, Watch, Reserve) antibiotic book*. Genebra, 2022.
- Schultz, L. et al. *Economic impact of redundant antimicrobial therapy in US hospitals*. Infection Control & Hospital Epidemiology, 2014.
- CLSI. *M39 — Analysis and Presentation of Cumulative Antimicrobial Susceptibility Test Data*.
- CDC. *National Healthcare Safety Network (NHSN) — Antimicrobial Use and Resistance (AUR) Module*.
