"""Reavaliação (time-out) e encerramento — US05 (RF05, RN08, RN09)."""

from datetime import date, timedelta

import pytest

HOJE = date.today()


def _dias_atras(dias: int) -> str:
    return (HOJE - timedelta(days=dias)).isoformat()


def test_registrar_reavaliacao_e_consultar_historico(client, nova_prescricao):
    prescricao = nova_prescricao(data_inicio=_dias_atras(3))

    resposta = client.post(
        f"/prescricoes/{prescricao['id']}/reavaliacoes",
        json={"conduta": "MANTER", "observacao": "Melhora clínica; manter até D7."},
    )

    assert resposta.status_code == 201
    reavaliacao = resposta.json()
    assert reavaliacao["conduta"] == "MANTER"
    assert reavaliacao["data_reavaliacao"] == HOJE.isoformat()
    historico = client.get(f"/prescricoes/{prescricao['id']}/reavaliacoes").json()
    assert [item["id"] for item in historico] == [reavaliacao["id"]]
    detalhe = client.get(f"/prescricoes/{prescricao['id']}").json()
    assert detalhe["reavaliacoes"][0]["conduta"] == "MANTER"


def test_historico_em_ordem_cronologica(client, nova_prescricao):
    prescricao = nova_prescricao(data_inicio=_dias_atras(5))
    url = f"/prescricoes/{prescricao['id']}/reavaliacoes"
    client.post(url, json={"conduta": "AJUSTAR", "data_reavaliacao": _dias_atras(1)})
    client.post(url, json={"conduta": "MANTER", "data_reavaliacao": _dias_atras(3)})

    condutas = [item["conduta"] for item in client.get(url).json()]

    assert condutas == ["MANTER", "AJUSTAR"]


def test_encerrar_prescricao_como_concluida(client, nova_prescricao):
    prescricao = nova_prescricao(data_inicio=_dias_atras(6))

    resposta = client.post(
        f"/prescricoes/{prescricao['id']}/encerramento",
        json={"status_final": "CONCLUIDA", "data_fim": _dias_atras(1), "motivo": "Curso completo"},
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "CONCLUIDA"
    assert corpo["data_fim"] == _dias_atras(1)
    assert corpo["motivo_encerramento"] == "Curso completo"
    assert corpo["dia_de_terapia"] == 6


def test_encerrar_como_suspensa_usa_hoje_por_padrao(client, nova_prescricao):
    prescricao = nova_prescricao()

    resposta = client.post(
        f"/prescricoes/{prescricao['id']}/encerramento", json={"status_final": "SUSPENSA"}
    )

    assert resposta.json()["status"] == "SUSPENSA"
    assert resposta.json()["data_fim"] == HOJE.isoformat()


@pytest.mark.parametrize(
    ("metodo", "rota", "corpo"),
    [
        ("post", "reavaliacoes", {"conduta": "MANTER"}),
        ("post", "encerramento", {"status_final": "SUSPENSA"}),
        ("patch", "", {"dose": "2 g"}),
    ],
)
def test_operacoes_em_prescricao_encerrada_retornam_409(
    client, nova_prescricao, metodo, rota, corpo
):
    prescricao = nova_prescricao()
    client.post(f"/prescricoes/{prescricao['id']}/encerramento", json={"status_final": "CONCLUIDA"})

    url = f"/prescricoes/{prescricao['id']}" + (f"/{rota}" if rota else "")
    resposta = getattr(client, metodo)(url, json=corpo)

    assert resposta.status_code == 409
    assert "CONCLUIDA" in resposta.json()["detail"]


@pytest.mark.parametrize(
    ("rota", "corpo"),
    [
        ("reavaliacoes", {"conduta": "MANTER", "data_reavaliacao": _dias_atras(10)}),
        ("encerramento", {"status_final": "CONCLUIDA", "data_fim": _dias_atras(10)}),
    ],
)
def test_data_anterior_ao_inicio_retorna_422(client, nova_prescricao, rota, corpo):
    prescricao = nova_prescricao(data_inicio=_dias_atras(2))

    resposta = client.post(f"/prescricoes/{prescricao['id']}/{rota}", json=corpo)

    assert resposta.status_code == 422
    assert "anterior ao início da prescrição" in resposta.json()["detail"]


@pytest.mark.parametrize(
    ("rota", "corpo"),
    [
        ("reavaliacoes", {"conduta": "MANTER", "data_reavaliacao": _dias_atras(-1)}),
        ("encerramento", {"status_final": "CONCLUIDA", "data_fim": _dias_atras(-1)}),
        ("reavaliacoes", {"conduta": "OBSERVAR"}),
        ("encerramento", {"status_final": "ATIVA"}),
    ],
)
def test_data_futura_ou_valores_invalidos_retornam_422(client, nova_prescricao, rota, corpo):
    prescricao = nova_prescricao()

    resposta = client.post(f"/prescricoes/{prescricao['id']}/{rota}", json=corpo)

    assert resposta.status_code == 422


@pytest.mark.parametrize(
    ("metodo", "rota", "corpo"),
    [
        ("post", "reavaliacoes", {"conduta": "MANTER"}),
        ("get", "reavaliacoes", None),
        ("post", "encerramento", {"status_final": "CONCLUIDA"}),
    ],
)
def test_prescricao_inexistente_retorna_404(client, metodo, rota, corpo):
    kwargs = {"json": corpo} if corpo else {}

    resposta = getattr(client, metodo)(f"/prescricoes/999/{rota}", **kwargs)

    assert resposta.status_code == 404
