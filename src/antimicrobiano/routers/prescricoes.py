"""Rotas de prescrições (UC02) e das intervenções do PGA (UC03)."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from antimicrobiano.database import SessaoDep
from antimicrobiano.enums import StatusPrescricao
from antimicrobiano.schemas.comum import RESPOSTA_404, RESPOSTA_409
from antimicrobiano.schemas.prescricao import (
    PADRAO_CODIGO_PACIENTE,
    EncerramentoCriar,
    PrescricaoAtualizar,
    PrescricaoCriar,
    PrescricaoResposta,
    ReavaliacaoCriar,
    ReavaliacaoResposta,
)
from antimicrobiano.services import prescricoes as servico

router = APIRouter(prefix="/prescricoes", tags=["Prescrições"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=PrescricaoResposta,
    responses=RESPOSTA_404,
    summary="Registrar prescrição",
)
def registrar(dados: PrescricaoCriar, sessao: SessaoDep):
    """Registra a prescrição de um antimicrobiano ativo para um paciente pseudonimizado."""
    return servico.registrar(sessao, dados)


@router.get("", response_model=list[PrescricaoResposta], summary="Listar prescrições")
def listar(
    sessao: SessaoDep,
    status_prescricao: Annotated[StatusPrescricao | None, Query(alias="status")] = None,
    setor: Annotated[str | None, Query(max_length=60)] = None,
    paciente_codigo: Annotated[str | None, Query(pattern=PADRAO_CODIGO_PACIENTE)] = None,
):
    """Lista prescrições da mais recente para a mais antiga."""
    return servico.listar(sessao, status_prescricao, setor, paciente_codigo)


@router.get(
    "/{prescricao_id}",
    response_model=PrescricaoResposta,
    responses=RESPOSTA_404,
    summary="Consultar prescrição",
)
def consultar(prescricao_id: int, sessao: SessaoDep):
    """Consulta a prescrição, incluindo o dia de terapia atual."""
    return servico.obter(sessao, prescricao_id)


@router.patch(
    "/{prescricao_id}",
    response_model=PrescricaoResposta,
    responses={**RESPOSTA_404, **RESPOSTA_409},
    summary="Atualizar prescrição ativa",
)
def atualizar(prescricao_id: int, dados: PrescricaoAtualizar, sessao: SessaoDep):
    """Atualiza setor, dose, intervalo, via, duração prevista ou justificativa."""
    return servico.atualizar(sessao, prescricao_id, dados)


@router.post(
    "/{prescricao_id}/reavaliacoes",
    status_code=status.HTTP_201_CREATED,
    response_model=ReavaliacaoResposta,
    responses={**RESPOSTA_404, **RESPOSTA_409},
    summary="Registrar reavaliação (time-out)",
)
def registrar_reavaliacao(prescricao_id: int, dados: ReavaliacaoCriar, sessao: SessaoDep):
    """Registra a reavaliação estruturada da terapia; encerra o alerta de time-out."""
    return servico.registrar_reavaliacao(sessao, prescricao_id, dados)


@router.get(
    "/{prescricao_id}/reavaliacoes",
    response_model=list[ReavaliacaoResposta],
    responses=RESPOSTA_404,
    summary="Listar reavaliações",
)
def listar_reavaliacoes(prescricao_id: int, sessao: SessaoDep):
    """Histórico de reavaliações em ordem cronológica."""
    return servico.listar_reavaliacoes(sessao, prescricao_id)


@router.post(
    "/{prescricao_id}/encerramento",
    response_model=PrescricaoResposta,
    responses={**RESPOSTA_404, **RESPOSTA_409},
    summary="Encerrar prescrição",
)
def encerrar(prescricao_id: int, dados: EncerramentoCriar, sessao: SessaoDep):
    """Encerra a prescrição como CONCLUIDA ou SUSPENSA."""
    return servico.encerrar(sessao, prescricao_id, dados)
