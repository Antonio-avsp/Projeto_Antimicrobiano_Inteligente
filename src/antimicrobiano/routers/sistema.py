"""Rotas de sistema: verificação de saúde e redirecionamento para a documentação."""

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from antimicrobiano import __version__
from antimicrobiano.schemas.comum import AVISO_APOIO_A_DECISAO
from antimicrobiano.schemas.sistema import Saude

router = APIRouter(tags=["Sistema"])


@router.get("/", include_in_schema=False)
def raiz() -> RedirectResponse:
    """Redireciona a raiz para a documentação interativa."""
    return RedirectResponse(url="/docs")


@router.get("/health", response_model=Saude, summary="Verificar a saúde da API")
def health() -> Saude:
    """Informa se a API está no ar e qual versão está em execução."""
    return Saude(status="ok", versao=__version__, aviso=AVISO_APOIO_A_DECISAO)
