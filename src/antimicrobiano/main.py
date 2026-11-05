"""Ponto de entrada da API Antimicrobiano Inteligente."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from antimicrobiano import __version__
from antimicrobiano.config import Configuracao
from antimicrobiano.database import Base, criar_engine, criar_fabrica_sessoes
from antimicrobiano.routers import sistema

DESCRICAO = """
API de apoio ao **Programa de Gerenciamento do Uso de Antimicrobianos (PGA / stewardship)**.

Centraliza prescrições, culturas e antibiogramas e gera alertas explicáveis para a equipe do PGA.

> ⚠️ Ferramenta de apoio à decisão para fins acadêmicos — não substitui o julgamento clínico.
"""

TAGS = [
    {"name": "Sistema", "description": "Saúde e versão da API."},
]


def create_app(config: Configuracao | None = None) -> FastAPI:
    """Cria e configura a aplicação FastAPI (padrão *application factory*)."""
    config = config or Configuracao.do_ambiente()
    engine = criar_engine(config.database_url)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        Base.metadata.create_all(bind=engine)
        yield
        engine.dispose()

    app = FastAPI(
        title="Antimicrobiano Inteligente",
        version=__version__,
        description=DESCRICAO,
        openapi_tags=TAGS,
        lifespan=lifespan,
    )
    app.state.config = config
    app.state.engine = engine
    app.state.fabrica_sessoes = criar_fabrica_sessoes(engine)

    app.include_router(sistema.router)
    return app


app = create_app()
