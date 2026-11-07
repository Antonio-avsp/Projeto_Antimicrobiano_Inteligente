"""Exceções de domínio e o formato único de erro da API.

Os serviços lançam exceções de domínio sem conhecer HTTP; a camada de apresentação converte
estas exceções, os erros de validação e os erros HTTP do framework no mesmo corpo JSON:

``{"codigo": "...", "mensagem": "...", "campos": [...], "id_requisicao": "..."}``

Erros inesperados viram ``500`` com mensagem genérica (sem detalhes internos) e são registrados
no log com o rastreamento completo e o identificador da requisição.
"""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from antimicrobiano.observabilidade import CABECALHO_ID, id_da_requisicao

logger = logging.getLogger("antimicrobiano.erros")


class ErroDeDominio(Exception):
    """Erro de negócio com mensagem em português."""

    status_code = 400
    codigo = "ERRO_DE_NEGOCIO"

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem


class RecursoNaoEncontrado(ErroDeDominio):
    """O recurso solicitado não existe (HTTP 404)."""

    status_code = 404
    codigo = "RECURSO_NAO_ENCONTRADO"


class ConflitoDeEstado(ErroDeDominio):
    """Conflito de unicidade ou de estado do recurso (HTTP 409)."""

    status_code = 409
    codigo = "CONFLITO"


class RegraDeNegocioViolada(ErroDeDominio):
    """Dados válidos no formato, mas que violam uma regra de negócio (HTTP 422)."""

    status_code = 422
    codigo = "REGRA_DE_NEGOCIO"


CODIGOS_HTTP = {
    400: "REQUISICAO_INVALIDA",
    401: "NAO_AUTENTICADO",
    403: "ACESSO_NEGADO",
    404: "RECURSO_NAO_ENCONTRADO",
    405: "METODO_NAO_PERMITIDO",
    409: "CONFLITO",
    422: "VALIDACAO",
}
MENSAGENS_HTTP = {
    401: "Autenticação necessária.",
    403: "Acesso negado.",
    404: "Recurso não encontrado.",
    405: "Método não permitido para esta rota.",
}

# Tradução das mensagens de validação do Pydantic (RNF03); {chaves} vêm do contexto do erro.
MENSAGENS_VALIDACAO = {
    "missing": "Campo obrigatório.",
    "string_too_short": "Deve ter pelo menos {min_length} caractere(s).",
    "string_too_long": "Deve ter no máximo {max_length} caractere(s).",
    "string_pattern_mismatch": "Formato inválido (padrão esperado: {pattern}).",
    "string_type": "Deve ser um texto.",
    "enum": "Valor inválido; use um destes: {expected}.",
    "literal_error": "Valor inválido; use um destes: {expected}.",
    "int_parsing": "Deve ser um número inteiro.",
    "int_type": "Deve ser um número inteiro.",
    "int_from_float": "Deve ser um número inteiro.",
    "float_parsing": "Deve ser um número.",
    "bool_parsing": "Deve ser verdadeiro ou falso.",
    "bool_type": "Deve ser verdadeiro ou falso.",
    "date_parsing": "Data inválida; use o formato AAAA-MM-DD.",
    "date_from_datetime_parsing": "Data inválida; use o formato AAAA-MM-DD.",
    "date_type": "Data inválida; use o formato AAAA-MM-DD.",
    "greater_than": "Deve ser maior que {gt}.",
    "greater_than_equal": "Deve ser maior ou igual a {ge}.",
    "less_than": "Deve ser menor que {lt}.",
    "less_than_equal": "Deve ser menor ou igual a {le}.",
    "list_type": "Deve ser uma lista.",
    "dict_type": "Deve ser um objeto JSON.",
    "model_attributes_type": "Deve ser um objeto JSON.",
    "json_invalid": "JSON inválido.",
    "extra_forbidden": "Campo não permitido.",
}
MENSAGEM_VALIDACAO = "Dados inválidos: verifique os campos informados."


MENSAGEM_ERRO_INTERNO = "Erro interno inesperado. Informe o identificador da requisição ao suporte."


def corpo_de_erro(
    codigo: str, mensagem: str, campos: list[dict] | None = None, id_requisicao: str | None = None
) -> dict:
    """Corpo JSON padronizado de todas as respostas de erro."""
    return {
        "codigo": codigo,
        "mensagem": mensagem,
        "campos": campos or [],
        "id_requisicao": id_requisicao,
    }


def traduzir_erro_de_validacao(erro: dict[str, Any]) -> dict[str, str]:
    """Converte um erro do Pydantic em ``{"campo", "local", "mensagem"}`` em português."""
    local, *caminho = [str(parte) for parte in erro.get("loc", ())] or ["body"]
    modelo = MENSAGENS_VALIDACAO.get(erro.get("type", ""))
    if modelo:
        try:
            mensagem = modelo.format(**(erro.get("ctx") or {}))
        except (KeyError, IndexError):
            mensagem = modelo
    else:
        mensagem = str(erro.get("msg", "Valor inválido."))
        mensagem = mensagem.removeprefix("Value error, ").removeprefix("Assertion failed, ")
    return {"campo": ".".join(caminho) or local, "local": local, "mensagem": mensagem}


def _resposta(status_code: int, corpo: dict, headers: dict | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=jsonable_encoder(corpo), headers=headers)


def registrar_tratadores_de_erro(app: FastAPI) -> None:
    """Registra os tratadores que produzem o formato único de erro."""

    @app.exception_handler(ErroDeDominio)
    async def _erro_de_dominio(request: Request, erro: ErroDeDominio) -> JSONResponse:
        corpo = corpo_de_erro(erro.codigo, erro.mensagem, id_requisicao=id_da_requisicao(request))
        return _resposta(erro.status_code, corpo)

    @app.exception_handler(RequestValidationError)
    async def _erro_de_validacao(request: Request, erro: RequestValidationError) -> JSONResponse:
        campos = [traduzir_erro_de_validacao(item) for item in erro.errors()]
        corpo = corpo_de_erro(
            "VALIDACAO", MENSAGEM_VALIDACAO, campos, id_requisicao=id_da_requisicao(request)
        )
        return _resposta(422, corpo)

    @app.exception_handler(Exception)
    async def _erro_inesperado(request: Request, erro: Exception) -> JSONResponse:
        identificador = id_da_requisicao(request)
        logger.error(
            "Erro inesperado em %s %s",
            request.method,
            request.url.path,
            exc_info=erro,
            extra={"id_requisicao": identificador, "rota": request.url.path},
        )
        corpo = corpo_de_erro("ERRO_INTERNO", MENSAGEM_ERRO_INTERNO, id_requisicao=identificador)
        cabecalhos = {CABECALHO_ID: identificador} if identificador else None
        return _resposta(500, corpo, cabecalhos)

    @app.exception_handler(StarletteHTTPException)
    async def _erro_http(request: Request, erro: StarletteHTTPException) -> JSONResponse:
        codigo = CODIGOS_HTTP.get(erro.status_code, "ERRO_HTTP")
        padrao = MENSAGENS_HTTP.get(erro.status_code) or HTTPStatus(erro.status_code).phrase
        mensagem = erro.detail if isinstance(erro.detail, str) else padrao
        if mensagem in {"Not Found", "Method Not Allowed", "Unauthorized", "Forbidden"}:
            mensagem = padrao
        corpo = corpo_de_erro(codigo, mensagem, id_requisicao=id_da_requisicao(request))
        return _resposta(erro.status_code, corpo, erro.headers)
