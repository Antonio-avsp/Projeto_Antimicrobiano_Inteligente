"""Antibiograma cumulativo — US14 (RF14, RN19)."""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from antimicrobiano.config import Configuracao, ParametrosClinicos
from antimicrobiano.enums import Perfil
from antimicrobiano.main import create_app
from tests.conftest import cabecalho_de, criar_usuario

URL = "/relatorios/antibiograma-cumulativo"
PERIODO = {"inicio": "2026-10-01", "fim": "2026-10-31"}


@pytest.fixture
def gentamicina(novo_antimicrobiano) -> int:
    return novo_antimicrobiano(
        nome="Gentamicina", classe="Aminoglicosídeo", categoria_aware="ACCESS"
    )["id"]


def _positiva(microrganismo: str, antibiograma: dict[int, str]) -> dict:
    return {
        "resultado": "POSITIVA",
        "microrganismo": microrganismo,
        "data_resultado": "2026-10-31",
        "antibiograma": [
            {"antimicrobiano_id": am_id, "interpretacao": interp}
            for am_id, interp in antibiograma.items()
        ],
    }


def _linha(relatorio: dict, microrganismo: str, antimicrobiano: str) -> dict:
    perfil = next(p for p in relatorio["microrganismos"] if p["microrganismo"] == microrganismo)
    return next(a for a in perfil["antimicrobianos"] if a["antimicrobiano"] == antimicrobiano)


def test_percentual_de_sensibilidade(client, nova_cultura, gentamicina):
    for i, interpretacao in enumerate(["S", "S", "S", "R"], start=1):
        nova_cultura(
            paciente_codigo=f"PAC-000{i}",
            data_coleta=f"2026-10-0{i}",
            resultado=_positiva("Escherichia coli", {gentamicina: interpretacao}),
        )

    relatorio = client.get(URL, params=PERIODO).json()

    linha = _linha(relatorio, "Escherichia coli", "Gentamicina")
    assert (linha["testados"], linha["sensiveis"], linha["resistentes"]) == (4, 3, 1)
    assert linha["percentual_sensivel"] == 75.0
    assert relatorio["total_isolados"] == 4


def test_somente_o_primeiro_isolado_por_paciente(client, nova_cultura, gentamicina):
    nova_cultura(
        data_coleta="2026-10-05", resultado=_positiva("Escherichia coli", {gentamicina: "S"})
    )
    nova_cultura(
        data_coleta="2026-10-20", resultado=_positiva("escherichia COLI", {gentamicina: "R"})
    )

    relatorio = client.get(URL, params=PERIODO).json()

    assert len(relatorio["microrganismos"]) == 1
    linha = _linha(relatorio, "Escherichia coli", "Gentamicina")
    assert (linha["testados"], linha["sensiveis"]) == (1, 1)


def test_amostra_com_menos_de_30_isolados_e_sinalizada(client, nova_cultura, gentamicina):
    nova_cultura(
        data_coleta="2026-10-05", resultado=_positiva("Escherichia coli", {gentamicina: "S"})
    )

    relatorio = client.get(URL, params=PERIODO).json()

    assert relatorio["minimo_isolados"] == 30
    assert _linha(relatorio, "Escherichia coli", "Gentamicina")["amostra_suficiente"] is False


def test_minimo_de_isolados_configuravel():
    config = Configuracao(
        database_url="sqlite://", parametros=ParametrosClinicos(minimo_isolados=2)
    )
    app = create_app(config)
    with TestClient(app) as cliente:
        criar_usuario(app, "gestor.teste", Perfil.GESTOR)
        cliente.headers.update(cabecalho_de(cliente, "gestor.teste"))
        am = cliente.post(
            "/antimicrobianos",
            json={"nome": "Gentamicina", "classe": "Aminoglicosídeo", "categoria_aware": "ACCESS"},
        ).json()["id"]
        for paciente in ("PAC-0001", "PAC-0002"):
            cultura = cliente.post(
                "/culturas",
                json={
                    "paciente_codigo": paciente,
                    "setor": "UTI Adulto",
                    "material": "URINA",
                    "data_coleta": "2026-10-10",
                },
            ).json()
            cliente.put(
                f"/culturas/{cultura['id']}/resultado",
                json=_positiva("Escherichia coli", {am: "S"}),
            )
        relatorio = cliente.get(URL, params=PERIODO).json()

    assert _linha(relatorio, "Escherichia coli", "Gentamicina")["amostra_suficiente"] is True


def test_filtro_por_setor(client, nova_cultura, gentamicina):
    nova_cultura(
        setor="UTI Adulto",
        data_coleta="2026-10-05",
        resultado=_positiva("Klebsiella pneumoniae", {gentamicina: "R"}),
    )
    nova_cultura(
        paciente_codigo="PAC-0002",
        setor="Clínica Médica",
        data_coleta="2026-10-05",
        resultado=_positiva("Escherichia coli", {gentamicina: "S"}),
    )

    relatorio = client.get(URL, params=PERIODO | {"setor": "UTI Adulto"}).json()

    assert [p["microrganismo"] for p in relatorio["microrganismos"]] == ["Klebsiella pneumoniae"]
    assert relatorio["setor"] == "UTI Adulto"


def test_considera_apenas_culturas_positivas_do_periodo(client, nova_cultura, gentamicina):
    nova_cultura(
        data_coleta="2026-09-30", resultado=_positiva("Escherichia coli", {gentamicina: "S"})
    )
    nova_cultura(
        paciente_codigo="PAC-0002", data_coleta="2026-10-10", resultado={"resultado": "NEGATIVA"}
    )
    nova_cultura(paciente_codigo="PAC-0003", data_coleta="2026-10-10")

    relatorio = client.get(URL, params=PERIODO).json()

    assert relatorio["microrganismos"] == []
    assert relatorio["total_isolados"] == 0


def test_microrganismos_ordenados_por_numero_de_isolados(client, nova_cultura, gentamicina):
    nova_cultura(data_coleta="2026-10-01", resultado=_positiva("Staphylococcus aureus", {}))
    for i in (2, 3):
        nova_cultura(
            paciente_codigo=f"PAC-000{i}",
            data_coleta="2026-10-01",
            resultado=_positiva("Escherichia coli", {gentamicina: "S"}),
        )

    relatorio = client.get(URL, params=PERIODO).json()

    assert [(p["microrganismo"], p["isolados"]) for p in relatorio["microrganismos"]] == [
        ("Escherichia coli", 2),
        ("Staphylococcus aureus", 1),
    ]


def test_periodo_padrao_de_doze_meses(client):
    relatorio = client.get(URL).json()

    assert relatorio["fim"] == date.today().isoformat()
    assert relatorio["inicio"] == (date.today() - timedelta(days=364)).isoformat()


@pytest.mark.parametrize(
    "params", [{"inicio": "2026-10-31", "fim": "2026-10-01"}, {"inicio": "01/10/2026"}]
)
def test_periodo_invalido_retorna_422(client, params):
    assert client.get(URL, params=params).status_code == 422
