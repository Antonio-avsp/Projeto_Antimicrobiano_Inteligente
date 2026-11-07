"""Contratos de autenticação e usuários (RF17)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from antimicrobiano.enums import Perfil

PADRAO_LOGIN = r"^[a-z0-9._-]{3,40}$"


class Credenciais(BaseModel):
    """Login e senha para obter o token de acesso."""

    login: str = Field(min_length=1, max_length=40, examples=["farmaceutico.demo"])
    senha: str = Field(min_length=1, max_length=128, examples=["senha-demo"])


class UsuarioResposta(BaseModel):
    """Usuário sem dados sensíveis."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    nome: str
    perfil: Perfil
    ativo: bool
    criado_em: datetime


class TokenAcesso(BaseModel):
    """Token Bearer para o cabeçalho ``Authorization``."""

    access_token: str
    token_type: str = "bearer"
    expira_em: datetime
    usuario: UsuarioResposta


class UsuarioCriar(BaseModel):
    """Dados para cadastrar um usuário."""

    model_config = ConfigDict(str_strip_whitespace=True)

    login: str = Field(
        pattern=PADRAO_LOGIN,
        examples=["ana.souza"],
        description="Letras minúsculas, números, ponto, hífen ou sublinhado (3 a 40).",
    )
    nome: str = Field(min_length=3, max_length=120, examples=["Ana Souza"])
    perfil: Perfil
    senha: str = Field(min_length=8, max_length=128, description="Mínimo de 8 caracteres.")
