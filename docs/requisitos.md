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
