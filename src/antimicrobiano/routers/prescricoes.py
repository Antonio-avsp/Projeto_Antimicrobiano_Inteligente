"""Rotas de prescrições (UC02)."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from antimicrobiano.database import SessaoDep
from antimicrobiano.enums import StatusPrescricao
from antimicrobiano.schemas.comum import RESPOSTA_404, RESPOSTA_409
from antimicrobiano.schemas.prescricao import (
    PADRAO_CODIGO_PACIENTE,
    PrescricaoAtualizar,
    PrescricaoCriar,
    PrescricaoResposta,
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
