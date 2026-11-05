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
            motor["<b>regras/</b><br/>Motor de regras + 7 regras clínicas (Strategy)"]
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
