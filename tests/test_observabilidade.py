"""Logs estruturados em JSON e identificador de requisição."""

import io
import json
import logging

import pytest
from fastapi.testclient import TestClient

from antimicrobiano.config import Configuracao, ConfiguracaoInvalida
from antimicrobiano.main import create_app
from antimicrobiano.observabilidade import FormatadorJSON


@pytest.fixture
def logs():
    """Captura, já formatados em JSON, os logs do pacote durante o teste."""
    saida = io.StringIO()
    manipulador = logging.StreamHandler(saida)
    manipulador.setFormatter(FormatadorJSON())
    logger = logging.getLogger("antimicrobiano")
    logger.addHandler(manipulador)
    try:
        yield lambda: [json.loads(linha) for linha in saida.getvalue().splitlines()]
    finally:
        logger.removeHandler(manipulador)


def test_toda_resposta_traz_o_identificador_da_requisicao(client):
    resposta = client.get("/health")

    assert len(resposta.headers["X-Request-ID"]) == 32


def test_identificador_enviado_pelo_cliente_e_reaproveitado(client):
    resposta = client.get("/health", headers={"X-Request-ID": "chamado-123"})

    assert resposta.headers["X-Request-ID"] == "chamado-123"


def test_identificador_invalido_do_cliente_e_substituido(client):
    resposta = client.get("/health", headers={"X-Request-ID": "invalido com espacos"})

    assert resposta.headers["X-Request-ID"] != "invalido com espacos"


def test_requisicao_registrada_em_json_com_contexto(client, logs):
    resposta = client.get("/antimicrobianos/999", headers={"X-Request-ID": "teste-404"})

    registro = next(r for r in logs() if r["logger"] == "antimicrobiano.http")
    assert registro["nivel"] == "WARNING"
    assert registro["id_requisicao"] == "teste-404" == resposta.json()["id_requisicao"]
    assert (registro["metodo"], registro["rota"], registro["status"]) == (
        "GET",
        "/antimicrobianos/999",
        404,
    )
    assert registro["duracao_ms"] >= 0
    assert "momento" in registro


def test_erro_inesperado_responde_500_generico_e_registra_o_rastreamento(logs):
    app = create_app(Configuracao(database_url="sqlite://"))

    @app.get("/falha-de-teste")
    def _falhar():
        raise RuntimeError("detalhe interno que não deve vazar")

    with TestClient(app, raise_server_exceptions=False) as cliente:
        resposta = cliente.get("/falha-de-teste", headers={"X-Request-ID": "falha-1"})

    assert resposta.status_code == 500
    assert resposta.headers["X-Request-ID"] == "falha-1"
    corpo = resposta.json()
    assert (corpo["codigo"], corpo["id_requisicao"]) == ("ERRO_INTERNO", "falha-1")
    assert "detalhe interno" not in resposta.text
    erro = next(r for r in logs() if r["logger"] == "antimicrobiano.erros")
    assert erro["nivel"] == "ERROR"
    assert erro["id_requisicao"] == "falha-1"
    assert "RuntimeError: detalhe interno" in erro["excecao"]


def test_nivel_de_log_configuravel(monkeypatch):
    monkeypatch.setenv("AMI_LOG_NIVEL", "warning")

    assert Configuracao.do_ambiente().log_nivel == "WARNING"


def test_nivel_de_log_invalido(monkeypatch):
    monkeypatch.setenv("AMI_LOG_NIVEL", "VERBOSO")

    with pytest.raises(ConfiguracaoInvalida, match="AMI_LOG_NIVEL"):
        Configuracao.do_ambiente()
