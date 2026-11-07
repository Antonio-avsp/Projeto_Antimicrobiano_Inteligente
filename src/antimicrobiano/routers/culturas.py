"""Rotas de culturas e antibiogramas (UC04)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from antimicrobiano.database import SessaoDep
from antimicrobiano.enums import StatusCultura
from antimicrobiano.routers.dependencias import EditorMicrobiologiaDep, usuario_atual
from antimicrobiano.schemas.comum import RESPOSTA_401, RESPOSTA_403, RESPOSTA_404, RESPOSTA_422
from antimicrobiano.schemas.cultura import CulturaCriar, CulturaResposta, ResultadoCultura
from antimicrobiano.schemas.prescricao import PADRAO_CODIGO_PACIENTE
from antimicrobiano.services import culturas as servico

router = APIRouter(
    prefix="/culturas",
    tags=["Microbiologia"],
    dependencies=[Depends(usuario_atual)],
    responses={**RESPOSTA_401, **RESPOSTA_422},
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CulturaResposta,
    responses=RESPOSTA_403,
    summary="Registrar coleta de cultura",
)
def registrar_coleta(dados: CulturaCriar, sessao: SessaoDep, _editor: EditorMicrobiologiaDep):
    """Registra a coleta; a cultura fica PENDENTE até o resultado."""
    return servico.registrar_coleta(sessao, dados)


@router.get("", response_model=list[CulturaResposta], summary="Listar culturas")
def listar(
    sessao: SessaoDep,
    paciente_codigo: Annotated[str | None, Query(pattern=PADRAO_CODIGO_PACIENTE)] = None,
    status_cultura: Annotated[StatusCultura | None, Query(alias="status")] = None,
):
    """Lista culturas da coleta mais recente para a mais antiga."""
    return servico.listar(sessao, paciente_codigo, status_cultura)


@router.get(
    "/{cultura_id}",
    response_model=CulturaResposta,
    responses=RESPOSTA_404,
    summary="Consultar cultura",
)
def consultar(cultura_id: int, sessao: SessaoDep):
    """Consulta a cultura com o antibiograma."""
    return servico.obter(sessao, cultura_id)


@router.put(
    "/{cultura_id}/resultado",
    response_model=CulturaResposta,
    responses={**RESPOSTA_403, **RESPOSTA_404},
    summary="Registrar resultado e antibiograma",
)
def registrar_resultado(
    cultura_id: int, dados: ResultadoCultura, sessao: SessaoDep, _editor: EditorMicrobiologiaDep
):
    """Registra o resultado (POSITIVA com microrganismo e antibiograma, ou NEGATIVA)."""
    return servico.registrar_resultado(sessao, cultura_id, dados)
