"""Conexão com o banco de dados e gerenciamento de sessões do SQLAlchemy."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

URLS_EM_MEMORIA = {"sqlite://", "sqlite:///:memory:"}


class Base(DeclarativeBase):
    """Classe base de todas as entidades ORM."""


def criar_engine(database_url: str) -> Engine:
    """Cria a engine do SQLAlchemy.

    No SQLite, habilita chaves estrangeiras (desligadas por padrão) e, para bancos em
    memória, compartilha uma única conexão entre as sessões (usado nos testes).
    """
    if not database_url.startswith("sqlite"):
        return create_engine(database_url)

    opcoes: dict = {"connect_args": {"check_same_thread": False}}
    if database_url in URLS_EM_MEMORIA:
        opcoes["poolclass"] = StaticPool
    engine = create_engine(database_url, **opcoes)

    @event.listens_for(engine, "connect")
    def _habilitar_chaves_estrangeiras(conexao_dbapi, _registro) -> None:
        cursor = conexao_dbapi.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def criar_fabrica_sessoes(engine: Engine) -> sessionmaker[Session]:
    """Cria a fábrica de sessões vinculada à engine."""
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db(request: Request) -> Iterator[Session]:
    """Dependência do FastAPI que fornece uma sessão por requisição."""
    sessao = request.app.state.fabrica_sessoes()
    try:
        yield sessao
    finally:
        sessao.close()


SessaoDep = Annotated[Session, Depends(get_db)]
"""Atalho para injetar a sessão nas rotas."""
