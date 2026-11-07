# Registros de Decisão de Arquitetura (ADR)

Cada arquivo registra **uma** decisão: o contexto, a decisão, as alternativas consideradas e as consequências. Um ADR aceito não é reescrito; se a decisão mudar, cria-se um novo ADR que o substitui e o antigo passa a *Substituída*.

| ADR | Decisão | Situação | Data | Versão |
|---|---|---|---|---|
| [0001](0001-python-e-fastapi.md) | Python e FastAPI na API REST | Aceita | 05/11/2026 | v0.1.0 |
| [0002](0002-sqlite-e-sqlalchemy.md) | SQLite com SQLAlchemy 2.0 | Aceita | 05/11/2026 | v0.1.0 |
| [0003](0003-motor-de-regras-strategy.md) | Motor de regras próprio no padrão Strategy | Aceita | 06/11/2026 | v0.3.0 |
| [0004](0004-alertas-calculados-sob-demanda.md) | Alertas calculados sob demanda | Aceita | 06/11/2026 | v0.3.0 |
| [0005](0005-paciente-por-codigo.md) | Paciente identificado apenas por código | Aceita | 05/11/2026 | v0.2.0 |
| [0006](0006-pytest-e-github-actions.md) | pytest e GitHub Actions com gates de qualidade | Aceita | 05/11/2026 | v0.1.0 (gates na v1.0.0) |
| [0007](0007-autenticacao-jwt-e-perfis.md) | Autenticação por token JWT e perfis de acesso | Aceita | 07/11/2026 | v1.0.0 |
| [0008](0008-formato-unico-de-erro.md) | Formato único de erro com mensagens em português | Aceita | 07/11/2026 | v1.0.0 |
| [0009](0009-logs-estruturados.md) | Logs estruturados em JSON com identificador da requisição | Aceita | 07/11/2026 | v1.0.0 |
| [0010](0010-interface-web-estatica.md) | Interface web estática servida pela própria API | Aceita | 07/11/2026 | v1.0.0 |
| [0011](0011-execucao-em-docker.md) | Execução reprodutível com Docker | Aceita | 07/11/2026 | v1.0.0 |

Para registrar uma decisão nova, copie a estrutura de um ADR existente, use o próximo número e inclua a linha nesta tabela.
