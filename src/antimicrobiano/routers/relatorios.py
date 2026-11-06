"""Rotas de relatórios (UC06)."""

from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Query

from antimicrobiano.database import SessaoDep
from antimicrobiano.routers.dependencias import ParametrosDep
from antimicrobiano.schemas.relatorio import AntibiogramaCumulativo
from antimicrobiano.services import relatorios as servico

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


@router.get(
    "/antibiograma-cumulativo",
    response_model=AntibiogramaCumulativo,
    summary="Gerar antibiograma cumulativo",
)
def antibiograma_cumulativo(
    sessao: SessaoDep,
    parametros: ParametrosDep,
    inicio: Annotated[date | None, Query(description="Padrão: 12 meses antes do fim.")] = None,
    fim: Annotated[date | None, Query(description="Padrão: hoje.")] = None,
    setor: Annotated[str | None, Query(max_length=60)] = None,
):
    """Perfil local de sensibilidade por microrganismo e antimicrobiano (CLSI M39)."""
    fim = fim or date.today()
    inicio = inicio or fim - timedelta(days=364)
    return servico.antibiograma_cumulativo(
        sessao, inicio, fim, minimo_isolados=parametros.minimo_isolados, setor=setor
    )
