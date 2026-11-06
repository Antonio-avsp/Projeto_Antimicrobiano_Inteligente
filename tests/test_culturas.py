"""Culturas e antibiogramas — US06 (RF06, RN10, RNF04)."""

from datetime import date, timedelta

import pytest

HOJE = date.today()


@pytest.fixture
def antimicrobianos(novo_antimicrobiano) -> dict[str, int]:
    return {
        "ceftriaxona": novo_antimicrobiano(nome="Ceftriaxona")["id"],
        "gentamicina": novo_antimicrobiano(
            nome="Gentamicina", classe="Aminoglicosídeo", categoria_aware="ACCESS"
        )["id"],
    }


def test_registrar_coleta_retorna_201_pendente(client):
    resposta = client.post(
        "/culturas",
        json={"paciente_codigo": "PAC-0001", "setor": "UTI Adulto", "material": "SANGUE"},
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["status"] == "PENDENTE"
    assert corpo["data_coleta"] == HOJE.isoformat()
    assert corpo["antibiograma"] == []


def test_resultado_positivo_com_antibiograma(client, nova_cultura, antimicrobianos):
    cultura = nova_cultura()

    resposta = client.put(
        f"/culturas/{cultura['id']}/resultado",
        json={
            "resultado": "POSITIVA",
            "microrganismo": "  Escherichia   coli ",
            "antibiograma": [
                {"antimicrobiano_id": antimicrobianos["ceftriaxona"], "interpretacao": "R"},
                {"antimicrobiano_id": antimicrobianos["gentamicina"], "interpretacao": "S"},
            ],
        },
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "POSITIVA"
    assert corpo["microrganismo"] == "Escherichia coli"
    assert corpo["data_resultado"] == HOJE.isoformat()
    assert {(i["antimicrobiano"]["nome"], i["interpretacao"]) for i in corpo["antibiograma"]} == {
        ("Ceftriaxona", "R"),
        ("Gentamicina", "S"),
    }


def test_resultado_negativo(client, nova_cultura):
    cultura = nova_cultura()

    resposta = client.put(f"/culturas/{cultura['id']}/resultado", json={"resultado": "NEGATIVA"})

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "NEGATIVA"
    assert resposta.json()["microrganismo"] is None


def test_correcao_substitui_o_resultado_anterior(client, nova_cultura, antimicrobianos):
    gentamicina = antimicrobianos["gentamicina"]
    cultura = nova_cultura(
        resultado={
            "resultado": "POSITIVA",
            "microrganismo": "Escherichia coli",
            "antibiograma": [{"antimicrobiano_id": gentamicina, "interpretacao": "S"}],
        }
    )

    resposta = client.put(
        f"/culturas/{cultura['id']}/resultado",
        json={
            "resultado": "POSITIVA",
            "microrganismo": "Klebsiella pneumoniae",
            "antibiograma": [{"antimicrobiano_id": gentamicina, "interpretacao": "R"}],
        },
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["microrganismo"] == "Klebsiella pneumoniae"
    assert [(i["antimicrobiano"]["id"], i["interpretacao"]) for i in corpo["antibiograma"]] == [
        (gentamicina, "R")
    ]


@pytest.mark.parametrize(
    "resultado",
    [
        {"resultado": "POSITIVA"},
        {"resultado": "POSITIVA", "microrganismo": "   "},
        {"resultado": "NEGATIVA", "microrganismo": "Escherichia coli"},
        {"resultado": "PENDENTE"},
        {"resultado": "POSITIVA", "microrganismo": "E. coli", "data_resultado": "2999-01-01"},
    ],
)
def test_resultado_inconsistente_retorna_422(client, nova_cultura, resultado):
    cultura = nova_cultura()

    resposta = client.put(f"/culturas/{cultura['id']}/resultado", json=resultado)

    assert resposta.status_code == 422


def test_antimicrobiano_repetido_no_antibiograma_retorna_422(client, nova_cultura, antimicrobianos):
    cultura = nova_cultura()
    item = {"antimicrobiano_id": antimicrobianos["gentamicina"], "interpretacao": "S"}

    resposta = client.put(
        f"/culturas/{cultura['id']}/resultado",
        json={"resultado": "POSITIVA", "microrganismo": "E. coli", "antibiograma": [item, item]},
    )

    assert resposta.status_code == 422


def test_negativa_com_antibiograma_retorna_422(client, nova_cultura, antimicrobianos):
    cultura = nova_cultura()
    item = {"antimicrobiano_id": antimicrobianos["gentamicina"], "interpretacao": "S"}

    resposta = client.put(
        f"/culturas/{cultura['id']}/resultado",
        json={"resultado": "NEGATIVA", "antibiograma": [item]},
    )

    assert resposta.status_code == 422


def test_antimicrobiano_inexistente_no_antibiograma_retorna_422(client, nova_cultura):
    cultura = nova_cultura()

    resposta = client.put(
        f"/culturas/{cultura['id']}/resultado",
        json={
            "resultado": "POSITIVA",
            "microrganismo": "E. coli",
            "antibiograma": [{"antimicrobiano_id": 999, "interpretacao": "S"}],
        },
    )

    assert resposta.status_code == 422
    assert "999" in resposta.json()["detail"]


def test_data_do_resultado_anterior_a_coleta_retorna_422(client, nova_cultura):
    cultura = nova_cultura(data_coleta=(HOJE - timedelta(days=1)).isoformat())

    resposta = client.put(
        f"/culturas/{cultura['id']}/resultado",
        json={"resultado": "NEGATIVA", "data_resultado": (HOJE - timedelta(days=3)).isoformat()},
    )

    assert resposta.status_code == 422
    assert "anterior à coleta" in resposta.json()["detail"]


@pytest.mark.parametrize(
    "dados",
    [
        {"paciente_codigo": "Maria", "setor": "UTI Adulto", "material": "SANGUE"},
        {"paciente_codigo": "PAC-0001", "setor": "UTI Adulto", "material": "SALIVA"},
        {
            "paciente_codigo": "PAC-0001",
            "setor": "UTI Adulto",
            "material": "URINA",
            "data_coleta": (HOJE + timedelta(days=1)).isoformat(),
        },
    ],
)
def test_coleta_invalida_retorna_422(client, dados):
    assert client.post("/culturas", json=dados).status_code == 422


def test_listar_culturas_por_paciente_da_mais_recente(client, nova_cultura):
    antiga = nova_cultura(data_coleta=(HOJE - timedelta(days=5)).isoformat())
    recente = nova_cultura(data_coleta=(HOJE - timedelta(days=1)).isoformat(), material="URINA")
    nova_cultura(paciente_codigo="PAC-0002")

    resposta = client.get("/culturas", params={"paciente_codigo": "PAC-0001"})

    assert [item["id"] for item in resposta.json()] == [recente["id"], antiga["id"]]


def test_listar_culturas_por_status(client, nova_cultura):
    nova_cultura()
    negativa = nova_cultura(resultado={"resultado": "NEGATIVA"})

    resposta = client.get("/culturas", params={"status": "NEGATIVA"})

    assert [item["id"] for item in resposta.json()] == [negativa["id"]]


@pytest.mark.parametrize("metodo", ["get", "put"])
def test_cultura_inexistente_retorna_404(client, metodo):
    url = "/culturas/999" + ("/resultado" if metodo == "put" else "")
    kwargs = {"json": {"resultado": "NEGATIVA"}} if metodo == "put" else {}

    resposta = getattr(client, metodo)(url, **kwargs)

    assert resposta.status_code == 404
