"""Logs estruturados em JSON e identificador de requisição (observabilidade).

Cada requisição recebe um identificador (o cabeçalho ``X-Request-ID`` enviado pelo cliente,
se válido, ou um novo UUID). Ele é devolvido no cabeçalho da resposta, incluído no corpo dos
erros e registrado no log JSON junto com o método, a rota, o status e a duração.
"""

from __future__ import annotations

import json
import logging
import re
import sys
import time
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

CABECALHO_ID = "X-Request-ID"
PADRAO_ID_CLIENTE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


logger_http = logging.getLogger("antimicrobiano.http")

_CAMPOS_PADRAO_DO_REGISTRO = set(vars(logging.LogRecord("", 0, "", 0, "", None, None))) | {
    "message",
    "asctime",
}


class FormatadorJSON(logging.Formatter):
    """Formata cada registro de log como um objeto JSON de uma linha."""

    def format(self, record: logging.LogRecord) -> str:
        dados = {
            "momento": datetime.fromtimestamp(record.created, UTC).isoformat(
                timespec="milliseconds"
            ),
            "nivel": record.levelname,
            "logger": record.name,
            "mensagem": record.getMessage(),
        }
        dados.update(
            {
                chave: valor
                for chave, valor in vars(record).items()
                if chave not in _CAMPOS_PADRAO_DO_REGISTRO and not chave.startswith("_")
            }
        )
        if record.exc_info:
            dados["excecao"] = self.formatException(record.exc_info)
        return json.dumps(dados, ensure_ascii=False, default=str)


def configurar_logs(nivel: str = "INFO") -> None:
    """Envia os logs do pacote ``antimicrobiano`` para a saída padrão em JSON (idempotente)."""
    logger = logging.getLogger("antimicrobiano")
    logger.setLevel(nivel)
    if not any(getattr(h, "_antimicrobiano_json", False) for h in logger.handlers):
        manipulador = logging.StreamHandler(sys.stdout)
        manipulador.setFormatter(FormatadorJSON())
        manipulador._antimicrobiano_json = True  # type: ignore[attr-defined]
        logger.addHandler(manipulador)
    logger.propagate = False


def id_da_requisicao(request: Request) -> str | None:
    """Identificador atribuído à requisição pelo middleware, se houver."""
    return getattr(request.state, "id_requisicao", None)


class MiddlewareDeObservabilidade(BaseHTTPMiddleware):
    """Atribui o identificador, mede a duração e registra a requisição no log JSON."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        recebido = request.headers.get(CABECALHO_ID, "")
        identificador = recebido if PADRAO_ID_CLIENTE.match(recebido) else uuid4().hex
        request.state.id_requisicao = identificador
        inicio = time.perf_counter()
        resposta = await call_next(request)
        resposta.headers[CABECALHO_ID] = identificador
        status = resposta.status_code
        nivel = (
            logging.ERROR if status >= 500 else logging.WARNING if status >= 400 else logging.INFO
        )
        logger_http.log(
            nivel,
            "%s %s → %s",
            request.method,
            request.url.path,
            status,
            extra={
                "id_requisicao": identificador,
                "metodo": request.method,
                "rota": request.url.path,
                "status": status,
                "duracao_ms": round((time.perf_counter() - inicio) * 1000, 1),
            },
        )
        return resposta


def registrar_observabilidade(app: FastAPI, nivel: str = "INFO") -> None:
    """Configura os logs e instala o middleware na aplicação."""
    configurar_logs(nivel)
    app.add_middleware(MiddlewareDeObservabilidade)
