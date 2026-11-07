"""Interface web do painel de alertas (RF18): página estática que consome a API."""

from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

PASTA_WEB = Path(__file__).resolve().parent.parent / "web"

router = APIRouter(include_in_schema=False)


@router.get("/painel")
def painel() -> FileResponse:
    """Página do painel; o login e os dados são obtidos pelo navegador na própria API."""
    return FileResponse(PASTA_WEB / "painel.html", media_type="text/html")


def registrar_interface_web(app: FastAPI) -> None:
    """Inclui a página do painel e os arquivos estáticos (CSS e JavaScript)."""
    app.include_router(router)
    app.mount("/painel/static", StaticFiles(directory=PASTA_WEB), name="painel-static")
