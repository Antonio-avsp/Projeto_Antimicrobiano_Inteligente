"""Regras de política — US09 e US12 (RN15, RN16), testadas sem banco de dados."""

from datetime import date

import pytest

from antimicrobiano.enums import CategoriaAware, Indicacao, Severidade, TipoAlerta
from antimicrobiano.regras import ContextoAvaliacao
from antimicrobiano.regras.politicas import RegraRestritoSemJustificativa, RegraSemCultura
from tests.regras.fabricas import fabricar_antimicrobiano, fabricar_cultura

REFERENCIA = date(2026, 11, 5)


def _contexto(*culturas) -> ContextoAvaliacao:
    por_paciente: dict[str, list] = {}
    for cultura in culturas:
        por_paciente.setdefault(cultura.paciente_codigo, []).append(cultura)
    return ContextoAvaliacao(data_referencia=REFERENCIA, culturas_por_paciente=por_paciente)


# --- RN15: uso restrito sem justificativa ---------------------------------------------------


def test_restrito_sem_justificativa_gera_alerta_de_severidade_alta(prescricao):
    meropenem = fabricar_antimicrobiano(nome="Meropenem", uso_restrito=True)

    alertas = RegraRestritoSemJustificativa().avaliar(prescricao(meropenem), _contexto())

    assert [(a.tipo, a.severidade) for a in alertas] == [
        (TipoAlerta.RESTRITO_SEM_JUSTIFICATIVA, Severidade.ALTA)
    ]
    assert "justificativa" in alertas[0].recomendacao


def test_restrito_com_justificativa_nao_gera_alerta(prescricao):
    meropenem = fabricar_antimicrobiano(nome="Meropenem", uso_restrito=True)
    justificada = prescricao(meropenem, justificativa="Choque séptico com suspeita de ESBL")

    assert RegraRestritoSemJustificativa().avaliar(justificada, _contexto()) == []


def test_antimicrobiano_nao_restrito_dispensa_justificativa(prescricao):
    assert RegraRestritoSemJustificativa().avaliar(prescricao(), _contexto()) == []


# --- RN16: amplo espectro empírico sem cultura -----------------------------------------------


@pytest.mark.parametrize("categoria", [CategoriaAware.WATCH, CategoriaAware.RESERVE])
def test_empirico_de_amplo_espectro_sem_cultura(prescricao, categoria):
    antimicrobiano = fabricar_antimicrobiano(
        nome="Piperacilina + tazobactam", categoria_aware=categoria
    )

    alertas = RegraSemCultura().avaliar(prescricao(antimicrobiano), _contexto())

    assert [(a.tipo, a.severidade) for a in alertas] == [(TipoAlerta.SEM_CULTURA, Severidade.MEDIA)]
    assert alertas[0].evidencias["categoria_aware"] == categoria.value


def test_cultura_coletada_no_inicio_da_terapia_evita_o_alerta(prescricao):
    p = prescricao(data_inicio=date(2026, 11, 1), paciente_codigo="PAC-0003")
    cultura = fabricar_cultura(paciente_codigo="PAC-0003", data_coleta=date(2026, 11, 1))

    assert RegraSemCultura().avaliar(p, _contexto(cultura)) == []


@pytest.mark.parametrize(
    ("paciente", "coleta"),
    [
        ("PAC-0003", date(2026, 10, 20)),  # antes da janela de 7 dias
        ("PAC-0003", date(2026, 11, 6)),  # depois da data de referência
        ("PAC-0009", date(2026, 11, 1)),  # outro paciente
    ],
)
def test_cultura_fora_da_janela_ou_de_outro_paciente_nao_conta(prescricao, paciente, coleta):
    p = prescricao(data_inicio=date(2026, 11, 1), paciente_codigo="PAC-0003")
    cultura = fabricar_cultura(paciente_codigo=paciente, data_coleta=coleta)

    assert len(RegraSemCultura().avaliar(p, _contexto(cultura))) == 1


def test_access_ou_indicacao_nao_empirica_nao_exige_cultura(prescricao):
    amoxicilina = fabricar_antimicrobiano(nome="Amoxicilina", categoria_aware=CategoriaAware.ACCESS)
    profilaxia = prescricao(indicacao=Indicacao.PROFILAXIA)
    dirigida = prescricao(indicacao=Indicacao.DIRIGIDA)

    for p in (prescricao(amoxicilina), profilaxia, dirigida):
        assert RegraSemCultura().avaliar(p, _contexto()) == []
