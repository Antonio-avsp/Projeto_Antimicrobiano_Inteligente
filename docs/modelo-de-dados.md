# Modelo de Dados

Modelo de dados do **Antimicrobiano Inteligente**: Diagrama Entidade-Relacionamento (DER), dicionário de dados e diagrama de classes. A persistência usa SQLite por meio do ORM SQLAlchemy (RNF02).

> **Decisão de privacidade (RNF04):** não existe tabela de pacientes. Prescrições e culturas referenciam o paciente apenas pelo código pseudonimizado `paciente_codigo` (`PAC-` + 4 a 10 dígitos). O vínculo entre prescrição e cultura é feito por esse código.

## 1. Diagrama Entidade-Relacionamento (DER)

```mermaid
erDiagram
    ANTIMICROBIANO ||--o{ PRESCRICAO : "é prescrito em"
    PRESCRICAO ||--o{ REAVALIACAO : "recebe"
    CULTURA ||--o{ ITEM_ANTIBIOGRAMA : "possui"
    ANTIMICROBIANO ||--o{ ITEM_ANTIBIOGRAMA : "é testado em"

    ANTIMICROBIANO {
        int id PK
        string nome
        string nome_normalizado UK
        string classe
        string categoria_aware "ACCESS, WATCH ou RESERVE"
        boolean uso_restrito
        boolean ativo
        datetime criado_em
        datetime atualizado_em
    }
    PRESCRICAO {
        int id PK
        string paciente_codigo "PAC-NNNN"
        string setor
        int antimicrobiano_id FK
        string dose
        int intervalo_horas
        string via "IV, VO ou IM"
        string indicacao "PROFILAXIA, EMPIRICA ou DIRIGIDA"
        string diagnostico
        date data_inicio
        int duracao_prevista_dias
        string justificativa "opcional"
        string status "ATIVA, CONCLUIDA ou SUSPENSA"
        date data_fim "opcional"
        string motivo_encerramento "opcional"
        datetime criado_em
        datetime atualizado_em
    }
    REAVALIACAO {
        int id PK
        int prescricao_id FK
        date data_reavaliacao
        string conduta "MANTER, AJUSTAR, DESCALONAR ou SUSPENDER"
        string observacao "opcional"
        datetime criado_em
    }
    CULTURA {
        int id PK
        string paciente_codigo "PAC-NNNN"
        string setor
        string material
        date data_coleta
        string status "PENDENTE, POSITIVA ou NEGATIVA"
        string microrganismo "opcional"
        date data_resultado "opcional"
        datetime criado_em
        datetime atualizado_em
    }
    ITEM_ANTIBIOGRAMA {
        int id PK
        int cultura_id FK
        int antimicrobiano_id FK
        string interpretacao "S, I ou R"
    }
```

**Cardinalidades**

- Um antimicrobiano pode estar em **zero ou muitas** prescrições; cada prescrição refere-se a **exatamente um** antimicrobiano.
- Uma prescrição recebe **zero ou muitas** reavaliações.
- Uma cultura positiva possui **zero ou muitos** itens de antibiograma; cada item refere-se a **um** antimicrobiano, que aparece no máximo uma vez por cultura (RN10).

## 2. Dicionário de dados

### 2.1 `antimicrobianos`

| Campo | Tipo | Obrig. | Restrições | Descrição |
|---|---|---|---|---|
| `id` | inteiro | sim | PK, autoincremento | Identificador |
| `nome` | texto (80) | sim | 2 a 80 caracteres | Nome comercial/genérico (ex.: Ceftriaxona) |
| `nome_normalizado` | texto (80) | sim | **único** | Nome em minúsculas, sem acentos e sem espaços extras (RN01) |
| `classe` | texto (80) | sim | 2 a 80 caracteres | Classe farmacológica |
| `categoria_aware` | enum | sim | `ACCESS`, `WATCH`, `RESERVE` | Classificação AWaRe da OMS |
| `uso_restrito` | booleano | sim | padrão `false` | Exige justificativa (RN07) |
| `ativo` | booleano | sim | padrão `true` | Inativação lógica (RN02, RN03) |
| `criado_em`, `atualizado_em` | data e hora | sim | automáticos (UTC) | Auditoria (RNF09) |

### 2.2 `prescricoes`

