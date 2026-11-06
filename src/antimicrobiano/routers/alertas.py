"""Rotas do painel de alertas inteligentes (UC05)."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from antimicrobiano.database import SessaoDep
from antimicrobiano.schemas.alerta import PainelAlertas
from antimicrobiano.schemas.comum import AVISO_APOIO_A_DECISAO
from antimicrobiano.services import alertas as servico

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get("", response_model=PainelAlertas, summary="Painel de alertas inteligentes")
def painel(
    sessao: SessaoDep,
    data_referencia: Annotated[
        date | None, Query(description="Data em que as regras são avaliadas. Padrão: hoje.")
    ] = None,
):
    """Avalia as prescrições ativas e devolve os alertas ordenados por severidade."""
    referencia = data_referencia or date.today()
    alertas = servico.avaliar(sessao, referencia)
    return PainelAlertas(
        data_referencia=referencia,
        aviso=AVISO_APOIO_A_DECISAO,
        total=len(alertas),
        alertas=alertas,
    )
