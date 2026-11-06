"""RNF01 / OBJ-03: painel de alertas com 1.000 prescrições ativas em até 2 segundos."""

import time
from datetime import date, timedelta

from antimicrobiano.enums import (
    CategoriaAware,
    Indicacao,
    Interpretacao,
    Material,
    StatusCultura,
    Via,
)
from antimicrobiano.models import Antimicrobiano, Cultura, ItemAntibiograma, Prescricao

LIMITE_SEGUNDOS = 2.0
QUANTIDADE = 1_000


def _popular(sessao) -> None:
    catalogo = [
        Antimicrobiano(
            nome=nome,
            nome_normalizado=nome.lower(),
            classe="Classe",
            categoria_aware=categoria,
            uso_restrito=restrito,
        )
        for nome, categoria, restrito in [
            ("Amoxicilina", CategoriaAware.ACCESS, False),
            ("Gentamicina", CategoriaAware.ACCESS, False),
            ("Ceftriaxona", CategoriaAware.WATCH, False),
            ("Meropenem", CategoriaAware.WATCH, True),
            ("Polimixina B", CategoriaAware.RESERVE, True),
        ]
    ]
    sessao.add_all(catalogo)
    sessao.flush()
    hoje = date.today()
    indicacoes = list(Indicacao)
    for i in range(QUANTIDADE):
        paciente = f"PAC-{i:05d}"
        prescrito = catalogo[i % len(catalogo)]
        sessao.add(
            Prescricao(
                paciente_codigo=paciente,
                setor=f"Setor {i % 8}",
                antimicrobiano_id=prescrito.id,
                dose="1 g",
                intervalo_horas=8,
                via=Via.IV,
                indicacao=indicacoes[i % len(indicacoes)],
                diagnostico="Infecção de teste",
                data_inicio=hoje - timedelta(days=i % 10),
                duracao_prevista_dias=1 + i % 7,
            )
        )
        if i % 2 == 0:
            cultura = Cultura(
                paciente_codigo=paciente,
                setor="UTI Adulto",
                material=Material.SANGUE,
                data_coleta=hoje - timedelta(days=i % 5),
                status=StatusCultura.POSITIVA,
                microrganismo="Escherichia coli",
            )
            cultura.antibiograma = (
                [
                    ItemAntibiograma(antimicrobiano_id=prescrito.id, interpretacao=Interpretacao.R),
                    ItemAntibiograma(
                        antimicrobiano_id=catalogo[1].id, interpretacao=Interpretacao.S
                    ),
                ]
                if prescrito.id != catalogo[1].id
                else []
            )
            sessao.add(cultura)
    sessao.commit()


def test_painel_com_mil_prescricoes_ativas_responde_em_ate_dois_segundos(app, client):
    with app.state.fabrica_sessoes() as sessao:
        _popular(sessao)

    inicio = time.perf_counter()
    resposta = client.get("/alertas")
    duracao = time.perf_counter() - inicio

    assert resposta.status_code == 200
    assert resposta.json()["total"] >= QUANTIDADE
    assert duracao <= LIMITE_SEGUNDOS, f"Painel levou {duracao:.2f} s"
