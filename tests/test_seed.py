"""Carga de demonstração — HT01 (RNF03, RNF04)."""

import pytest
from fastapi.testclient import TestClient

from antimicrobiano.config import Configuracao
from antimicrobiano.enums import TipoAlerta
from antimicrobiano.main import create_app
from antimicrobiano.seed import main


@pytest.fixture
def banco_demo(tmp_path, monkeypatch) -> str:
    url = f"sqlite:///{tmp_path / 'demo.db'}"
    monkeypatch.setenv("AMI_DATABASE_URL", url)
    return url


def _consultar(url: str, rota: str) -> dict | list:
    with TestClient(create_app(Configuracao(database_url=url))) as cliente:
        resposta = cliente.get(rota)
        assert resposta.status_code == 200, resposta.text
        return resposta.json()


def test_carga_em_banco_vazio_gera_um_alerta_de_cada_tipo(banco_demo, capsys):
    assert main([]) == 0

    assert "Carga concluída" in capsys.readouterr().out
    assert len(_consultar(banco_demo, "/antimicrobianos")) >= 15
    painel = _consultar(banco_demo, "/alertas")
    assert {alerta["tipo"] for alerta in painel["alertas"]} == set(TipoAlerta)


def test_carga_alimenta_o_antibiograma_cumulativo(banco_demo):
    main([])

    relatorio = _consultar(banco_demo, "/relatorios/antibiograma-cumulativo")

    perfis = {p["microrganismo"]: p for p in relatorio["microrganismos"]}
    linhas = {a["antimicrobiano"]: a for a in perfis["Escherichia coli"]["antimicrobianos"]}
    assert perfis["Escherichia coli"]["isolados"] >= 30
    assert linhas["Gentamicina"]["amostra_suficiente"] is True
    assert linhas["Piperacilina + tazobactam"]["testados"] < 30
    assert linhas["Piperacilina + tazobactam"]["amostra_suficiente"] is False


def test_execucao_repetida_nao_duplica_registros(banco_demo, capsys):
    main([])
    antes = len(_consultar(banco_demo, "/culturas"))
    capsys.readouterr()

    assert main([]) == 0

    assert "já possui dados" in capsys.readouterr().out
    assert len(_consultar(banco_demo, "/culturas")) == antes


def test_reset_recria_apenas_os_dados_de_demonstracao(banco_demo):
    main([])
    antes = len(_consultar(banco_demo, "/prescricoes"))

    assert main(["--reset"]) == 0

    assert len(_consultar(banco_demo, "/prescricoes")) == antes
