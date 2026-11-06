"""Regras de política de uso de antimicrobianos (RF09, RF12 — RN15, RN16)."""

from antimicrobiano.enums import CategoriaAware, Indicacao, Severidade, TipoAlerta
from antimicrobiano.models import Prescricao
from antimicrobiano.regras.base import Alerta, ContextoAvaliacao, Regra

CATEGORIAS_AMPLO_ESPECTRO = frozenset({CategoriaAware.WATCH, CategoriaAware.RESERVE})


class RegraRestritoSemJustificativa(Regra):
    """RN15: antimicrobiano de uso restrito prescrito sem justificativa."""

    tipo = TipoAlerta.RESTRITO_SEM_JUSTIFICATIVA
    severidade = Severidade.ALTA

    def avaliar(self, prescricao: Prescricao, contexto: ContextoAvaliacao) -> list[Alerta]:
        if not prescricao.antimicrobiano.uso_restrito or prescricao.justificativa:
            return []
        return [
            self._alerta(
                prescricao,
                mensagem=(
                    f"{prescricao.antimicrobiano.nome} é de uso restrito e a prescrição "
                    "não possui justificativa."
                ),
                recomendacao=(
                    "Registrar a justificativa clínica na prescrição e solicitar a validação "
                    "da equipe do PGA."
                ),
                uso_restrito=True,
                categoria_aware=prescricao.antimicrobiano.categoria_aware.value,
            )
        ]


class RegraSemCultura(Regra):
    """RN16: WATCH/RESERVE empírico sem cultura coletada na janela de relevância."""

    tipo = TipoAlerta.SEM_CULTURA
    severidade = Severidade.MEDIA

    def avaliar(self, prescricao: Prescricao, contexto: ContextoAvaliacao) -> list[Alerta]:
        categoria = prescricao.antimicrobiano.categoria_aware
        if (
            prescricao.indicacao != Indicacao.EMPIRICA
            or categoria not in CATEGORIAS_AMPLO_ESPECTRO
            or contexto.culturas_relevantes(prescricao)
        ):
            return []
        return [
            self._alerta(
                prescricao,
                mensagem=(
                    f"{prescricao.antimicrobiano.nome} ({categoria.value}) iniciado "
                    "empiricamente sem cultura coletada."
                ),
                recomendacao=(
                    "Coletar culturas pertinentes ao sítio de infecção, idealmente antes da "
                    "próxima dose, para permitir o ajuste da terapia."
                ),
                categoria_aware=categoria.value,
                janela_de_culturas_dias=contexto.parametros.janela_cultura_dias,
            )
        ]
