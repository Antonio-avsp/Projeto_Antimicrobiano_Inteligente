"""Prescrições — US03 e US04 (RF03, RF04, RN02, RN04–RN07, RNF04)."""

from datetime import date, timedelta

import pytest


def _payload(antimicrobiano_id: int, **campos) -> dict:
    return {
        "paciente_codigo": "PAC-0001",
        "setor": "Clínica Médica",
        "antimicrobiano_id": antimicrobiano_id,
        "dose": "1 g",
        "intervalo_horas": 24,
        "via": "IV",
        "indicacao": "EMPIRICA",
        "diagnostico": "Pneumonia comunitária",
        "data_inicio": "2026-11-01",
        "duracao_prevista_dias": 7,
    } | campos


# --- US03: registrar prescrição ----------------------------------------------------------------


def test_registro_valido_retorna_201_com_status_ativa(client, novo_antimicrobiano):
    ceftriaxona = novo_antimicrobiano(nome="Ceftriaxona")

    resposta = client.post("/prescricoes", json=_payload(ceftriaxona["id"]))

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["status"] == "ATIVA"
    assert corpo["paciente_codigo"] == "PAC-0001"
    assert corpo["antimicrobiano"]["nome"] == "Ceftriaxona"
    assert corpo["antimicrobiano"]["categoria_aware"] == "WATCH"
    assert corpo["justificativa"] is None


@pytest.mark.parametrize("codigo", ["João da Silva", "PAC-12", "pac-0001", "123.456.789-09"])
def test_codigo_de_paciente_fora_do_padrao_pseudonimizado_retorna_422(
    client, novo_antimicrobiano, codigo
):
    antimicrobiano = novo_antimicrobiano()

    resposta = client.post(
        "/prescricoes", json=_payload(antimicrobiano["id"], paciente_codigo=codigo)
    )

    assert resposta.status_code == 422
    assert resposta.json()["campos"][0]["campo"] == "paciente_codigo"


def test_antimicrobiano_inativo_nao_pode_ser_prescrito(client, novo_antimicrobiano):
    cefalotina = novo_antimicrobiano(nome="Cefalotina", classe="Cefalosporina de 1ª geração")
    client.delete(f"/antimicrobianos/{cefalotina['id']}")

    resposta = client.post("/prescricoes", json=_payload(cefalotina["id"]))

    assert resposta.status_code == 422
    assert resposta.json()["mensagem"] == "Antimicrobiano inativo não pode ser prescrito."


def test_antimicrobiano_inexistente_retorna_404(client):
    resposta = client.post("/prescricoes", json=_payload(999))

    assert resposta.status_code == 404


@pytest.mark.parametrize(
    "campos",
    [
        {"data_inicio": (date.today() + timedelta(days=1)).isoformat()},
        {"duracao_prevista_dias": 0},
        {"duracao_prevista_dias": 91},
        {"intervalo_horas": 0},
        {"intervalo_horas": 169},
        {"via": "SC"},
        {"indicacao": "TERAPEUTICA"},
    ],
)
def test_dados_fora_dos_limites_retornam_422(client, novo_antimicrobiano, campos):
    antimicrobiano = novo_antimicrobiano()

    resposta = client.post("/prescricoes", json=_payload(antimicrobiano["id"], **campos))

    assert resposta.status_code == 422


def test_justificativa_em_branco_e_armazenada_como_nula(client, novo_antimicrobiano):
    antimicrobiano = novo_antimicrobiano()

    resposta = client.post("/prescricoes", json=_payload(antimicrobiano["id"], justificativa="   "))

    assert resposta.json()["justificativa"] is None


# --- US04: consultar e atualizar prescrições ---------------------------------------------------


def test_filtrar_ativas_por_setor(client, nova_prescricao):
    uti = nova_prescricao(setor="UTI Adulto", paciente_codigo="PAC-0001")
    nova_prescricao(setor="Clínica Médica", paciente_codigo="PAC-0002")

    resposta = client.get("/prescricoes", params={"status": "ATIVA", "setor": "UTI Adulto"})

    assert resposta.status_code == 200
    assert [item["id"] for item in resposta.json()] == [uti["id"]]


def test_filtrar_por_paciente_e_ordenar_da_mais_recente(client, nova_prescricao):
    antiga = nova_prescricao(paciente_codigo="PAC-0003", data_inicio="2026-10-20")
    recente = nova_prescricao(paciente_codigo="PAC-0003", data_inicio="2026-11-02")
    nova_prescricao(paciente_codigo="PAC-0004")

    resposta = client.get("/prescricoes", params={"paciente_codigo": "PAC-0003"})

    assert [item["id"] for item in resposta.json()] == [recente["id"], antiga["id"]]


def test_filtro_de_paciente_invalido_retorna_422(client):
    assert client.get("/prescricoes", params={"paciente_codigo": "Maria"}).status_code == 422


def test_consultar_detalhe_com_dia_de_terapia(client, nova_prescricao):
    tres_dias_atras = (date.today() - timedelta(days=3)).isoformat()
    prescricao = nova_prescricao(data_inicio=tres_dias_atras)

    resposta = client.get(f"/prescricoes/{prescricao['id']}")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["dia_de_terapia"] == 4
    assert corpo["antimicrobiano"]["categoria_aware"] == "WATCH"


def test_atualizar_justificativa(client, novo_antimicrobiano, nova_prescricao):
    meropenem = novo_antimicrobiano(nome="Meropenem", classe="Carbapenêmico", uso_restrito=True)
    prescricao = nova_prescricao(antimicrobiano_id=meropenem["id"])

    resposta = client.patch(
        f"/prescricoes/{prescricao['id']}",
        json={"justificativa": "Choque séptico com suspeita de ESBL"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["justificativa"] == "Choque séptico com suspeita de ESBL"


def test_justificativa_pode_ser_removida_com_nulo(client, nova_prescricao):
    prescricao = nova_prescricao(justificativa="Motivo")

    resposta = client.patch(f"/prescricoes/{prescricao['id']}", json={"justificativa": None})

    assert resposta.json()["justificativa"] is None


def test_atualizar_campo_obrigatorio_com_nulo_retorna_422(client, nova_prescricao):
    prescricao = nova_prescricao()

    resposta = client.patch(f"/prescricoes/{prescricao['id']}", json={"setor": None})

    assert resposta.status_code == 422


@pytest.mark.parametrize("metodo", ["get", "patch"])
def test_prescricao_inexistente_retorna_404(client, metodo):
    kwargs = {"json": {"dose": "2 g"}} if metodo == "patch" else {}

    resposta = getattr(client, metodo)("/prescricoes/999", **kwargs)

    assert resposta.status_code == 404
    assert resposta.json()["mensagem"] == "Prescrição 999 não encontrada."
