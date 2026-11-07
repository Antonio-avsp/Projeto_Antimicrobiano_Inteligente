"""Administração de usuários pela linha de comando (cadastro do primeiro GESTOR).

Uso::

    python -m antimicrobiano.usuarios criar --login ana.souza --nome "Ana Souza" --perfil GESTOR

A senha é lida de ``AMI_SENHA_NOVO_USUARIO`` (uso não interativo, ex.: Docker) ou digitada
duas vezes no terminal. Depois do primeiro GESTOR, os demais usuários podem ser cadastrados
pela API em ``POST /usuarios``.
"""

from __future__ import annotations

import argparse
import getpass
import os

from pydantic import ValidationError

from antimicrobiano.config import Configuracao
from antimicrobiano.database import Base, criar_engine, criar_fabrica_sessoes
from antimicrobiano.enums import Perfil
from antimicrobiano.erros import ErroDeDominio
from antimicrobiano.schemas.usuario import UsuarioCriar
from antimicrobiano.services import usuarios as servico


def _ler_senha() -> str:
    senha = os.getenv("AMI_SENHA_NOVO_USUARIO")
    if senha:
        return senha
    senha = getpass.getpass("Senha (mínimo de 8 caracteres): ")
    if senha != getpass.getpass("Repita a senha: "):
        raise SystemExit("As senhas não conferem.")
    return senha


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada de ``python -m antimicrobiano.usuarios``."""
    parser = argparse.ArgumentParser(description="Administra os usuários da API.")
    comandos = parser.add_subparsers(dest="comando", required=True)
    criar = comandos.add_parser("criar", help="cadastra um usuário")
    criar.add_argument("--login", required=True)
    criar.add_argument("--nome", required=True)
    criar.add_argument("--perfil", required=True, choices=[perfil.value for perfil in Perfil])
    argumentos = parser.parse_args(argv)

    try:
        dados = UsuarioCriar(
            login=argumentos.login,
            nome=argumentos.nome,
            perfil=argumentos.perfil,
            senha=_ler_senha(),
        )
    except ValidationError as erro:
        for item in erro.errors():
            print(f"Valor inválido em '{item['loc'][0]}': {item['msg']}")
        return 2

    engine = criar_engine(Configuracao.do_ambiente().database_url)
    try:
        Base.metadata.create_all(engine)
        with criar_fabrica_sessoes(engine)() as sessao:
            usuario = servico.criar(sessao, dados)
    except ErroDeDominio as erro:
        print(erro.mensagem)
        return 1
    finally:
        engine.dispose()
    print(f"Usuário '{usuario.login}' ({usuario.perfil.value}) cadastrado.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
