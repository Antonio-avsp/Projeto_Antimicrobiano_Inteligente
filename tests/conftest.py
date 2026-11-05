"""Fixtures compartilhadas: aplicação com banco SQLite em memória e cliente HTTP."""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from antimicrobiano.config import Configuracao
from antimicrobiano.main import create_app


@pytest.fixture
def app() -> FastAPI:
    """Aplicação isolada por teste, com banco em memória."""
    return create_app(Configuracao(database_url="sqlite://"))


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    """Cliente HTTP; o gerenciador de contexto executa o *lifespan* (criação das tabelas)."""
    with TestClient(app) as cliente:
        yield cliente
