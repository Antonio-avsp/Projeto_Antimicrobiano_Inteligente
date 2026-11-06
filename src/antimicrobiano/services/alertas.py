"""Caso de uso do painel de alertas (UC05 — RF07 a RF13)."""

from collections import defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from antimicrobiano.enums import StatusPrescricao
from antimicrobiano.models import Cultura, Prescricao
from antimicrobiano.regras import Alerta, ContextoAvaliacao, MotorDeRegras, criar_motor_padrao


def avaliar(
    sessao: Session, data_referencia: date, motor: MotorDeRegras | None = None
) -> list[Alerta]:
    """Carrega as prescrições ativas uma única vez e aplica o motor de regras (RN11)."""
    prescricoes = sessao.scalars(
        select(Prescricao).where(Prescricao.status == StatusPrescricao.ATIVA)
    ).all()
    contexto = ContextoAvaliacao(
        data_referencia=data_referencia,
        culturas_por_paciente=_culturas_por_paciente(sessao, prescricoes),
    )
    return (motor or criar_motor_padrao()).avaliar(prescricoes, contexto)


def _culturas_por_paciente(
    sessao: Session, prescricoes: list[Prescricao]
) -> dict[str, list[Cultura]]:
    """Carrega, em uma única consulta, as culturas dos pacientes com prescrição ativa."""
    codigos = {prescricao.paciente_codigo for prescricao in prescricoes}
    agrupadas: dict[str, list[Cultura]] = defaultdict(list)
    if codigos:
        consulta = select(Cultura).where(Cultura.paciente_codigo.in_(codigos))
        for cultura in sessao.scalars(consulta):
            agrupadas[cultura.paciente_codigo].append(cultura)
    return dict(agrupadas)
