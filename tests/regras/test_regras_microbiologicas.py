"""Resistência e descalonamento — US10 e US11 (RN17, RN18, RN20), sem banco de dados."""

from datetime import date

import pytest

from antimicrobiano.enums import CategoriaAware, Severidade, TipoAlerta
from antimicrobiano.regras import ContextoAvaliacao
from antimicrobiano.regras.microbiologicas import RegraDescalonamento, RegraResistencia
from tests.regras.fabricas import fabricar_antimicrobiano, fabricar_cultura

REFERENCIA = date(2026, 11, 5)
ACCESS, WATCH, RESERVE = CategoriaAware.ACCESS, CategoriaAware.WATCH, CategoriaAware.RESERVE


@pytest.fixture
def catalogo():
    return {
        "ceftriaxona": fabricar_antimicrobiano("Ceftriaxona", WATCH),
        "meropenem": fabricar_antimicrobiano("Meropenem", WATCH, uso_restrito=True),
        "gentamicina": fabricar_antimicrobiano("Gentamicina", ACCESS),
        "amicacina": fabricar_antimicrobiano("Amicacina", ACCESS),
        "amoxicilina": fabricar_antimicrobiano("Amoxicilina", ACCESS),
        "polimixina": fabricar_antimicrobiano("Polimixina B", RESERVE),
        "cefalotina": fabricar_antimicrobiano("Cefalotina", ACCESS, ativo=False),
    }


def _contexto(*culturas) -> ContextoAvaliacao:
    por_paciente: dict[str, list] = {}
    for cultura in culturas:
        por_paciente.setdefault(cultura.paciente_codigo, []).append(cultura)
    return ContextoAvaliacao(data_referencia=REFERENCIA, culturas_por_paciente=por_paciente)


# --- RN17: resistência ------------------------------------------------------------------------


def test_microrganismo_resistente_gera_alerta_com_alternativas(prescricao, catalogo):
    p = prescricao(catalogo["ceftriaxona"])
    cultura = fabricar_cultura(
        microrganismo="Klebsiella pneumoniae",
        antibiograma={catalogo["ceftriaxona"]: "R", catalogo["meropenem"]: "S"},
    )

    alertas = RegraResistencia().avaliar(p, _contexto(cultura))

    assert [(a.tipo, a.severidade) for a in alertas] == [(TipoAlerta.RESISTENCIA, Severidade.ALTA)]
    assert "Klebsiella pneumoniae" in alertas[0].mensagem
    assert "Meropenem (WATCH)" in alertas[0].recomendacao
    assert alertas[0].evidencias["alternativas"] == ["Meropenem"]
    assert alertas[0].evidencias["culturas"][0]["cultura_id"] == cultura.id


def test_cultura_fora_da_janela_de_relevancia_nao_gera_alerta(prescricao, catalogo):
    p = prescricao(catalogo["ceftriaxona"], data_inicio=date(2026, 11, 1))
    antiga = fabricar_cultura(
        data_coleta=date(2026, 10, 2),
        microrganismo="Klebsiella pneumoniae",
        antibiograma={catalogo["ceftriaxona"]: "R"},
    )

    assert RegraResistencia().avaliar(p, _contexto(antiga)) == []


def test_alternativas_ativas_ordenadas_por_categoria_aware(prescricao, catalogo):
    p = prescricao(catalogo["ceftriaxona"])
    cultura = fabricar_cultura(
        microrganismo="Escherichia coli",
        antibiograma={
            catalogo["ceftriaxona"]: "R",
            catalogo["polimixina"]: "S",
            catalogo["meropenem"]: "S",
            catalogo["gentamicina"]: "S",
            catalogo["cefalotina"]: "S",  # inativo: não pode ser sugerido
        },
    )

    alerta = RegraResistencia().avaliar(p, _contexto(cultura))[0]

    assert alerta.evidencias["alternativas"] == ["Gentamicina", "Meropenem", "Polimixina B"]


def test_sem_alternativa_comum_orienta_discussao_com_infectologista(prescricao, catalogo):
    p = prescricao(catalogo["ceftriaxona"])
    primeira = fabricar_cultura(
        microrganismo="Escherichia coli",
        antibiograma={catalogo["ceftriaxona"]: "R", catalogo["gentamicina"]: "S"},
    )
    segunda = fabricar_cultura(
        microrganismo="Pseudomonas aeruginosa",
        antibiograma={catalogo["ceftriaxona"]: "R", catalogo["gentamicina"]: "R"},
    )

    alerta = RegraResistencia().avaliar(p, _contexto(primeira, segunda))[0]

    assert alerta.evidencias["alternativas"] == []
    assert "infectologista" in alerta.recomendacao


