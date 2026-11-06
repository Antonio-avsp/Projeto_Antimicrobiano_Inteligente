"""Catálogo de antimicrobianos — US01 e US02 (RF01, RF02, RN01–RN03)."""

import pytest

# --- US01: cadastrar antimicrobiano -------------------------------------------------------------


def test_cadastro_valido_retorna_201_com_id_e_ativo(client):
    resposta = client.post(
        "/antimicrobianos",
        json={
            "nome": "Ceftriaxona",
            "classe": "Cefalosporina de 3ª geração",
            "categoria_aware": "WATCH",
            "uso_restrito": False,
        },
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["id"] > 0
    assert corpo["nome"] == "Ceftriaxona"
    assert corpo["categoria_aware"] == "WATCH"
    assert corpo["ativo"] is True


@pytest.mark.parametrize("nome_repetido", ["CEFTRIAXONA", "  ceftriaxona  ", "Ceftriaxôna"])
def test_nome_duplicado_ignorando_maiusculas_acentos_e_espacos_retorna_409(
    client, novo_antimicrobiano, nome_repetido
):
    novo_antimicrobiano(nome="Ceftriaxona")

    resposta = client.post(
        "/antimicrobianos",
        json={"nome": nome_repetido, "classe": "Cefalosporina", "categoria_aware": "WATCH"},
    )

    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "Já existe um antimicrobiano com este nome."


def test_categoria_aware_invalida_retorna_422_indicando_o_campo(client):
    resposta = client.post(
        "/antimicrobianos",
        json={"nome": "Teste", "classe": "Classe", "categoria_aware": "XYZ"},
    )

    assert resposta.status_code == 422
    assert resposta.json()["detail"][0]["loc"] == ["body", "categoria_aware"]


@pytest.mark.parametrize("campo", ["nome", "classe", "categoria_aware"])
def test_campos_obrigatorios(client, campo):
    dados = {"nome": "Amoxicilina", "classe": "Penicilina", "categoria_aware": "ACCESS"}
    del dados[campo]

    resposta = client.post("/antimicrobianos", json=dados)

    assert resposta.status_code == 422


def test_nome_curto_demais_retorna_422(client):
    resposta = client.post(
        "/antimicrobianos", json={"nome": " A ", "classe": "Classe", "categoria_aware": "ACCESS"}
    )

    assert resposta.status_code == 422


# --- US02: consultar e manter o catálogo -------------------------------------------------------


def test_filtrar_por_categoria_e_uso_restrito(client, novo_antimicrobiano):
    novo_antimicrobiano(nome="Amoxicilina", classe="Penicilina", categoria_aware="ACCESS")
    novo_antimicrobiano(nome="Ceftriaxona", categoria_aware="WATCH", uso_restrito=False)
    novo_antimicrobiano(nome="Meropenem", classe="Carbapenêmico", uso_restrito=True)
    novo_antimicrobiano(
        nome="Polimixina B", classe="Polimixina", categoria_aware="RESERVE", uso_restrito=True
    )

    resposta = client.get(
        "/antimicrobianos", params={"categoria_aware": "WATCH", "uso_restrito": True}
    )

    assert resposta.status_code == 200
    assert [item["nome"] for item in resposta.json()] == ["Meropenem"]


def test_listagem_ordenada_por_nome_e_busca_sem_acentos(client, novo_antimicrobiano):
    novo_antimicrobiano(nome="Vancomicina", classe="Glicopeptídeo")
    novo_antimicrobiano(nome="Cefazolina", classe="Cefalosporina de 1ª geração")
    novo_antimicrobiano(nome="Ceftriaxona")

    todos = client.get("/antimicrobianos").json()
    busca = client.get("/antimicrobianos", params={"busca": "CÉF"}).json()

    assert [item["nome"] for item in todos] == ["Cefazolina", "Ceftriaxona", "Vancomicina"]
    assert [item["nome"] for item in busca] == ["Cefazolina", "Ceftriaxona"]


def test_atualizar_uso_restrito(client, novo_antimicrobiano):
    vancomicina = novo_antimicrobiano(nome="Vancomicina", classe="Glicopeptídeo")

    resposta = client.patch(f"/antimicrobianos/{vancomicina['id']}", json={"uso_restrito": True})

    assert resposta.status_code == 200
    consulta = client.get(f"/antimicrobianos/{vancomicina['id']}").json()
    assert consulta["uso_restrito"] is True
    assert consulta["nome"] == "Vancomicina"


def test_atualizar_nome_para_um_ja_existente_retorna_409(client, novo_antimicrobiano):
    novo_antimicrobiano(nome="Cefazolina", classe="Cefalosporina de 1ª geração")
    ceftriaxona = novo_antimicrobiano(nome="Ceftriaxona")

    resposta = client.patch(f"/antimicrobianos/{ceftriaxona['id']}", json={"nome": "cefazolina"})

    assert resposta.status_code == 409


def test_atualizar_mantendo_o_proprio_nome_e_permitido(client, novo_antimicrobiano):
    ceftriaxona = novo_antimicrobiano(nome="Ceftriaxona")

    resposta = client.patch(f"/antimicrobianos/{ceftriaxona['id']}", json={"nome": "CEFTRIAXONA"})

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "CEFTRIAXONA"


def test_atualizar_com_nulo_em_campo_obrigatorio_retorna_422(client, novo_antimicrobiano):
    ceftriaxona = novo_antimicrobiano()

    resposta = client.patch(f"/antimicrobianos/{ceftriaxona['id']}", json={"classe": None})

    assert resposta.status_code == 422


def test_inativar_preserva_historico_e_remove_da_listagem_padrao(client, novo_antimicrobiano):
    cefalotina = novo_antimicrobiano(nome="Cefalotina", classe="Cefalosporina de 1ª geração")

    resposta = client.delete(f"/antimicrobianos/{cefalotina['id']}")

    assert resposta.status_code == 204
    assert client.get(f"/antimicrobianos/{cefalotina['id']}").json()["ativo"] is False
    assert client.get("/antimicrobianos").json() == []
    inativos = client.get("/antimicrobianos", params={"ativo": False}).json()
    assert [item["nome"] for item in inativos] == ["Cefalotina"]


def test_reativar_pelo_patch(client, novo_antimicrobiano):
    cefalotina = novo_antimicrobiano(nome="Cefalotina", classe="Cefalosporina de 1ª geração")
    client.delete(f"/antimicrobianos/{cefalotina['id']}")

    resposta = client.patch(f"/antimicrobianos/{cefalotina['id']}", json={"ativo": True})

    assert resposta.json()["ativo"] is True


@pytest.mark.parametrize("metodo", ["get", "patch", "delete"])
def test_antimicrobiano_inexistente_retorna_404(client, metodo):
    kwargs = {"json": {"uso_restrito": True}} if metodo == "patch" else {}

    resposta = getattr(client, metodo)("/antimicrobianos/999", **kwargs)

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Antimicrobiano 999 não encontrado."
