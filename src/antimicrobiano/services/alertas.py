"""Caso de uso do painel de alertas (UC05 — RF07 a RF13)."""

from collections import Counter, defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from antimicrobiano.config import ParametrosClinicos
from antimicrobiano.enums import Severidade, StatusPrescricao, TipoAlerta
from antimicrobiano.models import Cultura, Prescricao
from antimicrobiano.regras import Alerta, ContextoAvaliacao, MotorDeRegras, criar_motor_padrao


def avaliar(
    sessao: Session,
    data_referencia: date,
    motor: MotorDeRegras | None = None,
    *,
    parametros: ParametrosClinicos | None = None,
    tipo: TipoAlerta | None = None,
    severidade: Severidade | None = None,
    setor: str | None = None,
    paciente_codigo: str | None = None,
) -> list[Alerta]:
    """Carrega as prescrições ativas uma única vez e aplica o motor de regras (RN11).

    Setor e paciente filtram as prescrições na consulta; tipo e severidade filtram os alertas.
    """
    consulta = select(Prescricao).where(Prescricao.status == StatusPrescricao.ATIVA)
    if setor:
        consulta = consulta.where(Prescricao.setor == setor)
    if paciente_codigo:
        consulta = consulta.where(Prescricao.paciente_codigo == paciente_codigo)
    prescricoes = sessao.scalars(consulta).all()
    contexto = ContextoAvaliacao(
        data_referencia=data_referencia,
        culturas_por_paciente=_culturas_por_paciente(sessao, prescricoes),
        parametros=parametros or ParametrosClinicos(),
    )
    alertas = (motor or criar_motor_padrao()).avaliar(prescricoes, contexto)
    return [
        alerta
        for alerta in alertas
        if (tipo is None or alerta.tipo == tipo)
        and (severidade is None or alerta.severidade == severidade)
    ]


def resumir(alertas: list[Alerta]) -> dict[str, dict]:
    """Contagem por severidade e por tipo, incluindo as categorias sem alertas."""
    por_severidade = Counter(alerta.severidade for alerta in alertas)
    por_tipo = Counter(alerta.tipo for alerta in alertas)
    return {
        "por_severidade": {s: por_severidade.get(s, 0) for s in Severidade},
        "por_tipo": {t: por_tipo.get(t, 0) for t in TipoAlerta},
    }


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
