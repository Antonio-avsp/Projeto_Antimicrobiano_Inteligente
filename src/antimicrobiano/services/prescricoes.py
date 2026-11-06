"""Casos de uso de prescrições (UC02 e UC03 — RF03 a RF05, RN02, RN04–RN09)."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from antimicrobiano.enums import StatusPrescricao
from antimicrobiano.erros import ConflitoDeEstado, RecursoNaoEncontrado, RegraDeNegocioViolada
from antimicrobiano.models import Prescricao, Reavaliacao
from antimicrobiano.schemas.prescricao import (
    EncerramentoCriar,
    PrescricaoAtualizar,
    PrescricaoCriar,
    ReavaliacaoCriar,
)
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


def _validar_data_no_tratamento(prescricao: Prescricao, data_informada: date, rotulo: str) -> None:
    """RN09: datas de reavaliação e de término não podem anteceder o início da terapia."""
    if data_informada < prescricao.data_inicio:
        raise RegraDeNegocioViolada(
            f"A data de {rotulo} não pode ser anterior ao início da prescrição "
            f"({prescricao.data_inicio:%d/%m/%Y})."
        )


def registrar_reavaliacao(
    sessao: Session, prescricao_id: int, dados: ReavaliacaoCriar
) -> Reavaliacao:
    """Registra o time-out de uma prescrição ativa (RF05)."""
    prescricao = obter(sessao, prescricao_id)
    garantir_ativa(prescricao)
    _validar_data_no_tratamento(prescricao, dados.data_reavaliacao, "reavaliação")
    reavaliacao = Reavaliacao(**dados.model_dump())
    prescricao.reavaliacoes.append(reavaliacao)
    sessao.commit()
    sessao.refresh(reavaliacao)
    return reavaliacao


def listar_reavaliacoes(sessao: Session, prescricao_id: int) -> list[Reavaliacao]:
    """Histórico de reavaliações em ordem cronológica."""
    return list(obter(sessao, prescricao_id).reavaliacoes)


def encerrar(sessao: Session, prescricao_id: int, dados: EncerramentoCriar) -> Prescricao:
    """Encerra a prescrição como concluída ou suspensa (RF05); ela deixa de gerar alertas."""
    prescricao = obter(sessao, prescricao_id)
    garantir_ativa(prescricao)
    _validar_data_no_tratamento(prescricao, dados.data_fim, "término")
    prescricao.status = StatusPrescricao(dados.status_final)
    prescricao.data_fim = dados.data_fim
    prescricao.motivo_encerramento = dados.motivo
    sessao.commit()
    sessao.refresh(prescricao)
    return prescricao
