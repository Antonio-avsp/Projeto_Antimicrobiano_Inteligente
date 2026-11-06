"""Relatórios gerenciais (UC06 — RF14, RN19)."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from antimicrobiano.enums import Interpretacao, StatusCultura
from antimicrobiano.erros import RegraDeNegocioViolada
from antimicrobiano.models import Cultura
from antimicrobiano.texto import normalizar

METODOLOGIA = (
    "Culturas positivas do período; somente o primeiro isolado por paciente e microrganismo "
    "(CLSI M39). Percentual de sensibilidade = S ÷ testados × 100. Combinações com menos isolados "
    "testados que o mínimo configurado são sinalizadas como amostra insuficiente."
)


def _primeiros_isolados(culturas: list[Cultura]) -> list[Cultura]:
    """Mantém a coleta mais antiga de cada par paciente × microrganismo (RN19)."""
    primeiros: dict[tuple[str, str], Cultura] = {}
    for cultura in sorted(culturas, key=lambda c: (c.data_coleta, c.id)):
        chave = (cultura.paciente_codigo, normalizar(cultura.microrganismo or ""))
        primeiros.setdefault(chave, cultura)
    return list(primeiros.values())


def antibiograma_cumulativo(
    sessao: Session,
    inicio: date,
    fim: date,
    minimo_isolados: int,
    setor: str | None = None,
) -> dict:
    """Consolida os antibiogramas do período por microrganismo e antimicrobiano (RF14)."""
    if inicio > fim:
        raise RegraDeNegocioViolada("A data inicial do período não pode ser posterior à final.")
    consulta = select(Cultura).where(
        Cultura.status == StatusCultura.POSITIVA, Cultura.data_coleta.between(inicio, fim)
    )
    if setor:
        consulta = consulta.where(Cultura.setor == setor)
    isolados = _primeiros_isolados(list(sessao.scalars(consulta)))

    perfis: dict[str, dict] = {}
    for cultura in isolados:
        perfil = perfis.setdefault(
            normalizar(cultura.microrganismo or ""),
            {"microrganismo": cultura.microrganismo, "isolados": 0, "contagens": {}},
        )
        perfil["isolados"] += 1
        for item in cultura.antibiograma:
            contagem = perfil["contagens"].setdefault(
                item.antimicrobiano_id,
                {"antimicrobiano": item.antimicrobiano, **dict.fromkeys(Interpretacao, 0)},
            )
            contagem[item.interpretacao] += 1

    microrganismos = []
    for perfil in sorted(
        perfis.values(), key=lambda p: (-p["isolados"], normalizar(p["microrganismo"]))
    ):
        linhas = []
        for contagem in sorted(
            perfil["contagens"].values(),
            key=lambda c: (
                c["antimicrobiano"].categoria_aware.nivel,
                normalizar(c["antimicrobiano"].nome),
            ),
        ):
            sensiveis = contagem[Interpretacao.S]
            testados = sensiveis + contagem[Interpretacao.I] + contagem[Interpretacao.R]
            linhas.append(
                {
                    "antimicrobiano": contagem["antimicrobiano"].nome,
                    "categoria_aware": contagem["antimicrobiano"].categoria_aware,
                    "testados": testados,
                    "sensiveis": sensiveis,
                    "sensiveis_aumentando_exposicao": contagem[Interpretacao.I],
                    "resistentes": contagem[Interpretacao.R],
                    "percentual_sensivel": round(100 * sensiveis / testados, 1),
                    "amostra_suficiente": testados >= minimo_isolados,
                }
            )
        microrganismos.append(
            {
                "microrganismo": perfil["microrganismo"],
                "isolados": perfil["isolados"],
                "antimicrobianos": linhas,
            }
        )

    return {
        "inicio": inicio,
        "fim": fim,
        "setor": setor,
        "minimo_isolados": minimo_isolados,
        "total_isolados": len(isolados),
        "metodologia": METODOLOGIA,
        "microrganismos": microrganismos,
    }
