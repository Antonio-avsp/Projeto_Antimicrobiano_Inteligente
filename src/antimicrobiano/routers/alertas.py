"""Rotas do painel de alertas inteligentes (UC05)."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from antimicrobiano.database import SessaoDep
from antimicrobiano.enums import Severidade, TipoAlerta
from antimicrobiano.routers.dependencias import ParametrosDep, usuario_atual
from antimicrobiano.schemas.alerta import PainelAlertas
from antimicrobiano.schemas.comum import AVISO_APOIO_A_DECISAO, RESPOSTA_401, RESPOSTA_422
from antimicrobiano.schemas.prescricao import PADRAO_CODIGO_PACIENTE
from antimicrobiano.services import alertas as servico

router = APIRouter(
    prefix="/alertas",
    tags=["Alertas"],
    dependencies=[Depends(usuario_atual)],
    responses={**RESPOSTA_401, **RESPOSTA_422},
)


@router.get("", response_model=PainelAlertas, summary="Painel de alertas inteligentes")
def painel(
    sessao: SessaoDep,
    parametros: ParametrosDep,
    data_referencia: Annotated[
        date | None, Query(description="Data em que as regras são avaliadas. Padrão: hoje.")
    ] = None,
    tipo: TipoAlerta | None = None,
    severidade: Severidade | None = None,
    setor: Annotated[str | None, Query(max_length=60)] = None,
    paciente_codigo: Annotated[str | None, Query(pattern=PADRAO_CODIGO_PACIENTE)] = None,
):
    """Avalia as prescrições ativas e devolve os alertas filtrados, ordenados por severidade
    (ALTA → MEDIA → BAIXA) e com o resumo de quantidades."""
    referencia = data_referencia or date.today()
    alertas = servico.avaliar(
        sessao,
        referencia,
        parametros=parametros,
        tipo=tipo,
        severidade=severidade,
        setor=setor,
        paciente_codigo=paciente_codigo,
    )
    return PainelAlertas(
        data_referencia=referencia,
        aviso=AVISO_APOIO_A_DECISAO,
        total=len(alertas),
        resumo=servico.resumir(alertas),
        alertas=alertas,
    )
