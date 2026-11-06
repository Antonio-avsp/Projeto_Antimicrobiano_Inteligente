"""Fábricas de objetos de domínio em memória para testar as regras isoladamente (RNF08)."""

from datetime import date
from itertools import count

import pytest

from antimicrobiano.enums import CategoriaAware, Conduta, Indicacao, StatusPrescricao, Via
from antimicrobiano.models import Antimicrobiano, Prescricao, Reavaliacao

_ids = count(1)


def fabricar_antimicrobiano(
    nome: str = "Ceftriaxona",
    categoria_aware: CategoriaAware = CategoriaAware.WATCH,
    uso_restrito: bool = False,
    ativo: bool = True,
    classe: str = "Cefalosporina de 3ª geração",
) -> Antimicrobiano:
    return Antimicrobiano(
        id=next(_ids),
        nome=nome,
        classe=classe,
        categoria_aware=categoria_aware,
        uso_restrito=uso_restrito,
        ativo=ativo,
    )


def fabricar_prescricao(
    antimicrobiano: Antimicrobiano | None = None,
    data_inicio: date = date(2026, 11, 1),
    duracao_prevista_dias: int = 7,
    indicacao: Indicacao = Indicacao.EMPIRICA,
    paciente_codigo: str = "PAC-0001",
    justificativa: str | None = None,
    status: StatusPrescricao = StatusPrescricao.ATIVA,
    reavaliacoes: tuple[date, ...] = (),
) -> Prescricao:
    prescricao = Prescricao(
        id=next(_ids),
        paciente_codigo=paciente_codigo,
        setor="UTI Adulto",
        antimicrobiano=antimicrobiano or fabricar_antimicrobiano(),
        dose="1 g",
        intervalo_horas=24,
        via=Via.IV,
        indicacao=indicacao,
        diagnostico="Pneumonia associada à ventilação",
        data_inicio=data_inicio,
        duracao_prevista_dias=duracao_prevista_dias,
        justificativa=justificativa,
        status=status,
    )
    for data in reavaliacoes:
        prescricao.reavaliacoes.append(Reavaliacao(data_reavaliacao=data, conduta=Conduta.MANTER))
    return prescricao


@pytest.fixture
def prescricao():
    return fabricar_prescricao
