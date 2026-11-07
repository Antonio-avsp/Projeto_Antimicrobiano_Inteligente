"""Carga de dados 100% fictícios para demonstração (HT01, RNF04).

Uso::

    python -m antimicrobiano.seed            # carrega se a base estiver vazia
    python -m antimicrobiano.seed --reset    # recria a base apenas com os dados de demonstração

As datas são relativas ao dia da execução, para que o painel de alertas do dia apresente
um exemplo de cada regra do motor.
"""

from __future__ import annotations

import argparse
import random
from datetime import date, timedelta

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from antimicrobiano.config import Configuracao
from antimicrobiano.database import Base, criar_engine, criar_fabrica_sessoes
from antimicrobiano.enums import (
    CategoriaAware,
    Conduta,
    Indicacao,
    Interpretacao,
    Material,
    StatusCultura,
    StatusPrescricao,
    Via,
)
from antimicrobiano.models import (
    Antimicrobiano,
    Cultura,
    ItemAntibiograma,
    Prescricao,
    Reavaliacao,
)
from antimicrobiano.texto import normalizar

ACCESS, WATCH, RESERVE = CategoriaAware.ACCESS, CategoriaAware.WATCH, CategoriaAware.RESERVE

CATALOGO: list[tuple[str, str, CategoriaAware, bool]] = [
    ("Amoxicilina", "Penicilina", ACCESS, False),
    ("Amoxicilina + clavulanato", "Penicilina com inibidor de betalactamase", ACCESS, False),
    ("Ampicilina", "Penicilina", ACCESS, False),
    ("Oxacilina", "Penicilina resistente à penicilinase", ACCESS, False),
    ("Cefazolina", "Cefalosporina de 1ª geração", ACCESS, False),
    ("Cefalexina", "Cefalosporina de 1ª geração", ACCESS, False),
    ("Gentamicina", "Aminoglicosídeo", ACCESS, False),
    ("Amicacina", "Aminoglicosídeo", ACCESS, False),
    ("Sulfametoxazol + trimetoprima", "Sulfonamida", ACCESS, False),
    ("Nitrofurantoína", "Nitrofurano", ACCESS, False),
    ("Clindamicina", "Lincosamida", ACCESS, False),
    ("Metronidazol", "Nitroimidazol", ACCESS, False),
    ("Ceftriaxona", "Cefalosporina de 3ª geração", WATCH, False),
    ("Cefepima", "Cefalosporina de 4ª geração", WATCH, False),
    ("Ciprofloxacino", "Fluoroquinolona", WATCH, False),
    ("Piperacilina + tazobactam", "Penicilina com inibidor de betalactamase", WATCH, True),
    ("Meropenem", "Carbapenêmico", WATCH, True),
    ("Vancomicina", "Glicopeptídeo", WATCH, True),
    ("Polimixina B", "Polimixina", RESERVE, True),
    ("Linezolida", "Oxazolidinona", RESERVE, True),
    ("Ceftazidima + avibactam", "Cefalosporina com inibidor de betalactamase", RESERVE, True),
]

# Perfis ilustrativos de sensibilidade (probabilidade de "S"), usados apenas para gerar o
# histórico fictício do antibiograma cumulativo.
PERFIS: dict[str, tuple[int, dict[str, float]]] = {
    "Escherichia coli": (
        35,
        {
            "Amoxicilina + clavulanato": 0.70,
            "Nitrofurantoína": 0.95,
            "Gentamicina": 0.90,
            "Amicacina": 0.98,
            "Sulfametoxazol + trimetoprima": 0.60,
            "Ceftriaxona": 0.80,
            "Ciprofloxacino": 0.65,
            "Meropenem": 1.00,
        },
    ),
    "Klebsiella pneumoniae": (
        15,
        {
            "Gentamicina": 0.75,
            "Amicacina": 0.90,
            "Ceftriaxona": 0.55,
            "Cefepima": 0.60,
            "Piperacilina + tazobactam": 0.65,
            "Meropenem": 0.85,
            "Polimixina B": 0.95,
        },
    ),
    "Staphylococcus aureus": (
        12,
        {
            "Oxacilina": 0.60,
            "Clindamicina": 0.75,
            "Sulfametoxazol + trimetoprima": 0.95,
            "Vancomicina": 1.00,
            "Linezolida": 1.00,
        },
    ),
    "Pseudomonas aeruginosa": (
        8,
        {
            "Amicacina": 0.90,
            "Cefepima": 0.75,
            "Ciprofloxacino": 0.70,
            "Piperacilina + tazobactam": 0.75,
            "Meropenem": 0.70,
            "Polimixina B": 0.98,
        },
    ),
}

