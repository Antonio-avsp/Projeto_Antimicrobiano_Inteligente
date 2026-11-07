"""Indicadores de consumo em dias de terapia — US15 (RF15, RN23)."""

from datetime import date, timedelta

import pytest

HOJE = date.today()


def dia(n: int) -> str:
    """Data ``n`` dias antes de hoje, em ISO."""
    return (HOJE - timedelta(days=n)).isoformat()


@pytest.fixture
def catalogo(novo_antimicrobiano) -> dict[str, int]:
    return {
        "Ceftriaxona": novo_antimicrobiano()["id"],
        "Amoxicilina": novo_antimicrobiano(
            nome="Amoxicilina", classe="Penicilina", categoria_aware="ACCESS"
        )["id"],
        "Gentamicina": novo_antimicrobiano(
            nome="Gentamicina", classe="Aminoglicosídeo", categoria_aware="ACCESS"
        )["id"],
    }


@pytest.fixture
def prescrever(client, nova_prescricao):
    """Registra a prescrição e, se ``termino`` for informado, encerra nessa data."""

    def _prescrever(am_id: int, inicio: int, termino: int | None = None, **campos) -> dict:
        prescricao = nova_prescricao(am_id, data_inicio=dia(inicio), **campos)
        if termino is not None:
            resposta = client.post(
                f"/prescricoes/{prescricao['id']}/encerramento",
                json={"status_final": "CONCLUIDA", "data_fim": dia(termino)},
            )
            assert resposta.status_code == 200, resposta.text
        return prescricao

    return _prescrever


def _indicadores(client, **params) -> dict:
    resposta = client.get("/relatorios/indicadores", params=params)
    assert resposta.status_code == 200, resposta.text
    return resposta.json()


def _por_categoria(relatorio: dict) -> dict[str, int]:
    return {linha["categoria_aware"]: linha["dot"] for linha in relatorio["por_categoria"]}


def test_dot_por_categoria_e_percentual_access(client, catalogo, prescrever):
    """Cenário da US15: 5 dias de Ceftriaxona (WATCH) e 3 de Amoxicilina (ACCESS)."""
    prescrever(catalogo["Ceftriaxona"], inicio=9, termino=5, paciente_codigo="PAC-0001")
    prescrever(catalogo["Amoxicilina"], inicio=8, termino=6, paciente_codigo="PAC-0002")

    relatorio = _indicadores(client, inicio=dia(10), fim=dia(0))

    assert _por_categoria(relatorio) == {"ACCESS": 3, "WATCH": 5, "RESERVE": 0}
    assert relatorio["total_dot"] == 8
    assert relatorio["percentual_access"] == 37.5
    assert relatorio["atinge_meta_access"] is False


def test_calculo_manual_de_tres_pacientes_em_sete_dias(client, catalogo, prescrever):
    """Exemplo documentado na RN23 (docs/requisitos.md)."""
    prescrever(catalogo["Ceftriaxona"], inicio=6, termino=2, paciente_codigo="PAC-0001")  # 5
    prescrever(catalogo["Amoxicilina"], inicio=7, termino=4, paciente_codigo="PAC-0002")  # 3
    prescrever(catalogo["Ceftriaxona"], inicio=1, paciente_codigo="PAC-0003")  # 2 (ativa)
    prescrever(catalogo["Gentamicina"], inicio=0, paciente_codigo="PAC-0003")  # 1 (ativa)

    relatorio = _indicadores(client, inicio=dia(6), fim=dia(0))

    assert relatorio["total_dot"] == 11
    assert _por_categoria(relatorio) == {"ACCESS": 4, "WATCH": 7, "RESERVE": 0}
    assert relatorio["percentual_access"] == 36.4
    linhas = {linha["antimicrobiano"]: linha for linha in relatorio["por_antimicrobiano"]}
    assert (linhas["Ceftriaxona"]["dot"], linhas["Ceftriaxona"]["pacientes"]) == (7, 2)
    assert [linha["antimicrobiano"] for linha in relatorio["por_antimicrobiano"]] == [
        "Ceftriaxona",
        "Amoxicilina",
        "Gentamicina",
    ]


def test_prescricao_parcialmente_no_periodo_conta_so_os_dias_internos(client, catalogo, prescrever):
    prescrever(catalogo["Ceftriaxona"], inicio=20, termino=12)

    relatorio = _indicadores(client, inicio=dia(15), fim=dia(5))

    assert relatorio["total_dot"] == 4  # dias 15, 14, 13 e 12 antes de hoje


def test_prescricao_ativa_conta_ate_hoje_mesmo_com_periodo_futuro(client, catalogo, prescrever):
    prescrever(catalogo["Ceftriaxona"], inicio=2)
    futuro = (HOJE + timedelta(days=10)).isoformat()

    relatorio = _indicadores(client, inicio=dia(5), fim=futuro)

    assert relatorio["total_dot"] == 3


def test_mesmo_antimicrobiano_sobreposto_no_mesmo_paciente_conta_uma_vez(
    client, catalogo, prescrever
):
    prescrever(catalogo["Ceftriaxona"], inicio=6, termino=3)
    prescrever(catalogo["Ceftriaxona"], inicio=4, termino=1)

    relatorio = _indicadores(client, inicio=dia(10), fim=dia(0))

    assert relatorio["total_dot"] == 6  # dias 6 a 1 antes de hoje


def test_filtro_e_quebra_por_setor(client, catalogo, prescrever):
    prescrever(catalogo["Ceftriaxona"], inicio=2, termino=0, setor="UTI Adulto")
    prescrever(
        catalogo["Amoxicilina"],
        inicio=1,
        termino=0,
        setor="Pediatria",
        paciente_codigo="PAC-0002",
    )

    geral = _indicadores(client, inicio=dia(5), fim=dia(0))
    uti = _indicadores(client, inicio=dia(5), fim=dia(0), setor="UTI Adulto")

    assert geral["por_setor"] == [
        {"setor": "UTI Adulto", "dot": 3},
        {"setor": "Pediatria", "dot": 2},
    ]
    assert (uti["setor"], uti["total_dot"]) == ("UTI Adulto", 3)


def test_periodo_sem_consumo(client):
    relatorio = _indicadores(client)

    assert relatorio["total_dot"] == 0
    assert relatorio["percentual_access"] is None
    assert relatorio["atinge_meta_access"] is None
    assert _por_categoria(relatorio) == {"ACCESS": 0, "WATCH": 0, "RESERVE": 0}
    assert (
        date.fromisoformat(relatorio["fim"]) - date.fromisoformat(relatorio["inicio"])
    ).days == 29


def test_meta_access_atingida(client, catalogo, prescrever):
    prescrever(catalogo["Amoxicilina"], inicio=3, termino=0)
    prescrever(catalogo["Ceftriaxona"], inicio=0, termino=0, paciente_codigo="PAC-0002")

    relatorio = _indicadores(client, inicio=dia(5), fim=dia(0))

    assert (relatorio["percentual_access"], relatorio["atinge_meta_access"]) == (80.0, True)


def test_periodo_invertido_retorna_422(client):
    resposta = client.get("/relatorios/indicadores", params={"inicio": dia(0), "fim": dia(5)})

    assert resposta.status_code == 422
