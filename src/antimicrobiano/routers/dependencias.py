"""Dependências compartilhadas pelas rotas."""

from typing import Annotated

from fastapi import Depends, Request

from antimicrobiano.config import ParametrosClinicos


def obter_parametros(request: Request) -> ParametrosClinicos:
    """Parâmetros clínicos configurados na criação da aplicação (RNF11)."""
    return request.app.state.config.parametros


ParametrosDep = Annotated[ParametrosClinicos, Depends(obter_parametros)]
