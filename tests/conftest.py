"""Fixtures compartilhadas: aplicação com banco SQLite em memória e cliente HTTP autenticado."""

from collections.abc import Iterator
from datetime import date, timedelta
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from antimicrobiano.config import Configuracao
from antimicrobiano.enums import Perfil
from antimicrobiano.main import create_app
from antimicrobiano.models import Usuario
from antimicrobiano.seguranca import criar_token, gerar_hash_de_senha

SEGREDO_TESTE = "segredo-de-teste-com-pelo-menos-32-caracteres"
SENHA_TESTE = "senha-de-teste"
HASH_SENHA_TESTE = gerar_hash_de_senha(
    SENHA_TESTE
)  # calculado uma vez: o scrypt é lento de propósito


@pytest.fixture(autouse=True)
def sem_arquivo_env(monkeypatch):
    """Isola os testes de um .env local do desenvolvedor."""
    monkeypatch.setenv("AMI_ARQUIVO_ENV", "")


@pytest.fixture
def app() -> FastAPI:
    """Aplicação isolada por teste, com banco em memória."""
    return create_app(Configuracao(database_url="sqlite://", jwt_segredo=SEGREDO_TESTE))


def criar_usuario(app: FastAPI, login: str, perfil: Perfil) -> None:
    """Cadastra um usuário (senha ``SENHA_TESTE``) direto no banco, sem depender de um GESTOR.

    Não faz nada se o login já existir.
    """
    with app.state.fabrica_sessoes() as sessao:
        if sessao.query(Usuario.id).filter_by(login=login).scalar():
            return
        sessao.add(
            Usuario(
                login=login, nome=f"Usuário {login}", perfil=perfil, senha_hash=HASH_SENHA_TESTE
            )
        )
        sessao.commit()


def cabecalho_de(cliente: TestClient, login: str) -> dict[str, str]:
    """Cabeçalho Authorization com um token válido do usuário (o login é testado à parte)."""
    with cliente.app.state.fabrica_sessoes() as sessao:
        perfil = sessao.query(Usuario.perfil).filter_by(login=login).scalar()
    token = criar_token(login, perfil, cliente.app.state.jwt_segredo, minutos=5)
    return {"Authorization": f"Bearer {token.valor}"}


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    """Cliente HTTP autenticado como GESTOR (acesso a todas as operações).

    O gerenciador de contexto executa o *lifespan* (criação das tabelas).
    """
    with TestClient(app) as cliente:
        criar_usuario(app, "gestor.teste", Perfil.GESTOR)
        cliente.headers.update(cabecalho_de(cliente, "gestor.teste"))
        yield cliente


@pytest.fixture
def como(app: FastAPI, client: TestClient):
    """Fábrica de cabeçalhos de autenticação para um usuário do perfil informado."""

    def _como(perfil: Perfil) -> dict[str, str]:
        login = f"{perfil.value.lower()}.teste"
        criar_usuario(app, login, perfil)
        return cabecalho_de(client, login)

    return _como


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


@pytest.fixture
def nova_cultura(client: TestClient):
    """Fábrica que registra a coleta e, opcionalmente, o resultado da cultura."""

    def _criar(
        paciente_codigo: str = "PAC-0001",
        setor: str = "UTI Adulto",
        material: str = "SANGUE",
        data_coleta: str | None = None,
        resultado: dict | None = None,
    ) -> dict:
        dados = {"paciente_codigo": paciente_codigo, "setor": setor, "material": material}
        if data_coleta:
            dados["data_coleta"] = data_coleta
        resposta = client.post("/culturas", json=dados)
        assert resposta.status_code == 201, resposta.text
        cultura = resposta.json()
        if resultado is not None:
            resposta = client.put(f"/culturas/{cultura['id']}/resultado", json=resultado)
            assert resposta.status_code == 200, resposta.text
            cultura = resposta.json()
        return cultura

    return _criar
