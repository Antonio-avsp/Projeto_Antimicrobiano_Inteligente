"""Exceções de domínio e sua tradução para respostas HTTP.

Os serviços lançam estas exceções sem conhecer HTTP; a camada de apresentação
as converte em ``{"detail": "mensagem"}`` com o código adequado.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ErroDeDominio(Exception):
    """Erro de negócio com mensagem em português."""

    status_code = 400

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem


class RecursoNaoEncontrado(ErroDeDominio):
    """O recurso solicitado não existe (HTTP 404)."""

    status_code = 404


class ConflitoDeEstado(ErroDeDominio):
    """Conflito de unicidade ou de estado do recurso (HTTP 409)."""

    status_code = 409


class RegraDeNegocioViolada(ErroDeDominio):
    """Dados válidos no formato, mas que violam uma regra de negócio (HTTP 422)."""

    status_code = 422


def registrar_tratadores_de_erro(app: FastAPI) -> None:
    """Registra o tratador que converte exceções de domínio em JSON."""

    @app.exception_handler(ErroDeDominio)
    async def _tratar_erro_de_dominio(_request: Request, erro: ErroDeDominio) -> JSONResponse:
        return JSONResponse(status_code=erro.status_code, content={"detail": erro.mensagem})
