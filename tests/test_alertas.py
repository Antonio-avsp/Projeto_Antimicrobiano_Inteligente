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


# --- US09 e US12: políticas de uso ----------------------------------------------------------


def test_justificativa_registrada_resolve_o_alerta_de_uso_restrito(
    client, novo_antimicrobiano, nova_prescricao, alertas
):
    meropenem = novo_antimicrobiano(nome="Meropenem", classe="Carbapenêmico", uso_restrito=True)
    prescricao = nova_prescricao(antimicrobiano_id=meropenem["id"])

    antes = alertas()
    client.patch(
        f"/prescricoes/{prescricao['id']}",
        json={"justificativa": "Choque séptico com suspeita de ESBL"},
    )
    depois = alertas()

    assert "RESTRITO_SEM_JUSTIFICATIVA" in _tipos(antes, prescricao["id"])
    assert antes["alertas"][0]["severidade"] == "ALTA"
    assert "RESTRITO_SEM_JUSTIFICATIVA" not in _tipos(depois, prescricao["id"])


def test_cultura_coletada_resolve_o_alerta_de_amplo_espectro_sem_cultura(
    client, novo_antimicrobiano, nova_prescricao, nova_cultura, alertas
):
    piperacilina = novo_antimicrobiano(nome="Piperacilina + tazobactam", classe="Penicilina")
    prescricao = nova_prescricao(
        antimicrobiano_id=piperacilina["id"], paciente_codigo="PAC-0003", data_inicio="2026-11-01"
    )

    antes = alertas(data_referencia="2026-11-02")
    nova_cultura(paciente_codigo="PAC-0003", data_coleta="2026-11-01")
    depois = alertas(data_referencia="2026-11-02")

    assert "SEM_CULTURA" in _tipos(antes, prescricao["id"])
    assert "SEM_CULTURA" not in _tipos(depois, prescricao["id"])


def test_access_empirico_nao_exige_cultura(novo_antimicrobiano, nova_prescricao, alertas):
    amoxicilina = novo_antimicrobiano(
        nome="Amoxicilina", classe="Penicilina", categoria_aware="ACCESS"
    )
    prescricao = nova_prescricao(antimicrobiano_id=amoxicilina["id"])

    assert "SEM_CULTURA" not in _tipos(alertas(), prescricao["id"])


# --- US10 e US11: microbiologia ----------------------------------------------------------------


def _resultado(microrganismo: str, antibiograma: dict[int, str]) -> dict:
    return {
        "resultado": "POSITIVA",
        "microrganismo": microrganismo,
        "antibiograma": [
            {"antimicrobiano_id": am_id, "interpretacao": interp}
            for am_id, interp in antibiograma.items()
        ],
    }


def test_resistencia_no_painel_lista_alternativa_sensivel(
    novo_antimicrobiano, nova_prescricao, nova_cultura, alertas
):
    ceftriaxona = novo_antimicrobiano(nome="Ceftriaxona")
    meropenem = novo_antimicrobiano(nome="Meropenem", classe="Carbapenêmico", uso_restrito=True)
    prescricao = nova_prescricao(antimicrobiano_id=ceftriaxona["id"], data_inicio="2026-11-01")
    nova_cultura(
        data_coleta="2026-11-01",
        resultado=_resultado(
            "Klebsiella pneumoniae", {ceftriaxona["id"]: "R", meropenem["id"]: "S"}
        ),
    )

    painel = alertas(data_referencia="2026-11-04")

    resistencia = next(a for a in painel["alertas"] if a["tipo"] == "RESISTENCIA")
    assert resistencia["prescricao_id"] == prescricao["id"]
    assert resistencia["severidade"] == "ALTA"
    assert "Meropenem" in resistencia["recomendacao"]


def test_descalonamento_no_painel_sugere_opcao_access(
    novo_antimicrobiano, nova_prescricao, nova_cultura, alertas
):
    meropenem = novo_antimicrobiano(nome="Meropenem", classe="Carbapenêmico")
    gentamicina = novo_antimicrobiano(
        nome="Gentamicina", classe="Aminoglicosídeo", categoria_aware="ACCESS"
    )
    prescricao = nova_prescricao(
        antimicrobiano_id=meropenem["id"], paciente_codigo="PAC-0002", data_inicio="2026-11-01"
    )
    nova_cultura(
        paciente_codigo="PAC-0002",
        data_coleta="2026-11-01",
        resultado=_resultado("Escherichia coli", {meropenem["id"]: "S", gentamicina["id"]: "S"}),
    )

    painel = alertas(data_referencia="2026-11-04")

    descalonamento = next(a for a in painel["alertas"] if a["tipo"] == "DESCALONAMENTO")
    assert descalonamento["prescricao_id"] == prescricao["id"]
    assert descalonamento["evidencias"]["opcoes"] == [
        {"nome": "Gentamicina", "categoria_aware": "ACCESS"}
    ]
    assert painel["alertas"][-1]["severidade"] == "BAIXA"


