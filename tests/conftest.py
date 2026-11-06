"""Fixtures compartilhadas: aplicação com banco SQLite em memória e cliente HTTP."""

from collections.abc import Iterator
from datetime import date, timedelta
from uuid import uuid4

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


@pytest.fixture
def nova_prescricao(client: TestClient, novo_antimicrobiano):
    """Fábrica de prescrições; cria um antimicrobiano padrão quando nenhum id é informado."""

    def _criar(antimicrobiano_id: int | None = None, **campos) -> dict:
        if antimicrobiano_id is None:
            antimicrobiano_id = novo_antimicrobiano(nome=f"Antimicrobiano {uuid4().hex[:8]}")["id"]
        dados = {
            "paciente_codigo": "PAC-0001",
            "setor": "Clínica Médica",
            "antimicrobiano_id": antimicrobiano_id,
            "dose": "1 g",
            "intervalo_horas": 24,
            "via": "IV",
            "indicacao": "EMPIRICA",
            "diagnostico": "Pneumonia comunitária",
            "data_inicio": (date.today() - timedelta(days=2)).isoformat(),
            "duracao_prevista_dias": 7,
        } | campos
        resposta = client.post("/prescricoes", json=dados)
        assert resposta.status_code == 201, resposta.text
        return resposta.json()

    return _criar
