"""Regras temporais — US07 e US08 (RN12, RN13, RN14), testadas sem banco de dados."""

from datetime import date

import pytest

from antimicrobiano.config import ParametrosClinicos
from antimicrobiano.enums import Indicacao, Severidade, StatusPrescricao, TipoAlerta
from antimicrobiano.regras import ContextoAvaliacao, MotorDeRegras, criar_motor_padrao
from antimicrobiano.regras.temporais import (
    RegraDuracaoExcedida,
    RegraProfilaxiaProlongada,
    RegraTimeout,
)


def _contexto(dia: int) -> ContextoAvaliacao:
    return ContextoAvaliacao(data_referencia=date(2026, 11, dia))


# --- RN12: time-out de 72 horas -----------------------------------------------------------------


def test_timeout_dispara_com_72_horas_sem_reavaliacao(prescricao):
    alertas = RegraTimeout().avaliar(prescricao(data_inicio=date(2026, 11, 1)), _contexto(4))

    assert len(alertas) == 1
    alerta = alertas[0]
    assert alerta.tipo == TipoAlerta.TIMEOUT_REAVALIACAO
    assert alerta.severidade == Severidade.MEDIA
    assert alerta.evidencias["dias_de_uso"] == 3
    assert "time-out" in alerta.recomendacao


def test_timeout_nao_dispara_antes_de_72_horas(prescricao):
    assert RegraTimeout().avaliar(prescricao(data_inicio=date(2026, 11, 2)), _contexto(4)) == []


def test_timeout_nao_dispara_quando_ha_reavaliacao(prescricao):
    reavaliada = prescricao(data_inicio=date(2026, 11, 1), reavaliacoes=(date(2026, 11, 3),))

    assert RegraTimeout().avaliar(reavaliada, _contexto(4)) == []


def test_reavaliacao_posterior_a_data_de_referencia_nao_conta(prescricao):
    reavaliada_depois = prescricao(data_inicio=date(2026, 11, 1), reavaliacoes=(date(2026, 11, 5),))

    assert len(RegraTimeout().avaliar(reavaliada_depois, _contexto(4))) == 1


# --- RN13: duração excedida ---------------------------------------------------------------------


def test_duracao_excedida_informa_o_dia_de_terapia(prescricao):
    alertas = RegraDuracaoExcedida().avaliar(
        prescricao(data_inicio=date(2026, 11, 1), duracao_prevista_dias=3), _contexto(5)
    )

    assert [a.tipo for a in alertas] == [TipoAlerta.DURACAO_EXCEDIDA]
    assert alertas[0].evidencias == {"dia_de_terapia": 5, "duracao_prevista_dias": 3}


@pytest.mark.parametrize(("duracao", "dia_referencia"), [(7, 5), (5, 5), (3, 3)])
def test_duracao_dentro_do_previsto_nao_gera_alerta(prescricao, duracao, dia_referencia):
    p = prescricao(data_inicio=date(2026, 11, 1), duracao_prevista_dias=duracao)

    assert RegraDuracaoExcedida().avaliar(p, _contexto(dia_referencia)) == []


# --- RN14: profilaxia prolongada ----------------------------------------------------------------


def test_profilaxia_planejada_acima_de_24_horas(prescricao):
    p = prescricao(indicacao=Indicacao.PROFILAXIA, duracao_prevista_dias=3)

    alertas = RegraProfilaxiaProlongada().avaliar(p, _contexto(1))

    assert [a.tipo for a in alertas] == [TipoAlerta.PROFILAXIA_PROLONGADA]
    assert "24 horas" in alertas[0].recomendacao


@pytest.mark.parametrize(
    ("indicacao", "duracao"),
    [(Indicacao.PROFILAXIA, 1), (Indicacao.EMPIRICA, 3), (Indicacao.DIRIGIDA, 14)],
)
def test_profilaxia_de_24_horas_ou_outra_indicacao_nao_gera_alerta(prescricao, indicacao, duracao):
    p = prescricao(indicacao=indicacao, duracao_prevista_dias=duracao)

    assert RegraProfilaxiaProlongada().avaliar(p, _contexto(1)) == []


# --- Motor ---------------------------------------------------------------------------------------


def test_motor_ignora_prescricoes_encerradas(prescricao):
    encerrada = prescricao(
        data_inicio=date(2026, 10, 1), duracao_prevista_dias=3, status=StatusPrescricao.CONCLUIDA
    )

    assert criar_motor_padrao().avaliar([encerrada], _contexto(5)) == []


def test_motor_combina_regras_e_ordena_por_tipo_e_prescricao(prescricao):
    motor = MotorDeRegras([RegraDuracaoExcedida(), RegraTimeout(), RegraProfilaxiaProlongada()])
    primeira = prescricao(data_inicio=date(2026, 11, 1), duracao_prevista_dias=3)
    segunda = prescricao(data_inicio=date(2026, 11, 1), duracao_prevista_dias=10)

    alertas = motor.avaliar([segunda, primeira], _contexto(5))

    assert [(a.tipo, a.prescricao_id) for a in alertas] == [
        (TipoAlerta.TIMEOUT_REAVALIACAO, primeira.id),
        (TipoAlerta.TIMEOUT_REAVALIACAO, segunda.id),
        (TipoAlerta.DURACAO_EXCEDIDA, primeira.id),
    ]


def test_motor_aceita_novas_regras_sem_alterar_as_existentes(prescricao):
    motor = MotorDeRegras([RegraProfilaxiaProlongada()])

    alertas = motor.avaliar([prescricao(duracao_prevista_dias=3)], _contexto(5))

    assert alertas == []
    assert len(motor.regras) == 1


def test_regras_usam_os_parametros_clinicos_do_contexto(prescricao):
    parametros = ParametrosClinicos(timeout_dias=2, limite_profilaxia_dias=2)
    contexto = ContextoAvaliacao(data_referencia=date(2026, 11, 3), parametros=parametros)

    timeout = RegraTimeout().avaliar(prescricao(data_inicio=date(2026, 11, 1)), contexto)
    profilaxia = RegraProfilaxiaProlongada().avaliar(
        prescricao(indicacao=Indicacao.PROFILAXIA, duracao_prevista_dias=2), contexto
    )

    assert timeout[0].evidencias["limite_dias"] == 2
    assert profilaxia == []
