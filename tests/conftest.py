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


@pytest.fixture
def novo_antimicrobiano(client: TestClient):
    """Fábrica que cadastra um antimicrobiano pela API e devolve o JSON criado."""

    def _criar(
        nome: str = "Ceftriaxona",
        classe: str = "Cefalosporina de 3ª geração",
        categoria_aware: str = "WATCH",
        uso_restrito: bool = False,
    ) -> dict:
        resposta = client.post(
            "/antimicrobianos",
            json={
                "nome": nome,
                "classe": classe,
                "categoria_aware": categoria_aware,
                "uso_restrito": uso_restrito,
            },
        )
        assert resposta.status_code == 201, resposta.text
        return resposta.json()

    return _criar
