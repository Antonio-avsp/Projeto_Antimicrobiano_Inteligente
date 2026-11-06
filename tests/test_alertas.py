"""Painel de alertas via API — US07, US08 e US13 (RF07, RF08, RF13, RNF10)."""

import pytest


@pytest.fixture
def alertas(client):
    def _consultar(**params) -> dict:
        resposta = client.get("/alertas", params=params)
        assert resposta.status_code == 200, resposta.text
        return resposta.json()

    return _consultar


def _tipos(painel: dict, prescricao_id: int) -> set[str]:
    return {a["tipo"] for a in painel["alertas"] if a["prescricao_id"] == prescricao_id}


def test_timeout_aparece_no_painel_com_72_horas(nova_prescricao, alertas):
    prescricao = nova_prescricao(data_inicio="2026-11-01")

    painel = alertas(data_referencia="2026-11-04")

    assert "TIMEOUT_REAVALIACAO" in _tipos(painel, prescricao["id"])
    assert painel["data_referencia"] == "2026-11-04"


def test_reavaliacao_registrada_encerra_o_alerta_de_timeout(client, nova_prescricao, alertas):
    prescricao = nova_prescricao(data_inicio="2026-11-01")
    client.post(
        f"/prescricoes/{prescricao['id']}/reavaliacoes",
        json={"conduta": "MANTER", "data_reavaliacao": "2026-11-03"},
    )

    painel = alertas(data_referencia="2026-11-04")

    assert "TIMEOUT_REAVALIACAO" not in _tipos(painel, prescricao["id"])


def test_duracao_excedida_e_profilaxia_prolongada(nova_prescricao, alertas):
    excedida = nova_prescricao(data_inicio="2026-11-01", duracao_prevista_dias=3)
    profilaxia = nova_prescricao(
        data_inicio="2026-11-01", indicacao="PROFILAXIA", duracao_prevista_dias=3
    )
    no_prazo = nova_prescricao(data_inicio="2026-11-01", duracao_prevista_dias=7)

    painel = alertas(data_referencia="2026-11-05")

    duracao = next(
        a
        for a in painel["alertas"]
        if a["prescricao_id"] == excedida["id"] and a["tipo"] == "DURACAO_EXCEDIDA"
    )
    assert duracao["evidencias"]["dia_de_terapia"] == 5
    assert "PROFILAXIA_PROLONGADA" in _tipos(painel, profilaxia["id"])
    assert "DURACAO_EXCEDIDA" not in _tipos(painel, no_prazo["id"])


def test_prescricao_encerrada_nao_gera_alertas(client, nova_prescricao, alertas):
    prescricao = nova_prescricao(data_inicio="2026-11-01", duracao_prevista_dias=3)
    client.post(
        f"/prescricoes/{prescricao['id']}/encerramento",
        json={"status_final": "CONCLUIDA", "data_fim": "2026-11-03"},
    )

    painel = alertas(data_referencia="2026-11-05")

    assert _tipos(painel, prescricao["id"]) == set()


def test_alerta_e_explicavel(nova_prescricao, alertas):
    nova_prescricao(data_inicio="2026-11-01")

    alerta = alertas(data_referencia="2026-11-04")["alertas"][0]

    for campo in ("tipo", "severidade", "mensagem", "recomendacao", "evidencias"):
        assert alerta[campo]
    assert {"paciente_codigo", "setor", "antimicrobiano"} <= alerta.keys()


def test_painel_vazio_e_aviso_de_apoio_a_decisao(alertas):
    painel = alertas()

    assert painel["total"] == 0
    assert painel["alertas"] == []
    assert "não substitui o julgamento clínico" in painel["aviso"]


def test_data_de_referencia_invalida_retorna_422(client):
    assert client.get("/alertas", params={"data_referencia": "04/11/2026"}).status_code == 422
