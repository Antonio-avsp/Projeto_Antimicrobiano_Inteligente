"""Testes do endpoint de saúde e da documentação interativa (#6)."""

from antimicrobiano import __version__


def test_health_responde_ok_com_versao(client):
    resposta = client.get("/health")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "ok"
    assert corpo["versao"] == __version__
    assert "não substitui o julgamento clínico" in corpo["aviso"]


def test_documentacao_openapi_disponivel(client):
    assert client.get("/docs").status_code == 200
    esquema = client.get("/openapi.json").json()
    assert esquema["info"]["title"] == "Antimicrobiano Inteligente"


def test_raiz_redireciona_para_documentacao(client):
    resposta = client.get("/", follow_redirects=False)

    assert resposta.status_code == 307
    assert resposta.headers["location"] == "/docs"
