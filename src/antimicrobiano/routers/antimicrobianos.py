"""Rotas do catálogo de antimicrobianos (UC01)."""

from fastapi import APIRouter, Query, Response, status

from antimicrobiano.database import SessaoDep
from antimicrobiano.enums import CategoriaAware
from antimicrobiano.schemas.antimicrobiano import (
    AntimicrobianoAtualizar,
    AntimicrobianoCriar,
    AntimicrobianoResposta,
)
from antimicrobiano.schemas.comum import RESPOSTA_404, RESPOSTA_409
from antimicrobiano.services import antimicrobianos as servico

router = APIRouter(prefix="/antimicrobianos", tags=["Antimicrobianos"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=AntimicrobianoResposta,
    responses=RESPOSTA_409,
    summary="Cadastrar antimicrobiano",
)
def cadastrar(dados: AntimicrobianoCriar, sessao: SessaoDep):
    """Cadastra um antimicrobiano ativo. O nome é único (RN01)."""
    return servico.criar(sessao, dados)


@router.get("", response_model=list[AntimicrobianoResposta], summary="Listar antimicrobianos")
def listar(
    sessao: SessaoDep,
    categoria_aware: CategoriaAware | None = None,
    uso_restrito: bool | None = None,
    ativo: bool | None = Query(True, description="Padrão: somente ativos."),
    busca: str | None = Query(None, min_length=1, max_length=80, description="Trecho do nome."),
):
    """Lista o catálogo ordenado por nome."""
    return servico.listar(sessao, categoria_aware, uso_restrito, ativo, busca)


@router.get(
    "/{antimicrobiano_id}",
    response_model=AntimicrobianoResposta,
    responses=RESPOSTA_404,
    summary="Consultar antimicrobiano",
)
def consultar(antimicrobiano_id: int, sessao: SessaoDep):
    """Consulta um antimicrobiano, inclusive inativo."""
    return servico.obter(sessao, antimicrobiano_id)


@router.patch(
    "/{antimicrobiano_id}",
    response_model=AntimicrobianoResposta,
    responses={**RESPOSTA_404, **RESPOSTA_409},
    summary="Atualizar antimicrobiano",
)
def atualizar(antimicrobiano_id: int, dados: AntimicrobianoAtualizar, sessao: SessaoDep):
    """Atualiza os campos informados."""
    return servico.atualizar(sessao, antimicrobiano_id, dados)


@router.delete(
    "/{antimicrobiano_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPOSTA_404,
    summary="Inativar antimicrobiano",
)
def inativar(antimicrobiano_id: int, sessao: SessaoDep) -> Response:
    """Inativa o antimicrobiano (exclusão lógica — RN03)."""
    servico.inativar(sessao, antimicrobiano_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
