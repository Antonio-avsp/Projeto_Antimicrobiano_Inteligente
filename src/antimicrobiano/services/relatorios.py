"""Relatórios gerenciais (UC06 e UC07 — RF14, RF15, RN19, RN23)."""

from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from antimicrobiano.enums import CategoriaAware, Interpretacao, StatusCultura, StatusPrescricao
from antimicrobiano.erros import RegraDeNegocioViolada
from antimicrobiano.models import Cultura, Prescricao
from antimicrobiano.texto import normalizar

METODOLOGIA = (
    "Culturas positivas do período; somente o primeiro isolado por paciente e microrganismo "
    "(CLSI M39). Percentual de sensibilidade = S ÷ testados × 100. Combinações com menos isolados "
    "testados que o mínimo configurado são sinalizadas como amostra insuficiente."
)


METODOLOGIA_DOT = (
    "Dias de terapia (DOT): cada dia de calendário em que o paciente recebeu o antimicrobiano "
    "conta 1, independentemente do número de doses. Contam os dias entre o início da prescrição "
    "e o término (ou hoje, se ainda ativa) que caem dentro do período; dias do mesmo "
    "antimicrobiano para o mesmo paciente não são contados duas vezes. Percentual ACCESS = DOT "
    "ACCESS ÷ DOT total × 100 (meta da OMS: ao menos 60%)."
)
META_ACCESS_OMS = 60.0


def _validar_periodo(inicio: date, fim: date) -> None:
    if inicio > fim:
        raise RegraDeNegocioViolada("A data inicial do período não pode ser posterior à final.")


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
    _validar_periodo(inicio, fim)
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


def _percentual(parte: int, total: int) -> float | None:
    return round(100 * parte / total, 1) if total else None


def indicadores_de_consumo(
    sessao: Session, inicio: date, fim: date, hoje: date, setor: str | None = None
) -> dict:
    """Dias de terapia (DOT) do período por antimicrobiano, categoria AWaRe e setor (RF15)."""
    _validar_periodo(inicio, fim)
    ultimo_dia = min(fim, hoje)
    consulta = select(Prescricao).where(Prescricao.data_inicio <= ultimo_dia)
    if setor:
        consulta = consulta.where(Prescricao.setor == setor)

    dias_por_uso: dict[tuple[str, int], set[date]] = defaultdict(set)
    setor_do_uso: dict[tuple[str, int], dict[date, str]] = defaultdict(dict)
    antimicrobianos = {}
    for prescricao in sessao.scalars(consulta):
        termino = prescricao.data_fim if prescricao.status != StatusPrescricao.ATIVA else hoje
        primeiro, ultimo = max(prescricao.data_inicio, inicio), min(termino or hoje, ultimo_dia)
        chave = (prescricao.paciente_codigo, prescricao.antimicrobiano_id)
        antimicrobianos[prescricao.antimicrobiano_id] = prescricao.antimicrobiano
        dia = primeiro
        while dia <= ultimo:
            dias_por_uso[chave].add(dia)
            setor_do_uso[chave].setdefault(dia, prescricao.setor)
            dia += timedelta(days=1)

    por_antimicrobiano: dict[int, dict] = {}
    por_setor: dict[str, int] = defaultdict(int)
    for (paciente, antimicrobiano_id), dias in dias_por_uso.items():
        if not dias:
            continue
        linha = por_antimicrobiano.setdefault(antimicrobiano_id, {"dot": 0, "pacientes": set()})
        linha["dot"] += len(dias)
        linha["pacientes"].add(paciente)
        for dia in dias:
            por_setor[setor_do_uso[(paciente, antimicrobiano_id)][dia]] += 1

    total = sum(linha["dot"] for linha in por_antimicrobiano.values())
    por_categoria = dict.fromkeys(CategoriaAware, 0)
    for antimicrobiano_id, linha in por_antimicrobiano.items():
        por_categoria[antimicrobianos[antimicrobiano_id].categoria_aware] += linha["dot"]
    percentual_access = _percentual(por_categoria[CategoriaAware.ACCESS], total)
    return {
        "inicio": inicio,
        "fim": fim,
        "setor": setor,
        "metodologia": METODOLOGIA_DOT,
        "total_dot": total,
        "percentual_access": percentual_access,
        "meta_access_oms": META_ACCESS_OMS,
        "atinge_meta_access": None
        if percentual_access is None
        else percentual_access >= META_ACCESS_OMS,
        "por_categoria": [
            {"categoria_aware": categoria, "dot": dot, "percentual": _percentual(dot, total)}
            for categoria, dot in por_categoria.items()
        ],
        "por_antimicrobiano": sorted(
            (
                {
                    "antimicrobiano": antimicrobianos[antimicrobiano_id].nome,
                    "classe": antimicrobianos[antimicrobiano_id].classe,
                    "categoria_aware": antimicrobianos[antimicrobiano_id].categoria_aware,
                    "dot": linha["dot"],
                    "pacientes": len(linha["pacientes"]),
                }
                for antimicrobiano_id, linha in por_antimicrobiano.items()
            ),
            key=lambda item: (-item["dot"], normalizar(item["antimicrobiano"])),
        ),
        "por_setor": sorted(
            ({"setor": nome, "dot": dot} for nome, dot in por_setor.items()),
            key=lambda item: (-item["dot"], normalizar(item["setor"])),
        ),
    }