@pytest.mark.parametrize("interpretacao", ["S", "I"])
def test_sensivel_ou_sensivel_aumentando_exposicao_nao_e_resistencia(
    prescricao, catalogo, interpretacao
):
    p = prescricao(catalogo["ceftriaxona"])
    cultura = fabricar_cultura(
        microrganismo="Escherichia coli", antibiograma={catalogo["ceftriaxona"]: interpretacao}
    )

    assert RegraResistencia().avaliar(p, _contexto(cultura)) == []


def test_cultura_pendente_nao_e_considerada(prescricao, catalogo):
    p = prescricao(catalogo["ceftriaxona"])

    assert RegraResistencia().avaliar(p, _contexto(fabricar_cultura())) == []


# --- RN18: descalonamento ---------------------------------------------------------------------


def test_oportunidade_de_descalonamento(prescricao, catalogo):
    p = prescricao(catalogo["meropenem"], paciente_codigo="PAC-0002")
    cultura = fabricar_cultura(
        paciente_codigo="PAC-0002",
        microrganismo="Escherichia coli",
        antibiograma={catalogo["meropenem"]: "S", catalogo["gentamicina"]: "S"},
    )

    alertas = RegraDescalonamento().avaliar(p, _contexto(cultura))

    assert [(a.tipo, a.severidade) for a in alertas] == [
        (TipoAlerta.DESCALONAMENTO, Severidade.BAIXA)
    ]
    assert alertas[0].evidencias["opcoes"] == [{"nome": "Gentamicina", "categoria_aware": "ACCESS"}]
    assert "Gentamicina (ACCESS)" in alertas[0].recomendacao


def test_prescricao_access_nao_tem_descalonamento(prescricao, catalogo):
    p = prescricao(catalogo["amoxicilina"])
    cultura = fabricar_cultura(
        microrganismo="Escherichia coli", antibiograma={catalogo["gentamicina"]: "S"}
    )

    assert RegraDescalonamento().avaliar(p, _contexto(cultura)) == []


def test_opcao_precisa_ser_sensivel_em_todas_as_culturas(prescricao, catalogo):
    p = prescricao(catalogo["meropenem"])
    primeira = fabricar_cultura(
        microrganismo="Escherichia coli",
        antibiograma={catalogo["gentamicina"]: "S", catalogo["amicacina"]: "S"},
    )
    segunda = fabricar_cultura(
        microrganismo="Klebsiella pneumoniae",
        antibiograma={catalogo["gentamicina"]: "R", catalogo["amicacina"]: "S"},
    )

    alerta = RegraDescalonamento().avaliar(p, _contexto(primeira, segunda))[0]

    assert [opcao["nome"] for opcao in alerta.evidencias["opcoes"]] == ["Amicacina"]


def test_reserve_pode_descalonar_para_watch(prescricao, catalogo):
    p = prescricao(catalogo["polimixina"])
    cultura = fabricar_cultura(
        microrganismo="Klebsiella pneumoniae", antibiograma={catalogo["meropenem"]: "S"}
    )

    alerta = RegraDescalonamento().avaliar(p, _contexto(cultura))[0]

    assert alerta.evidencias["opcoes"] == [{"nome": "Meropenem", "categoria_aware": "WATCH"}]


def test_resistencia_ao_prescrito_nao_e_tratada_como_descalonamento(prescricao, catalogo):
    p = prescricao(catalogo["meropenem"])
    cultura = fabricar_cultura(
        microrganismo="Klebsiella pneumoniae",
        antibiograma={catalogo["meropenem"]: "R", catalogo["gentamicina"]: "S"},
    )

    assert RegraDescalonamento().avaliar(p, _contexto(cultura)) == []


def test_sem_opcao_de_categoria_inferior_nao_gera_alerta(prescricao, catalogo):
    p = prescricao(catalogo["meropenem"])
    cultura = fabricar_cultura(
        microrganismo="Escherichia coli",
        antibiograma={catalogo["meropenem"]: "S", catalogo["ceftriaxona"]: "S"},
    )

    assert RegraDescalonamento().avaliar(p, _contexto(cultura)) == []
