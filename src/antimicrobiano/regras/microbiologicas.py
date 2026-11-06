"""Regras que cruzam a prescrição com o antibiograma (RF10, RF11 — RN17, RN18, RN20)."""

from antimicrobiano.enums import Interpretacao, Severidade, StatusCultura, TipoAlerta
from antimicrobiano.models import Antimicrobiano, Cultura, Prescricao
from antimicrobiano.regras.base import Alerta, ContextoAvaliacao, Regra
from antimicrobiano.regras.politicas import CATEGORIAS_AMPLO_ESPECTRO
from antimicrobiano.texto import normalizar


def _positivas(culturas: list[Cultura]) -> list[Cultura]:
    return [cultura for cultura in culturas if cultura.status == StatusCultura.POSITIVA]


def _interpretacao(cultura: Cultura, antimicrobiano_id: int) -> Interpretacao | None:
    for item in cultura.antibiograma:
        if item.antimicrobiano_id == antimicrobiano_id:
            return item.interpretacao
    return None


def sensiveis_em_todas(culturas: list[Cultura]) -> list[Antimicrobiano]:
    """Antimicrobianos ativos com ``S`` em todas as culturas, do ACCESS ao RESERVE (RN20)."""
    if not culturas:
        return []
    por_id: dict[int, Antimicrobiano] = {}
    conjuntos: list[set[int]] = []
    for cultura in culturas:
        sensiveis = {
            item.antimicrobiano_id
            for item in cultura.antibiograma
            if item.interpretacao == Interpretacao.S and item.antimicrobiano.ativo
        }
        por_id.update(
            {item.antimicrobiano_id: item.antimicrobiano for item in cultura.antibiograma}
        )
        conjuntos.append(sensiveis)
    comuns = set.intersection(*conjuntos)
    return sorted(
        (por_id[i] for i in comuns),
        key=lambda a: (a.categoria_aware.nivel, normalizar(a.nome)),
    )


def _rotulo(antimicrobiano: Antimicrobiano) -> str:
    return f"{antimicrobiano.nome} ({antimicrobiano.categoria_aware.value})"


def _resumo(cultura: Cultura) -> dict:
    return {
        "cultura_id": cultura.id,
        "material": cultura.material.value,
        "data_coleta": cultura.data_coleta.isoformat(),
        "microrganismo": cultura.microrganismo,
    }


class RegraResistencia(Regra):
    """RN17: cultura relevante com microrganismo resistente ao antimicrobiano prescrito."""

    tipo = TipoAlerta.RESISTENCIA
    severidade = Severidade.ALTA

    def avaliar(self, prescricao: Prescricao, contexto: ContextoAvaliacao) -> list[Alerta]:
        prescrito = prescricao.antimicrobiano
        positivas = _positivas(contexto.culturas_relevantes(prescricao))
        resistentes = [c for c in positivas if _interpretacao(c, prescrito.id) == Interpretacao.R]
        if not resistentes:
            return []
        alternativas = [a for a in sensiveis_em_todas(positivas) if a.id != prescrito.id]
        if alternativas:
            recomendacao = (
                "Revisar a terapia. Alternativas sensíveis no antibiograma: "
                + ", ".join(_rotulo(a) for a in alternativas)
                + "."
            )
        else:
            recomendacao = (
                "Revisar a terapia com o infectologista: não há alternativa sensível comum "
                "a todas as culturas positivas."
            )
        microrganismos = ", ".join(sorted({c.microrganismo or "" for c in resistentes}))
        return [
            self._alerta(
                prescricao,
                mensagem=(
                    f"{microrganismos} resistente a {prescrito.nome} em cultura do paciente: "
                    "terapia possivelmente inadequada."
                ),
                recomendacao=recomendacao,
                culturas=[_resumo(c) for c in resistentes],
                alternativas=[a.nome for a in alternativas],
            )
        ]


class RegraDescalonamento(Regra):
    """RN18: antibiograma permite antimicrobiano de categoria AWaRe inferior."""

    tipo = TipoAlerta.DESCALONAMENTO
    severidade = Severidade.BAIXA

    def avaliar(self, prescricao: Prescricao, contexto: ContextoAvaliacao) -> list[Alerta]:
        prescrito = prescricao.antimicrobiano
        if prescrito.categoria_aware not in CATEGORIAS_AMPLO_ESPECTRO:
            return []
        positivas = _positivas(contexto.culturas_relevantes(prescricao))
        if not positivas or any(
            _interpretacao(c, prescrito.id) == Interpretacao.R for c in positivas
        ):
            return []
        opcoes = [
            a
            for a in sensiveis_em_todas(positivas)
            if a.categoria_aware.nivel < prescrito.categoria_aware.nivel
        ]
        if not opcoes:
            return []
        return [
            self._alerta(
                prescricao,
                mensagem=(
                    f"O antibiograma permite descalonar {_rotulo(prescrito)} para antimicrobiano "
                    "de categoria AWaRe inferior."
                ),
                recomendacao=(
                    "Considerar o descalonamento para: "
                    + ", ".join(_rotulo(a) for a in opcoes)
                    + "."
                ),
                culturas=[_resumo(c) for c in positivas],
                opcoes=[
                    {"nome": a.nome, "categoria_aware": a.categoria_aware.value} for a in opcoes
                ],
            )
        ]
