# Arquitetura

Visão arquitetural do **Antimicrobiano Inteligente** segundo o [modelo C4](https://c4model.com/) (contexto → contêineres → componentes), complementada pela arquitetura em camadas, pelo fluxo de geração de alertas e pelas principais decisões técnicas. O modelo de dados está em [modelo-de-dados.md](modelo-de-dados.md).

## 1. Nível 1 — Diagrama de contexto

```mermaid
flowchart TB
    farm["<b>Farmacêutico clínico / Infectologista</b><br/>[Pessoa]<br/>Equipe do PGA que triaga prescrições e registra intervenções"]
    lab["<b>Analista de microbiologia</b><br/>[Pessoa]<br/>Registra culturas e antibiogramas"]
    gestor["<b>Gestor da CCIH</b><br/>[Pessoa]<br/>Mantém o catálogo e analisa o perfil de resistência"]

    sis["<b>Antimicrobiano Inteligente</b><br/>[Sistema de software]<br/>API REST que centraliza prescrições, culturas e antibiogramas e gera alertas explicáveis de uso de antimicrobianos"]

    his["<b>Prontuário eletrônico / HIS</b><br/>[Sistema externo — fora do escopo]"]
    lis["<b>Sistema do laboratório / LIS</b><br/>[Sistema externo — fora do escopo]"]

    farm -- "Registra prescrições, reavaliações e consulta o painel de alertas<br/>[HTTPS/JSON]" --> sis
    lab -- "Registra culturas e resultados<br/>[HTTPS/JSON]" --> sis
    gestor -- "Mantém catálogo e gera antibiograma cumulativo<br/>[HTTPS/JSON]" --> sis
    his -. "Integração futura (HL7/FHIR)" .-> sis
    lis -. "Integração futura" .-> sis

    classDef pessoa fill:#08427b,stroke:#052e56,color:#fff
    classDef sistema fill:#1168bd,stroke:#0b4884,color:#fff
    classDef externo fill:#999999,stroke:#6b6b6b,color:#fff,stroke-dasharray: 5 5
    class farm,lab,gestor pessoa
    class sis sistema
    class his,lis externo
```

## 2. Nível 2 — Diagrama de contêineres

```mermaid
flowchart TB
    usuario["<b>Usuários do PGA</b><br/>[Pessoa]"]

    subgraph fronteira["Antimicrobiano Inteligente"]
        swagger["<b>Swagger UI / ReDoc</b><br/>[Navegador]<br/>Documentação interativa gerada a partir do OpenAPI"]
        api["<b>API REST</b><br/>[Python 3.11+, FastAPI, Uvicorn]<br/>Regras de negócio, motor de regras e relatórios"]
        db[("<b>Banco de dados</b><br/>[SQLite via SQLAlchemy]<br/>Catálogo, prescrições, reavaliações, culturas e antibiogramas")]
        web["<b>Interface web</b><br/>[HTML + JavaScript]<br/>Planejada — issue #26"]
    end

    usuario -- "Usa [HTTPS]" --> swagger
    usuario -. "Usará" .-> web
    swagger -- "Chama [JSON/HTTPS]" --> api
    web -. "Chamará [JSON/HTTPS]" .-> api
    api -- "Lê e grava [SQL via ORM]" --> db

    classDef pessoa fill:#08427b,stroke:#052e56,color:#fff
    classDef container fill:#438dd5,stroke:#2e6295,color:#fff
    classDef banco fill:#438dd5,stroke:#2e6295,color:#fff
    classDef futuro fill:#cccccc,stroke:#999999,color:#333,stroke-dasharray: 5 5
    class usuario pessoa
    class swagger,api container
    class db banco
    class web futuro
```

## 3. Nível 3 — Diagrama de componentes da API

```mermaid
flowchart LR
    cliente["Cliente HTTP<br/>(Swagger UI, curl, interface web)"]

    subgraph api["API REST — pacote antimicrobiano"]
        direction LR
        subgraph http["Camada de apresentação"]
            routers["<b>routers/</b><br/>Rotas FastAPI por recurso"]
            schemas["<b>schemas/</b><br/>Contratos Pydantic<br/>(validação de entrada e saída)"]
        end
        subgraph negocio["Camada de negócio"]
            services["<b>services/</b><br/>Casos de uso e regras de negócio (RN01–RN10, RN19)"]
            motor["<b>regras/</b><br/>Motor de regras + 8 regras clínicas (Strategy)"]
            erros["<b>erros.py</b><br/>Exceções de domínio → HTTP 404/409/422"]
        end
        subgraph dados["Camada de dados"]
            models["<b>models.py</b><br/>Entidades ORM SQLAlchemy"]
            database["<b>database.py</b><br/>Engine e sessão"]
        end
        config["<b>config.py</b><br/>Configuração por variáveis de ambiente"]
    end

    db[("SQLite")]

    cliente --> routers
    routers --> schemas
    routers --> services
    services --> erros
    services --> motor
    services --> models
    motor --> models
    models --> database
    database --> db
    config -.-> database
    config -.-> motor
```

## 4. Arquitetura em camadas

| Camada | Pacote | Responsabilidade | Pode depender de |
|---|---|---|---|
| Apresentação | `routers/`, `schemas/` | Receber requisições HTTP, validar formato (Pydantic), serializar respostas e documentar o OpenAPI. | Negócio |
| Negócio | `services/`, `regras/`, `erros.py` | Aplicar as regras de negócio e os casos de uso; lançar exceções de domínio independentes de HTTP. | Dados |
| Dados | `models.py`, `database.py` | Mapear entidades para tabelas e gerenciar sessões/transações. | — |
| Transversal | `config.py`, `enums.py` | Configuração por ambiente e enumerações do domínio. | — |

As regras do motor **não acessam o banco**: recebem a prescrição e um contexto pré-carregado (culturas relevantes, parâmetros e data de referência). Isso as torna funções puras, testáveis isoladamente (RNF08), e evita consultas repetidas por prescrição (RNF01).

## 5. Motor de regras — padrão Strategy

- Cada regra é uma classe que implementa `avaliar(prescricao, contexto) -> list[Alerta]`.
- O `MotorDeRegras` recebe a lista de regras e as aplica a cada prescrição ativa.
- Incluir uma regra é criar uma nova classe e registrá-la no motor, **sem alterar as demais** (princípio aberto/fechado — RNF07). Foi assim que a duplicidade terapêutica (#22, RN22) entrou na v1.0.0: `RegraDuplicidadeTerapeutica` em `regras/politicas.py`, com o contexto passando a expor as prescrições ativas do paciente.
- Cada alerta carrega **evidências** (datas, dia de terapia, culturas, interpretações) para que a recomendação seja auditável (RNF10).

## 6. Fluxo de geração do painel de alertas

```mermaid
sequenceDiagram
    autonumber
    actor U as Farmacêutico / Infectologista
    participant R as Router /alertas
    participant S as Serviço de alertas
    participant DB as Banco (SQLAlchemy)
    participant M as MotorDeRegras
    participant RG as Regras (Strategy)

    U->>R: GET /alertas?data_referencia=2026-11-05&severidade=ALTA
    R->>S: gerar_painel(data_referencia, filtros)
    S->>DB: prescrições ATIVA + antimicrobiano + reavaliações
    DB-->>S: prescrições
    S->>DB: culturas dos pacientes envolvidos + antibiogramas
    DB-->>S: culturas
    S->>M: avaliar(prescrições, contexto)
    loop Para cada prescrição ativa
        M->>RG: regra.avaliar(prescrição, contexto)
        RG-->>M: 0..n alertas com evidências
    end
    M-->>S: alertas
    S->>S: filtrar, ordenar por severidade e resumir
    S-->>R: painel
    R-->>U: 200 OK (JSON com aviso, resumo e alertas)
```

## 7. Recursos da API

| Método | Rota | Descrição | Requisito |
|---|---|---|---|
| `GET` | `/health` | Status e versão da aplicação | RNF03 |
| `POST` | `/antimicrobianos` | Cadastrar antimicrobiano | RF01 |
| `GET` | `/antimicrobianos` | Listar com filtros | RF02 |
| `GET` | `/antimicrobianos/{id}` | Consultar | RF02 |
| `PATCH` | `/antimicrobianos/{id}` | Atualizar | RF02 |
| `DELETE` | `/antimicrobianos/{id}` | Inativar (exclusão lógica) | RF02 |
| `POST` | `/prescricoes` | Registrar prescrição | RF03 |
| `GET` | `/prescricoes` | Listar com filtros | RF04 |
| `GET` | `/prescricoes/{id}` | Consultar | RF04 |
| `PATCH` | `/prescricoes/{id}` | Atualizar prescrição ativa | RF04 |
| `POST` | `/prescricoes/{id}/reavaliacoes` | Registrar reavaliação (time-out) | RF05 |
| `GET` | `/prescricoes/{id}/reavaliacoes` | Histórico de reavaliações | RF05 |
| `POST` | `/prescricoes/{id}/encerramento` | Encerrar prescrição | RF05 |
| `POST` | `/culturas` | Registrar coleta | RF06 |
| `GET` | `/culturas` | Listar culturas | RF06 |
| `GET` | `/culturas/{id}` | Consultar cultura | RF06 |
| `PUT` | `/culturas/{id}/resultado` | Registrar resultado e antibiograma | RF06 |
| `GET` | `/alertas` | Painel de alertas inteligentes | RF07–RF13 |
| `GET` | `/relatorios/antibiograma-cumulativo` | Antibiograma cumulativo | RF14 |
| `GET` | `/relatorios/indicadores` | Indicadores de consumo (DOT) por antimicrobiano, categoria AWaRe e setor | RF15 |

**Convenção de erros:** `404` recurso inexistente · `405` método não permitido · `409` conflito de estado ou de unicidade · `422` dados inválidos ou regra de negócio violada. Todas as respostas de erro — de negócio, de validação e do próprio framework — seguem o esquema único `Erro` (`erros.py`), com mensagens em português:

```json
{
  "codigo": "VALIDACAO",
  "mensagem": "Dados inválidos: verifique os campos informados.",
  "campos": [
    {"campo": "categoria_aware", "local": "body", "mensagem": "Valor inválido; use um destes: 'ACCESS', 'WATCH' ou 'RESERVE'."}
  ]
}
```

| `codigo` | Status | Quando |
|---|---|---|
| `RECURSO_NAO_ENCONTRADO` | 404 | Recurso ou rota inexistente |
| `METODO_NAO_PERMITIDO` | 405 | Método HTTP não aceito pela rota |
| `CONFLITO` | 409 | Unicidade ou estado do recurso (ex.: prescrição encerrada) |
| `REGRA_DE_NEGOCIO` | 422 | Dados bem formados que violam uma regra de negócio |
| `VALIDACAO` | 422 | Campo ausente, tipo ou formato inválido (`campos` indica cada problema) |

## 8. Decisões de arquitetura

| Decisão | Alternativas consideradas | Motivo |
|---|---|---|
| **Python + FastAPI** | Flask, Django REST, Node.js/Express | Validação declarativa com Pydantic, OpenAPI/Swagger automático (RNF03) e tipagem que facilita testes. |
| **SQLite + SQLAlchemy 2.0** | PostgreSQL, arquivos JSON | Zero configuração e portabilidade (RNF06); o ORM permite migrar para PostgreSQL só trocando `AMI_DATABASE_URL` (RNF02). |
| **Motor de regras próprio (Strategy)** | Motor de regras de terceiros, aprendizado de máquina | Regras clínicas simples, explicáveis e testáveis; não há dados reais para treinar modelos. |
| **Alertas calculados sob demanda** | Persistir alertas em tabela | Os alertas sempre refletem o estado atual; resolver a causa (ex.: registrar reavaliação) encerra o alerta automaticamente. |
| **Paciente apenas por código** | Cadastro de pacientes | Minimização de dados (LGPD — RNF04); a identificação fica no prontuário de origem. |
| **pytest + GitHub Actions** | unittest, outros serviços de CI | Padrão de mercado, gratuito e integrado ao GitHub (RNF08, RNF12). |