# --- US13: painel filtrável com resumo -------------------------------------------------------


@pytest.fixture
def cenario_painel(novo_antimicrobiano, nova_prescricao):
    """Três prescrições que geram alertas ALTA, MEDIA e BAIXA em setores diferentes."""
    meropenem = novo_antimicrobiano(nome="Meropenem", classe="Carbapenêmico", uso_restrito=True)
    amoxicilina = novo_antimicrobiano(
        nome="Amoxicilina", classe="Penicilina", categoria_aware="ACCESS"
    )
    return {
        "uti": nova_prescricao(
            antimicrobiano_id=meropenem["id"], setor="UTI Adulto", paciente_codigo="PAC-0001"
        ),
        "clinica": nova_prescricao(
            antimicrobiano_id=amoxicilina["id"],
            setor="Clínica Médica",
            paciente_codigo="PAC-0002",
            data_inicio="2026-11-01",
        ),
    }


def test_ordenacao_por_severidade_e_resumo(cenario_painel, alertas):
    painel = alertas(data_referencia="2026-11-05")

    ordens = {"ALTA": 0, "MEDIA": 1, "BAIXA": 2}
    severidades = [alerta["severidade"] for alerta in painel["alertas"]]
    assert severidades == sorted(severidades, key=ordens.get)
    assert painel["total"] == len(painel["alertas"])
    assert sum(painel["resumo"]["por_severidade"].values()) == painel["total"]
    assert painel["resumo"]["por_severidade"]["ALTA"] == 1
    assert painel["resumo"]["por_tipo"]["RESTRITO_SEM_JUSTIFICATIVA"] == 1
    assert painel["resumo"]["por_tipo"]["DESCALONAMENTO"] == 0


def test_filtros_combinados_de_severidade_e_setor(cenario_painel, alertas):
    painel = alertas(data_referencia="2026-11-05", severidade="ALTA", setor="UTI Adulto")

    assert painel["total"] == 1
    assert {(a["severidade"], a["setor"]) for a in painel["alertas"]} == {("ALTA", "UTI Adulto")}
    assert painel["resumo"]["por_severidade"] == {"ALTA": 1, "MEDIA": 0, "BAIXA": 0}


def test_filtro_por_tipo_e_paciente(cenario_painel, alertas):
    painel = alertas(
        data_referencia="2026-11-05", tipo="TIMEOUT_REAVALIACAO", paciente_codigo="PAC-0002"
    )

    assert [(a["tipo"], a["paciente_codigo"]) for a in painel["alertas"]] == [
        ("TIMEOUT_REAVALIACAO", "PAC-0002")
    ]


@pytest.mark.parametrize(
    "params",
    [{"tipo": "INEXISTENTE"}, {"severidade": "CRITICA"}, {"paciente_codigo": "Maria"}],
)
def test_filtros_invalidos_retornam_422(client, params):
    assert client.get("/alertas", params=params).status_code == 422


def test_duplicidade_terapeutica_considera_prescricoes_de_outro_setor(
    client, novo_antimicrobiano, nova_prescricao
):
    """RN22: o filtro de setor não esconde a outra prescrição da mesma classe."""
    cefazolina = novo_antimicrobiano(
        nome="Cefazolina", classe="Cefalosporina de 1ª geração", categoria_aware="ACCESS"
    )
    cefalexina = novo_antimicrobiano(
        nome="Cefalexina", classe="Cefalosporina de 1ª geração", categoria_aware="ACCESS"
    )
    iv = nova_prescricao(cefazolina["id"], setor="UTI Adulto", indicacao="DIRIGIDA")
    vo = nova_prescricao(cefalexina["id"], setor="Clínica Médica", indicacao="DIRIGIDA", via="VO")

    painel = client.get(
        "/alertas", params={"tipo": "DUPLICIDADE_TERAPEUTICA", "setor": "UTI Adulto"}
    ).json()

    assert [a["prescricao_id"] for a in painel["alertas"]] == [iv["id"]]
    assert painel["alertas"][0]["evidencias"]["prescricoes_da_mesma_classe"] == [vo["id"]]
    assert painel["resumo"]["por_tipo"]["DUPLICIDADE_TERAPEUTICA"] == 1


def test_encerrar_uma_das_prescricoes_resolve_a_duplicidade(
    client, novo_antimicrobiano, nova_prescricao
):
    classe = "Cefalosporina de 1ª geração"
    iv = nova_prescricao(novo_antimicrobiano(nome="Cefazolina", classe=classe)["id"])
    nova_prescricao(novo_antimicrobiano(nome="Cefalexina", classe=classe)["id"], via="VO")
    client.post(f"/prescricoes/{iv['id']}/encerramento", json={"status_final": "SUSPENSA"})

    painel = client.get("/alertas", params={"tipo": "DUPLICIDADE_TERAPEUTICA"}).json()

    assert painel["total"] == 0
