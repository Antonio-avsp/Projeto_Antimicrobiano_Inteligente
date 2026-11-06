"""Caso de uso do painel de alertas (UC05 — RF07 a RF13)."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from antimicrobiano.enums import StatusPrescricao
from antimicrobiano.models import Prescricao
from antimicrobiano.regras import Alerta, ContextoAvaliacao, MotorDeRegras, criar_motor_padrao


def avaliar(
    sessao: Session, data_referencia: date, motor: MotorDeRegras | None = None
) -> list[Alerta]:
    """Carrega as prescrições ativas uma única vez e aplica o motor de regras (RN11)."""
    prescricoes = sessao.scalars(
        select(Prescricao).where(Prescricao.status == StatusPrescricao.ATIVA)
    ).all()
    contexto = ContextoAvaliacao(data_referencia=data_referencia)
    return (motor or criar_motor_padrao()).avaliar(prescricoes, contexto)
