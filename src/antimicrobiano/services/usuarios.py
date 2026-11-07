"""Casos de uso de usuários e autenticação (UC08 — RF17, RN24)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from antimicrobiano.enums import Perfil
from antimicrobiano.erros import ConflitoDeEstado, NaoAutenticado
from antimicrobiano.models import Usuario
from antimicrobiano.schemas.usuario import UsuarioCriar
from antimicrobiano.seguranca import gerar_hash_de_senha, verificar_senha

MENSAGEM_CREDENCIAIS = "Login ou senha inválidos."


def criar(sessao: Session, dados: UsuarioCriar) -> Usuario:
    """Cadastra o usuário com a senha armazenada apenas como hash (RNF05)."""
    if sessao.scalar(select(Usuario).where(Usuario.login == dados.login)):
        raise ConflitoDeEstado(f"Já existe um usuário com o login '{dados.login}'.")
    usuario = Usuario(
        login=dados.login,
        nome=dados.nome,
        perfil=Perfil(dados.perfil),
        senha_hash=gerar_hash_de_senha(dados.senha),
    )
    sessao.add(usuario)
    sessao.commit()
    sessao.refresh(usuario)
    return usuario


def listar(sessao: Session) -> list[Usuario]:
    """Usuários ordenados pelo login."""
    return list(sessao.scalars(select(Usuario).order_by(Usuario.login)))


def obter_ativo(sessao: Session, login: str) -> Usuario | None:
    """Usuário ativo com o login informado, se existir."""
    return sessao.scalar(select(Usuario).where(Usuario.login == login, Usuario.ativo.is_(True)))


def autenticar(sessao: Session, login: str, senha: str) -> Usuario:
    """Confere as credenciais; a mesma mensagem é usada para login ou senha errados."""
    usuario = obter_ativo(sessao, login.strip().lower())
    if usuario is None or not verificar_senha(senha, usuario.senha_hash):
        raise NaoAutenticado(MENSAGEM_CREDENCIAIS)
    return usuario