| Campo | Tipo | Obrig. | Restrições | Descrição |
|---|---|---|---|---|
| `id` | inteiro | sim | PK | Identificador |
| `paciente_codigo` | texto (15) | sim | `^PAC-\d{4,10}$`, indexado | Paciente pseudonimizado (RN04) |
| `setor` | texto (60) | sim | 2 a 60 caracteres | Setor de internação |
| `antimicrobiano_id` | inteiro | sim | FK → `antimicrobianos.id` | Antimicrobiano prescrito (deve estar ativo — RN02) |
| `dose` | texto (40) | sim | 1 a 40 caracteres | Dose por administração (ex.: "1 g") |
| `intervalo_horas` | inteiro | sim | 1 a 168 | Intervalo entre doses (RN06) |
| `via` | enum | sim | `IV`, `VO`, `IM` | Via de administração |
| `indicacao` | enum | sim | `PROFILAXIA`, `EMPIRICA`, `DIRIGIDA` | Finalidade da terapia |
| `diagnostico` | texto (120) | sim | 3 a 120 caracteres | Diagnóstico/sítio de infecção ou procedimento |
| `data_inicio` | data | sim | ≤ hoje | Início da terapia (RN05) |
| `duracao_prevista_dias` | inteiro | sim | 1 a 90 | Duração planejada (RN06) |
| `justificativa` | texto (500) | não | — | Justificativa clínica (RN07) |
| `status` | enum | sim | `ATIVA`, `CONCLUIDA`, `SUSPENSA` | Situação da prescrição |
| `data_fim` | data | não | início ≤ data ≤ hoje | Data de término (RN09) |
| `motivo_encerramento` | texto (300) | não | — | Motivo informado no encerramento |
| `criado_em`, `atualizado_em` | data e hora | sim | automáticos (UTC) | Auditoria |

### 2.3 `reavaliacoes`

| Campo | Tipo | Obrig. | Restrições | Descrição |
|---|---|---|---|---|
| `id` | inteiro | sim | PK | Identificador |
| `prescricao_id` | inteiro | sim | FK → `prescricoes.id`, indexado | Prescrição reavaliada |
| `data_reavaliacao` | data | sim | início ≤ data ≤ hoje | Data do time-out (RN09) |
| `conduta` | enum | sim | `MANTER`, `AJUSTAR`, `DESCALONAR`, `SUSPENDER` | Decisão tomada |
| `observacao` | texto (500) | não | — | Detalhes da intervenção |
| `criado_em` | data e hora | sim | automático (UTC) | Auditoria |

### 2.4 `culturas`

| Campo | Tipo | Obrig. | Restrições | Descrição |
|---|---|---|---|---|
| `id` | inteiro | sim | PK | Identificador |
| `paciente_codigo` | texto (15) | sim | `^PAC-\d{4,10}$`, indexado | Paciente pseudonimizado |
| `setor` | texto (60) | sim | 2 a 60 caracteres | Setor de coleta |
| `material` | enum | sim | `SANGUE`, `URINA`, `SECRECAO_TRAQUEAL`, `LIQUOR`, `PONTA_DE_CATETER`, `SECRECAO_DE_FERIDA`, `OUTRO` | Material biológico |
| `data_coleta` | data | sim | ≤ hoje | Data da coleta (RN10) |
| `status` | enum | sim | `PENDENTE`, `POSITIVA`, `NEGATIVA` | Situação do exame |
| `microrganismo` | texto (120) | condicional | obrigatório se `POSITIVA` | Microrganismo isolado |
| `data_resultado` | data | não | coleta ≤ data ≤ hoje | Data de liberação do resultado |
| `criado_em`, `atualizado_em` | data e hora | sim | automáticos (UTC) | Auditoria |

### 2.5 `itens_antibiograma`

| Campo | Tipo | Obrig. | Restrições | Descrição |
|---|---|---|---|---|
| `id` | inteiro | sim | PK | Identificador |
| `cultura_id` | inteiro | sim | FK → `culturas.id` (exclusão em cascata) | Cultura de origem |
| `antimicrobiano_id` | inteiro | sim | FK → `antimicrobianos.id` | Antimicrobiano testado |
| `interpretacao` | enum | sim | `S`, `I`, `R` | Interpretação BrCAST/EUCAST |
| (`cultura_id`, `antimicrobiano_id`) | — | — | **único** | Um antimicrobiano por antibiograma (RN10) |

