"""Interface web do painel de alertas — US18 (RF18)."""

import pytest

SEM_TOKEN = {"Authorization": ""}


def test_pagina_do_painel_e_publica(client):
    resposta = client.get("/painel", headers=SEM_TOKEN)

    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/html")
    assert "Painel de alertas" in resposta.text
    assert 'id="form-login"' in resposta.text


@pytest.mark.parametrize(
    ("arquivo", "tipo"), [("painel.js", "javascript"), ("painel.css", "text/css")]
)
def test_arquivos_estaticos(client, arquivo, tipo):
    resposta = client.get(f"/painel/static/{arquivo}", headers=SEM_TOKEN)

    assert resposta.status_code == 200
    assert tipo in resposta.headers["content-type"]


def test_painel_consome_a_api_com_token_e_agrupa_por_severidade(client):
    script = client.get("/painel/static/painel.js").text

    assert "/auth/login" in script and "/alertas?" in script
    assert "Authorization: `Bearer ${token}`" in script
    for severidade in ("ALTA", "MEDIA", "BAIXA"):
        assert f'valor: "{severidade}"' in script


def test_severidade_nao_depende_apenas_de_cor(client):
    """Acessibilidade: cada severidade tem ícone e texto, além da cor."""
    script = client.get("/painel/static/painel.js").text

    for icone, rotulo in (("▲", "Alta"), ("●", "Média"), ("▼", "Baixa")):
        assert f'rotulo: "{rotulo}", icone: "{icone}"' in script


def test_conteudo_da_api_e_inserido_como_texto(client):
    """Mensagens e evidências vêm da API e não podem ser interpretadas como HTML."""
    script = client.get("/painel/static/painel.js").text

    assert "innerHTML" not in script


def test_pagina_nao_aparece_no_openapi(client):
    assert "/painel" not in client.get("/openapi.json").json()["paths"]
