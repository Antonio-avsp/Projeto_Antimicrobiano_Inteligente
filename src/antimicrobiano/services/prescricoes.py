"""Casos de uso de prescrições (UC02 — RF03, RF04, RN02, RN04–RN08)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from antimicrobiano.enums import StatusPrescricao
from antimicrobiano.erros import ConflitoDeEstado, RecursoNaoEncontrado, RegraDeNegocioViolada
from antimicrobiano.models import Prescricao
from antimicrobiano.schemas.prescricao import PrescricaoAtualizar, PrescricaoCriar
from antimicrobiano.services import antimicrobianos as servico_antimicrobianos


def registrar(sessao: Session, dados: PrescricaoCriar) -> Prescricao:
    """Registra a prescrição como ATIVA; o antimicrobiano deve existir e estar ativo (RN02)."""
    antimicrobiano = servico_antimicrobianos.obter(sessao, dados.antimicrobiano_id)
    if not antimicrobiano.ativo:
        raise RegraDeNegocioViolada("Antimicrobiano inativo não pode ser prescrito.")
    prescricao = Prescricao(**dados.model_dump())
    sessao.add(prescricao)
    sessao.commit()
    sessao.refresh(prescricao)
    return prescricao


def listar(
    sessao: Session,
    status: StatusPrescricao | None = None,
    setor: str | None = None,
    paciente_codigo: str | None = None,
) -> list[Prescricao]:
    """Lista prescrições da mais recente para a mais antiga, com filtros opcionais (RF04)."""
    consulta = select(Prescricao).order_by(Prescricao.data_inicio.desc(), Prescricao.id.desc())
    if status is not None:
        consulta = consulta.where(Prescricao.status == status)
    if setor:
        consulta = consulta.where(Prescricao.setor == setor)
    if paciente_codigo:
        consulta = consulta.where(Prescricao.paciente_codigo == paciente_codigo)
    return list(sessao.scalars(consulta))


def obter(sessao: Session, prescricao_id: int) -> Prescricao:
    """Retorna a prescrição ou lança 404."""
    prescricao = sessao.get(Prescricao, prescricao_id)
    if prescricao is None:
        raise RecursoNaoEncontrado(f"Prescrição {prescricao_id} não encontrada.")
    return prescricao


def garantir_ativa(prescricao: Prescricao) -> None:
    """RN08: prescrição encerrada não pode ser alterada, reavaliada ou encerrada novamente."""
    if prescricao.status != StatusPrescricao.ATIVA:
        raise ConflitoDeEstado(
            f"A prescrição {prescricao.id} está {prescricao.status.value} e não pode ser alterada."
        )


def atualizar(sessao: Session, prescricao_id: int, dados: PrescricaoAtualizar) -> Prescricao:
    """Atualiza os campos informados de uma prescrição ativa (RF04)."""
    prescricao = obter(sessao, prescricao_id)
    garantir_ativa(prescricao)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(prescricao, campo, valor)
    sessao.commit()
    sessao.refresh(prescricao)
    return prescricao
