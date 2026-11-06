"""Regras baseadas em tempo de terapia (RF07, RF08 — RN12 a RN14)."""

from antimicrobiano.enums import Indicacao, Severidade, TipoAlerta
from antimicrobiano.models import Prescricao
from antimicrobiano.regras.base import Alerta, ContextoAvaliacao, Regra


class RegraTimeout(Regra):
    """RN12: prescrição ativa há 72 horas ou mais sem reavaliação registrada."""

    tipo = TipoAlerta.TIMEOUT_REAVALIACAO
    severidade = Severidade.MEDIA

    def avaliar(self, prescricao: Prescricao, contexto: ContextoAvaliacao) -> list[Alerta]:
        limite = contexto.parametros.timeout_dias
        dias_de_uso = (contexto.data_referencia - prescricao.data_inicio).days
        reavaliada = any(
            r.data_reavaliacao <= contexto.data_referencia for r in prescricao.reavaliacoes
        )
        if dias_de_uso < limite or reavaliada:
            return []
        return [
            self._alerta(
                prescricao,
                mensagem=(
                    f"{prescricao.antimicrobiano.nome} em uso há {dias_de_uso} dias "
                    f"(≥ {limite * 24} horas) sem reavaliação registrada."
                ),
                recomendacao=(
                    "Realizar o time-out: confirmar o diagnóstico, revisar as culturas e definir "
                    "a conduta (manter, ajustar, descalonar ou suspender)."
                ),
                data_inicio=prescricao.data_inicio.isoformat(),
                dias_de_uso=dias_de_uso,
                limite_dias=limite,
            )
        ]


class RegraDuracaoExcedida(Regra):
    """RN13: dia de terapia maior que a duração prevista."""

    tipo = TipoAlerta.DURACAO_EXCEDIDA
    severidade = Severidade.MEDIA

    def avaliar(self, prescricao: Prescricao, contexto: ContextoAvaliacao) -> list[Alerta]:
        dia = prescricao.dia_de_terapia(contexto.data_referencia)
        if dia <= prescricao.duracao_prevista_dias:
            return []
        return [
            self._alerta(
                prescricao,
                mensagem=(
                    f"Tratamento com {prescricao.antimicrobiano.nome} no dia {dia} de terapia, "
                    f"acima da duração prevista de {prescricao.duracao_prevista_dias} dias."
                ),
                recomendacao=(
                    "Avaliar a suspensão do antimicrobiano ou registrar nova duração prevista "
                    "com justificativa clínica."
                ),
                dia_de_terapia=dia,
                duracao_prevista_dias=prescricao.duracao_prevista_dias,
            )
        ]


class RegraProfilaxiaProlongada(Regra):
    """RN14: profilaxia planejada por mais de 24 horas."""

    tipo = TipoAlerta.PROFILAXIA_PROLONGADA
    severidade = Severidade.MEDIA

    def avaliar(self, prescricao: Prescricao, contexto: ContextoAvaliacao) -> list[Alerta]:
        limite = contexto.parametros.limite_profilaxia_dias
        if (
            prescricao.indicacao != Indicacao.PROFILAXIA
            or prescricao.duracao_prevista_dias <= limite
        ):
            return []
        return [
            self._alerta(
                prescricao,
                mensagem=(
                    f"Profilaxia com {prescricao.antimicrobiano.nome} planejada para "
                    f"{prescricao.duracao_prevista_dias} dias (acima de "
                    f"{limite * 24} horas)."
                ),
                recomendacao=(
                    f"Suspender a profilaxia em até {limite * 24} horas após o procedimento, "
                    "salvo exceção justificada."
                ),
                duracao_prevista_dias=prescricao.duracao_prevista_dias,
                limite_dias=limite,
            )
        ]
