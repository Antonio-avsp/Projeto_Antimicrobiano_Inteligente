# ADR 0007 — Autenticação por token JWT e perfis de acesso

- **Situação:** Aceita
- **Data:** 07/11/2026
- **Versão:** v1.0.0
- **Issue:** #24

## Contexto

A API expunha dados clínicos sem controle de acesso (risco apontado na Avaliação Técnica Week_01). É preciso autenticar, autorizar por perfil e registrar a autoria das intervenções (RF17), sem servidor de identidade.

## Decisão

Login em `POST /auth/login` com senha conferida contra hash **scrypt** com sal (biblioteca padrão) e emissão de **JWT HS256** com expiração (PyJWT). Cada rota declara a dependência de usuário autenticado e, nas escritas, os perfis permitidos (RN24). O segredo vem de `AMI_JWT_SEGREDO`.

## Alternativas consideradas

- **Sessão com cookie:** exige estado no servidor e proteção contra CSRF.
- **OAuth2 com formulário (`OAuth2PasswordRequestForm`):** exigiria a dependência `python-multipart` e um corpo em formulário em vez de JSON.
- **bcrypt/argon2:** dependências nativas extras; o scrypt da biblioteca padrão atende ao requisito.

## Consequências

- API sem estado e fácil de testar.
- Permissões declaradas junto de cada rota.
- Um token não pode ser revogado antes de expirar; a inativação do usuário bloqueia o acesso na próxima requisição.