## 3. Diagrama de classes

O diagrama mostra as entidades do domínio e o motor de regras, que aplica o padrão **Strategy**: cada regra clínica é uma especialização de `Regra` e o `MotorDeRegras` apenas as orquestra (RNF07).

```mermaid
classDiagram
    direction TB

    class Antimicrobiano {
        +int id
        +str nome
        +str classe
        +CategoriaAware categoria_aware
        +bool uso_restrito
        +bool ativo
    }
    class Prescricao {
        +int id
        +str paciente_codigo
        +str setor
        +Indicacao indicacao
        +date data_inicio
        +int duracao_prevista_dias
        +str justificativa
        +StatusPrescricao status
        +dia_de_terapia(data_referencia) int
    }
    class Reavaliacao {
        +date data_reavaliacao
        +Conduta conduta
        +str observacao
    }
    class Cultura {
        +str paciente_codigo
        +Material material
        +date data_coleta
        +StatusCultura status
        +str microrganismo
    }
    class ItemAntibiograma {
        +Interpretacao interpretacao
    }

    Prescricao "*" --> "1" Antimicrobiano : prescreve
    Prescricao "1" *-- "*" Reavaliacao : reavaliacoes
    Cultura "1" *-- "*" ItemAntibiograma : antibiograma
    ItemAntibiograma "*" --> "1" Antimicrobiano : testa

    class MotorDeRegras {
        -list~Regra~ regras
        +avaliar(prescricoes, contexto) list~Alerta~
    }
    class ContextoAvaliacao {
        +date data_referencia
        +ParametrosClinicos parametros
        +culturas_relevantes(prescricao) list~Cultura~
    }
    class ParametrosClinicos {
        +int timeout_dias
        +int limite_profilaxia_dias
        +int janela_cultura_dias
        +int minimo_isolados
    }
    class Regra {
        <<abstract>>
        +TipoAlerta tipo
        +Severidade severidade
        +avaliar(prescricao, contexto) list~Alerta~
    }
    class Alerta {
        +TipoAlerta tipo
        +Severidade severidade
        +int prescricao_id
        +str mensagem
        +str recomendacao
        +dict evidencias
    }

    MotorDeRegras o-- "1..*" Regra
    MotorDeRegras ..> ContextoAvaliacao : usa
    ContextoAvaliacao --> ParametrosClinicos
    Regra ..> Prescricao : avalia
    Regra ..> Alerta : cria

    Regra <|-- RegraTimeout
    Regra <|-- RegraDuracaoExcedida
    Regra <|-- RegraProfilaxiaProlongada
    Regra <|-- RegraRestritoSemJustificativa
    Regra <|-- RegraSemCultura
    Regra <|-- RegraResistencia
    Regra <|-- RegraDescalonamento
```

## 4. Enumerações do domínio

| Enumeração | Valores |
|---|---|
| `CategoriaAware` | `ACCESS` (1), `WATCH` (2), `RESERVE` (3) — ordem usada no descalonamento (RN20) |
| `Via` | `IV`, `VO`, `IM` |
| `Indicacao` | `PROFILAXIA`, `EMPIRICA`, `DIRIGIDA` |
| `StatusPrescricao` | `ATIVA`, `CONCLUIDA`, `SUSPENSA` |
| `Conduta` | `MANTER`, `AJUSTAR`, `DESCALONAR`, `SUSPENDER` |
| `Material` | `SANGUE`, `URINA`, `SECRECAO_TRAQUEAL`, `LIQUOR`, `PONTA_DE_CATETER`, `SECRECAO_DE_FERIDA`, `OUTRO` |
| `StatusCultura` | `PENDENTE`, `POSITIVA`, `NEGATIVA` |
| `Interpretacao` | `S` (sensível), `I` (sensível, aumentando exposição), `R` (resistente) |
| `TipoAlerta` | `TIMEOUT_REAVALIACAO`, `DURACAO_EXCEDIDA`, `PROFILAXIA_PROLONGADA`, `RESTRITO_SEM_JUSTIFICATIVA`, `SEM_CULTURA`, `RESISTENCIA`, `DESCALONAMENTO` |
| `Severidade` | `ALTA`, `MEDIA`, `BAIXA` (RN21) |
