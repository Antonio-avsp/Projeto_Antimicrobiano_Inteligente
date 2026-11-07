"""Formato único de erro da API, com mensagens em português (RNF03, RNF05)."""

from datetime import date, timedelta

import pytest

from antimicrobiano.erros import traduzir_erro_de_validacao

CHAVES = {"codigo", "mensagem", "campos", "id_requisicao"}


def _sem_id(resposta) -> dict:
    """Corpo do erro sem o identificador, conferindo que ele é o mesmo do cabeçalho."""
    corpo = resposta.json()
    assert corpo.pop("id_requisicao") == resposta.headers["X-Request-ID"]
    return corpo


def test_recurso_inexistente(client):
    resposta = client.get("/antimicrobianos/999")

    assert resposta.status_code == 404
    assert _sem_id(resposta) == {
        "codigo": "RECURSO_NAO_ENCONTRADO",
        "mensagem": "Antimicrobiano 999 não encontrado.",
        "campos": [],
    }


def test_conflito_de_unicidade(client, novo_antimicrobiano):
    novo_antimicrobiano()

    resposta = client.post(
        "/antimicrobianos",
        json={"nome": "CEFTRIAXONA", "classe": "Cefalosporina", "categoria_aware": "WATCH"},
    )

    assert resposta.status_code == 409
    assert resposta.json()["codigo"] == "CONFLITO"


def test_regra_de_negocio_violada(client, novo_antimicrobiano, nova_prescricao):
    inativo = novo_antimicrobiano(nome="Cefalotina")
    client.delete(f"/antimicrobianos/{inativo['id']}")

    resposta = client.post(
        "/prescricoes",
        json={
            "paciente_codigo": "PAC-0001",
            "setor": "UTI Adulto",
            "antimicrobiano_id": inativo["id"],
            "dose": "1 g",
            "intervalo_horas": 8,
            "via": "IV",
            "indicacao": "EMPIRICA",
            "diagnostico": "Sepse",
            "data_inicio": date.today().isoformat(),
            "duracao_prevista_dias": 7,
        },
    )

    assert resposta.status_code == 422
    assert _sem_id(resposta) == {
        "codigo": "REGRA_DE_NEGOCIO",
        "mensagem": "Antimicrobiano inativo não pode ser prescrito.",
        "campos": [],
    }


def test_validacao_indica_o_campo_com_mensagem_em_portugues(client):
    resposta = client.post(
        "/antimicrobianos", json={"nome": "Teste", "classe": "X", "categoria_aware": "XYZ"}
    )

    corpo = resposta.json()
    assert resposta.status_code == 422
    assert corpo["codigo"] == "VALIDACAO"
    assert corpo["mensagem"] == "Dados inválidos: verifique os campos informados."
    campos = {campo["campo"]: campo for campo in corpo["campos"]}
    assert campos["classe"]["mensagem"] == "Deve ter pelo menos 2 caractere(s)."
    assert campos["categoria_aware"]["local"] == "body"
    assert "use um destes" in campos["categoria_aware"]["mensagem"]


def test_campo_obrigatorio(client):
    resposta = client.post("/antimicrobianos", json={"nome": "Teste"})

    mensagens = {campo["campo"]: campo["mensagem"] for campo in resposta.json()["campos"]}
    assert mensagens["classe"] == "Campo obrigatório."


def test_mensagem_do_validador_de_dominio_sem_prefixo_em_ingles(client, novo_antimicrobiano):
    amanha = (date.today() + timedelta(days=1)).isoformat()

    resposta = client.post(
        "/prescricoes",
        json={
            "paciente_codigo": "PAC-0001",
            "setor": "UTI Adulto",
            "antimicrobiano_id": novo_antimicrobiano()["id"],
            "dose": "1 g",
            "intervalo_horas": 8,
            "via": "IV",
            "indicacao": "EMPIRICA",
            "diagnostico": "Sepse",
            "data_inicio": amanha,
            "duracao_prevista_dias": 7,
        },
    )

    campo = resposta.json()["campos"][0]
    assert (campo["campo"], campo["mensagem"]) == (
        "data_inicio",
        "A data não pode ser posterior à data atual.",
    )


def test_parametro_de_consulta_invalido(client):
    resposta = client.get("/alertas", params={"data_referencia": "05/11/2026"})

    campo = resposta.json()["campos"][0]
    assert (campo["campo"], campo["local"]) == ("data_referencia", "query")
    assert campo["mensagem"] == "Data inválida; use o formato AAAA-MM-DD."


def test_json_mal_formado(client):
    resposta = client.post(
        "/antimicrobianos", content="{nome:", headers={"Content-Type": "application/json"}
    )

    assert resposta.status_code == 422
    assert resposta.json()["campos"][0]["mensagem"] == "JSON inválido."


@pytest.mark.parametrize(
    ("metodo", "rota", "status", "codigo"),
    [
        ("get", "/rota-inexistente", 404, "RECURSO_NAO_ENCONTRADO"),
        ("put", "/health", 405, "METODO_NAO_PERMITIDO"),
    ],
)
def test_erros_http_do_framework_seguem_o_mesmo_formato(client, metodo, rota, status, codigo):
    resposta = client.request(metodo, rota)

    assert resposta.status_code == status
    assert resposta.json()["codigo"] == codigo
    assert set(resposta.json()) == CHAVES


def test_tipo_de_erro_desconhecido_mantem_a_mensagem_original():
    erro = {"type": "tipo_novo", "loc": ("body", "itens", 0, "x"), "msg": "Algo deu errado"}

    assert traduzir_erro_de_validacao(erro) == {
        "campo": "itens.0.x",
        "local": "body",
        "mensagem": "Algo deu errado",
    }


def test_openapi_documenta_o_formato_de_erro(client):
    esquema = client.get("/openapi.json").json()

    resposta_422 = esquema["paths"]["/antimicrobianos"]["post"]["responses"]["422"]
    assert resposta_422["content"]["application/json"]["schema"]["$ref"].endswith("/Erro")
    assert "HTTPValidationError" not in esquema["components"]["schemas"]