SETORES = ("UTI Adulto", "Clínica Médica", "Pediatria")


def _catalogo(sessao: Session) -> dict[str, Antimicrobiano]:
    itens = {
        nome: Antimicrobiano(
            nome=nome,
            nome_normalizado=normalizar(nome),
            classe=classe,
            categoria_aware=categoria,
            uso_restrito=restrito,
        )
        for nome, classe, categoria, restrito in CATALOGO
    }
    sessao.add_all(itens.values())
    sessao.flush()
    return itens


def _prescricao(am: Antimicrobiano, **campos) -> Prescricao:
    padrao = {"dose": "1 g", "intervalo_horas": 8, "via": Via.IV, "duracao_prevista_dias": 7}
    return Prescricao(antimicrobiano=am, **(padrao | campos))


def _cultura(
    paciente: str, setor: str, coleta: date, microrganismo: str, antibiograma: dict
) -> Cultura:
    cultura = Cultura(
        paciente_codigo=paciente,
        setor=setor,
        material=Material.SANGUE,
        data_coleta=coleta,
        status=StatusCultura.POSITIVA,
        microrganismo=microrganismo,
        data_resultado=coleta + timedelta(days=2),
    )
    cultura.antibiograma = [
        ItemAntibiograma(antimicrobiano=am, interpretacao=Interpretacao(interp))
        for am, interp in antibiograma.items()
    ]
    return cultura


def _cenarios_do_painel(sessao: Session, am: dict[str, Antimicrobiano], hoje: date) -> None:
    """Pacientes fictícios que geram, no dia da carga, um exemplo de cada tipo de alerta."""
    dias = lambda n: hoje - timedelta(days=n)  # noqa: E731

    # RESTRITO_SEM_JUSTIFICATIVA + SEM_CULTURA
    sessao.add(
        _prescricao(
            am["Meropenem"],
            paciente_codigo="PAC-1001",
            setor="UTI Adulto",
            indicacao=Indicacao.EMPIRICA,
            diagnostico="Sepse de foco abdominal",
            data_inicio=dias(1),
        )
    )
    # RESISTENCIA + TIMEOUT_REAVALIACAO
    sessao.add(
        _prescricao(
            am["Ceftriaxona"],
            paciente_codigo="PAC-1002",
            setor="Clínica Médica",
            indicacao=Indicacao.EMPIRICA,
            diagnostico="Pneumonia comunitária",
            data_inicio=dias(4),
            intervalo_horas=24,
        )
    )
    sessao.add(
        _cultura(
            "PAC-1002",
            "Clínica Médica",
            dias(4),
            "Klebsiella pneumoniae",
            {am["Ceftriaxona"]: "R", am["Meropenem"]: "S", am["Amicacina"]: "S"},
        )
    )
    # DESCALONAMENTO (justificada e reavaliada: sem outros alertas)
    descalonavel = _prescricao(
        am["Piperacilina + tazobactam"],
        paciente_codigo="PAC-1003",
        setor="UTI Adulto",
        indicacao=Indicacao.DIRIGIDA,
        diagnostico="Infecção do trato urinário complicada",
        data_inicio=dias(3),
        justificativa="Sepse urinária em paciente com uso prévio de antimicrobianos",
        dose="4,5 g",
        intervalo_horas=6,
    )
    descalonavel.reavaliacoes.append(
        Reavaliacao(data_reavaliacao=dias(1), conduta=Conduta.MANTER, observacao="Aguardar TSA")
    )
    sessao.add(descalonavel)
    sessao.add(
        _cultura(
            "PAC-1003",
            "UTI Adulto",
            dias(3),
            "Escherichia coli",
            {
                am["Piperacilina + tazobactam"]: "S",
                am["Gentamicina"]: "S",
                am["Amoxicilina + clavulanato"]: "S",
                am["Ciprofloxacino"]: "R",
            },
        )
    )
    # PROFILAXIA_PROLONGADA
    sessao.add(
        _prescricao(
            am["Cefazolina"],
            paciente_codigo="PAC-1004",
            setor="Centro Cirúrgico",
            indicacao=Indicacao.PROFILAXIA,
            diagnostico="Profilaxia em artroplastia de quadril",
            data_inicio=hoje,
            duracao_prevista_dias=3,
            dose="2 g",
        )
    )
    # DURACAO_EXCEDIDA (reavaliada no time-out)
    prolongada = _prescricao(
        am["Amoxicilina"],
        paciente_codigo="PAC-1005",
        setor="Clínica Médica",
        indicacao=Indicacao.DIRIGIDA,
        diagnostico="Otite média aguda",
        data_inicio=dias(9),
        via=Via.VO,
        dose="500 mg",
    )
    prolongada.reavaliacoes.append(Reavaliacao(data_reavaliacao=dias(6), conduta=Conduta.MANTER))
    sessao.add(prolongada)
    # DUPLICIDADE_TERAPEUTICA: transição IV → VO sem suspender a cefalosporina IV
    for nome, via, dose in (("Cefazolina", Via.IV, "1 g"), ("Cefalexina", Via.VO, "500 mg")):
        sessao.add(
            _prescricao(
                am[nome],
                paciente_codigo="PAC-1009",
                setor="Clínica Médica",
                indicacao=Indicacao.DIRIGIDA,
                diagnostico="Celulite em membro inferior",
                data_inicio=dias(1),
                via=via,
                dose=dose,
                intervalo_horas=6,
            )
        )
    # Sem alertas: ACCESS empírico recente e uma prescrição já concluída
    sessao.add(
        _prescricao(
            am["Ampicilina"],
            paciente_codigo="PAC-1006",
            setor="Pediatria",
            indicacao=Indicacao.EMPIRICA,
            diagnostico="Pneumonia comunitária",
            data_inicio=hoje,
            dose="50 mg/kg",
            intervalo_horas=6,
        )
    )
    sessao.add(
        _prescricao(
            am["Ciprofloxacino"],
            paciente_codigo="PAC-1007",
            setor="Clínica Médica",
            indicacao=Indicacao.DIRIGIDA,
            diagnostico="Pielonefrite",
            data_inicio=dias(9),
            via=Via.VO,
            dose="500 mg",
            intervalo_horas=12,
            status=StatusPrescricao.CONCLUIDA,
            data_fim=dias(2),
            motivo_encerramento="Curso completo",
        )
    )
    # Cultura ainda pendente
    sessao.add(
        Cultura(
            paciente_codigo="PAC-1008",
            setor="UTI Adulto",
            material=Material.URINA,
            data_coleta=hoje,
        )
    )


