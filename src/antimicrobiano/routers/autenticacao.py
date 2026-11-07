"""Rotas de autenticação e de administração de usuários (UC08 — RF17)."""

from fastapi import APIRouter, Request, status

from antimicrobiano.database import SessaoDep
from antimicrobiano.routers.dependencias import AdministradorDep, UsuarioDep
from antimicrobiano.schemas.comum import RESPOSTA_401, RESPOSTA_403, RESPOSTA_409, RESPOSTA_422
from antimicrobiano.schemas.usuario import (
    Credenciais,
    TokenAcesso,
    UsuarioCriar,
    UsuarioResposta,
)
from antimicrobiano.seguranca import criar_token
from antimicrobiano.services import usuarios as servico

router = APIRouter(tags=["Autenticação"], responses={**RESPOSTA_401, **RESPOSTA_422})


@router.post("/auth/login", response_model=TokenAcesso, summary="Entrar (obter token)")
def entrar(credenciais: Credenciais, sessao: SessaoDep, request: Request):
    """Confere login e senha e devolve um token Bearer com expiração."""
    usuario = servico.autenticar(sessao, credenciais.login, credenciais.senha)
    config = request.app.state.config
    token = criar_token(
        usuario.login, usuario.perfil, request.app.state.jwt_segredo, config.jwt_expiracao_minutos
    )
    return TokenAcesso(access_token=token.valor, expira_em=token.expira_em, usuario=usuario)


@router.get("/auth/me", response_model=UsuarioResposta, summary="Usuário autenticado")
def eu(usuario: UsuarioDep):
    """Dados do usuário dono do token."""
    return usuario


@router.post(
    "/usuarios",
    status_code=status.HTTP_201_CREATED,
    response_model=UsuarioResposta,
    responses={**RESPOSTA_403, **RESPOSTA_409},
    summary="Cadastrar usuário",
)
def cadastrar_usuario(dados: UsuarioCriar, sessao: SessaoDep, _gestor: AdministradorDep):
    """Cadastra um usuário com perfil de acesso (somente GESTOR)."""
    return servico.criar(sessao, dados)


@router.get(
    "/usuarios",
    response_model=list[UsuarioResposta],
    responses=RESPOSTA_403,
    summary="Listar usuários",
)
def listar_usuarios(sessao: SessaoDep, _gestor: AdministradorDep):
    """Lista os usuários (somente GESTOR)."""
    return servico.listar(sessao)
