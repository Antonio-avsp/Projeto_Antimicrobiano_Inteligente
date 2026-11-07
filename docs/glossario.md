# Glossário

Termos do domínio utilizados na especificação e no código do **Antimicrobiano Inteligente**. Os nomes de campos e enumerações da API aparecem em `monoespaçado`.

| Termo | Definição |
|---|---|
| **Antimicrobiano** | Medicamento que mata ou inibe o crescimento de microrganismos (bactérias, fungos etc.). Neste projeto, o foco são os antibacterianos de uso hospitalar. |
| **Antibiograma** | Teste de sensibilidade que indica, para um microrganismo isolado em cultura, a interpretação de cada antimicrobiano testado: `S`, `I` ou `R`. |
| **Antibiograma cumulativo** | Relatório que consolida os antibiogramas de um período e informa o percentual de sensibilidade de cada microrganismo a cada antimicrobiano. Orienta a terapia empírica do hospital. |
| **AWaRe** | Classificação da OMS que agrupa antibióticos em **ACCESS** (primeira escolha, menor potencial de resistência), **WATCH** (maior potencial de resistência, uso monitorado) e **RESERVE** (último recurso para bactérias multirresistentes). Campo `categoria_aware`. |
| **BrCAST / EUCAST** | Comitês (brasileiro e europeu) que padronizam a interpretação dos testes de sensibilidade utilizada no Brasil. |
| **CCIH / SCIH** | Comissão / Serviço de Controle de Infecção Hospitalar. |
| **CLSI M39** | Norma do *Clinical and Laboratory Standards Institute* para elaboração do antibiograma cumulativo (ex.: contar apenas o primeiro isolado por paciente e sinalizar amostras com menos de 30 isolados). |
| **Cultura** | Exame microbiológico de uma amostra (sangue, urina, secreção etc.) para identificar o microrganismo causador da infecção. Pode estar `PENDENTE`, `POSITIVA` ou `NEGATIVA`. |
| **Descalonamento** | Troca de um antimicrobiano de amplo espectro por outro de espectro mais estreito (ou categoria AWaRe inferior) com base no antibiograma, mantendo a eficácia. |
| **Dia de terapia** | Contagem dos dias de uso de uma prescrição, em que o dia de início é o **dia 1**. |
| **DOT (*Days of Therapy*)** | Indicador de consumo: soma dos dias em que cada antimicrobiano foi administrado a cada paciente; cada dia conta 1, independentemente do número de doses (RN23). Endpoint `GET /relatorios/indicadores`. |
| **Duplicidade terapêutica** | Duas ou mais prescrições ativas de antimicrobianos da **mesma classe** para o mesmo paciente (ex.: cefazolina IV mantida após o início da cefalexina VO). Gera o alerta `DUPLICIDADE_TERAPEUTICA` (RN22). |
| **Identificador da requisição** | Código único de cada chamada à API, devolvido no cabeçalho `X-Request-ID` e no campo `id_requisicao` dos erros e registrado no log JSON; serve para localizar um problema relatado. |
| **Indicação** | Finalidade da prescrição: `PROFILAXIA` (prevenção, ex.: cirúrgica), `EMPIRICA` (tratamento antes do resultado de cultura) ou `DIRIGIDA` (tratamento guiado por cultura). |
| **Isolado** | Microrganismo identificado em uma cultura positiva. |
| **Janela de relevância da cultura** | Período em que uma cultura é considerada para avaliar uma prescrição: de 7 dias antes do início da terapia até a data de referência (parâmetro configurável). |
| **Microrganismo resistente (`R`)** | Alta probabilidade de falha terapêutica mesmo com exposição aumentada ao antimicrobiano. |
| **Percentual ACCESS** | Parcela do consumo (em DOT) de antimicrobianos da categoria ACCESS. A OMS recomenda que seja de pelo menos **60%**. |
| **Perfil de acesso** | Papel do usuário na API, que define o que ele pode alterar: `FARMACEUTICO`, `INFECTOLOGISTA`, `LABORATORIO` ou `GESTOR` (RN24). Todos os perfis consultam o painel e os relatórios. |
| **Paciente pseudonimizado** | Paciente identificado apenas por um código (`PAC-0001`), sem nome, CPF ou outro dado pessoal direto, em conformidade com a LGPD. |
| **PGA (*stewardship*)** | Programa de Gerenciamento do Uso de Antimicrobianos: conjunto de ações coordenadas para promover o uso adequado de antimicrobianos. |
| **Profilaxia cirúrgica prolongada** | Profilaxia antimicrobiana mantida por mais de 24 horas, prática não recomendada pelas diretrizes na maioria dos procedimentos. |
| **Sensível (`S`)** | Alta probabilidade de sucesso terapêutico com a dose padrão. |
| **Sensível, aumentando exposição (`I`)** | Alta probabilidade de sucesso terapêutico desde que a exposição ao antimicrobiano seja aumentada (dose, frequência ou via). |
| **Severidade do alerta** | `ALTA` (ação imediata), `MEDIA` (ação em até 24 horas) ou `BAIXA` (oportunidade de otimização). |
| **Token de acesso (JWT)** | Credencial assinada e com validade limitada, obtida em `POST /auth/login` e enviada no cabeçalho `Authorization: Bearer <token>`. |
| **Time-out (reavaliação)** | Revisão estruturada da terapia entre 48 e 72 horas após o início, quando os resultados de cultura costumam estar disponíveis: manter, ajustar, descalonar ou suspender. |
| **Validação clínica** | Revisão de cada regra do motor por especialista (infectologista ou farmacêutico do PGA), com fonte, responsável, data e parecer registrados em [validacao-clinica.md](validacao-clinica.md). Obrigatória antes de qualquer uso assistencial; pendente até a v1.0.0. |
| **Uso restrito** | Antimicrobiano cuja prescrição exige justificativa e/ou autorização da equipe do PGA (geralmente carbapenêmicos, glicopeptídeos, polimixinas e antimicrobianos RESERVE). |