def _historico_microbiologico(sessao: Session, am: dict[str, Antimicrobiano], hoje: date) -> None:
    """Culturas fictícias dos últimos seis meses para o antibiograma cumulativo."""
    sorteio = random.Random(42)
    paciente = 2000
    for microrganismo, (quantidade, perfil) in PERFIS.items():
        for _ in range(quantidade):
            paciente += 1
            antibiograma = {}
            for nome, prob_sensivel in perfil.items():
                if sorteio.random() < prob_sensivel:
                    antibiograma[am[nome]] = "S"
                else:
                    antibiograma[am[nome]] = "I" if sorteio.random() < 0.2 else "R"
            sessao.add(
                _cultura(
                    f"PAC-{paciente}",
                    sorteio.choice(SETORES),
                    hoje - timedelta(days=sorteio.randint(10, 180)),
                    microrganismo,
                    antibiograma,
                )
            )


def carregar(sessao: Session, hoje: date | None = None) -> dict[str, int]:
    """Insere o catálogo, os cenários do painel e o histórico microbiológico."""
    hoje = hoje or date.today()
    antimicrobianos = _catalogo(sessao)
    _cenarios_do_painel(sessao, antimicrobianos, hoje)
    _historico_microbiologico(sessao, antimicrobianos, hoje)
    sessao.commit()
    return {
        "antimicrobianos": sessao.scalar(select(func.count(Antimicrobiano.id))),
        "prescricoes": sessao.scalar(select(func.count(Prescricao.id))),
        "culturas": sessao.scalar(select(func.count(Cultura.id))),
    }


def _preparar_banco(engine: Engine, reset: bool) -> None:
    if reset:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada do comando ``python -m antimicrobiano.seed``."""
    parser = argparse.ArgumentParser(description="Carrega dados fictícios de demonstração.")
    parser.add_argument(
        "--reset", action="store_true", help="apaga a base e recria apenas os dados de demonstração"
    )
    argumentos = parser.parse_args(argv)

    config = Configuracao.do_ambiente()
    engine = criar_engine(config.database_url)
    try:
        _preparar_banco(engine, argumentos.reset)
        with criar_fabrica_sessoes(engine)() as sessao:
            if sessao.scalar(select(func.count(Antimicrobiano.id))):
                print(
                    "A base já possui dados; nada foi alterado. "
                    "Use --reset para recriá-la com os dados de demonstração."
                )
                return 0
            totais = carregar(sessao)
    finally:
        engine.dispose()
    print(
        f"Carga concluída em {config.database_url}: {totais['antimicrobianos']} antimicrobianos, "
        f"{totais['prescricoes']} prescrições e {totais['culturas']} culturas (dados fictícios)."
    )
    print("Inicie a API com 'uvicorn antimicrobiano.main:app' e consulte GET /alertas.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
