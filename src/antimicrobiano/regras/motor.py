"""Motor de regras: aplica cada regra (Strategy) a cada prescrição ativa (RN11, RN21)."""

from collections.abc import Iterable, Sequence

from antimicrobiano.enums import StatusPrescricao, TipoAlerta
from antimicrobiano.models import Prescricao
from antimicrobiano.regras.base import Alerta, ContextoAvaliacao, Regra
from antimicrobiano.regras.microbiologicas import RegraDescalonamento, RegraResistencia
from antimicrobiano.regras.politicas import (
    RegraDuplicidadeTerapeutica,
    RegraRestritoSemJustificativa,
    RegraSemCultura,
)
from antimicrobiano.regras.temporais import (
    RegraDuracaoExcedida,
    RegraProfilaxiaProlongada,
    RegraTimeout,
)


def ordenar(alertas: Iterable[Alerta]) -> list[Alerta]:
    """RN21: severidade (ALTA → BAIXA), depois tipo e prescrição."""
    tipos = list(TipoAlerta)
    return sorted(alertas, key=lambda a: (a.severidade.ordem, tipos.index(a.tipo), a.prescricao_id))


class MotorDeRegras:
    """Orquestra as regras; novas regras são adicionadas sem alterar as existentes (RNF07)."""

    def __init__(self, regras: Sequence[Regra]) -> None:
        self._regras = tuple(regras)

    @property
    def regras(self) -> tuple[Regra, ...]:
        return self._regras

    def avaliar(
        self, prescricoes: Iterable[Prescricao], contexto: ContextoAvaliacao
    ) -> list[Alerta]:
        """Avalia apenas prescrições ativas e devolve os alertas já ordenados."""
        alertas: list[Alerta] = []
        for prescricao in prescricoes:
            if prescricao.status != StatusPrescricao.ATIVA:
                continue
            for regra in self._regras:
                alertas.extend(regra.avaliar(prescricao, contexto))
        return ordenar(alertas)


def criar_motor_padrao() -> MotorDeRegras:
    """Motor com todas as regras clínicas implementadas."""
    return MotorDeRegras(
        [
            RegraTimeout(),
            RegraDuracaoExcedida(),
            RegraProfilaxiaProlongada(),
            RegraRestritoSemJustificativa(),
            RegraSemCultura(),
            RegraResistencia(),
            RegraDescalonamento(),
            RegraDuplicidadeTerapeutica(),
        ]
    )
