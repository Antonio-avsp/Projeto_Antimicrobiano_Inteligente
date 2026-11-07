"""Dependências compartilhadas pelas rotas: parâmetros clínicos, usuário autenticado e perfis."""

from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from antimicrobiano.config import ParametrosClinicos
from antimicrobiano.database import SessaoDep
from antimicrobiano.enums import Perfil
from antimicrobiano.erros import AcessoNegado, NaoAutenticado
from antimicrobiano.models import Usuario
from antimicrobiano.seguranca import ler_token
from antimicrobiano.services import usuarios as servico_usuarios

# RN24: perfis autorizados por grupo de operações de escrita.
# A leitura é permitida a qualquer usuário autenticado.
PERFIS_CATALOGO = frozenset({Perfil.FARMACEUTICO, Perfil.GESTOR})
PERFIS_PRESCRICOES = frozenset({Perfil.FARMACEUTICO, Perfil.INFECTOLOGISTA, Perfil.GESTOR})
PERFIS_MICROBIOLOGIA = frozenset({Perfil.LABORATORIO, Perfil.GESTOR})
PERFIS_USUARIOS = frozenset({Perfil.GESTOR})


def obter_parametros(request: Request) -> ParametrosClinicos:
    """Parâmetros clínicos configurados na criação da aplicação (RNF11)."""
    return request.app.state.config.parametros


ParametrosDep = Annotated[ParametrosClinicos, Depends(obter_parametros)]

_esquema_bearer = HTTPBearer(
    auto_error=False,
    scheme_name="Token de acesso",
    description="Token obtido em POST /auth/login (cabeçalho Authorization: Bearer <token>).",
)


def usuario_atual(
    request: Request,
    sessao: SessaoDep,
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(_esquema_bearer)],
) -> Usuario:
    """Usuário dono do token Bearer; ``401`` se o token faltar, for inválido ou tiver expirado."""
    if credenciais is None:
        raise NaoAutenticado("Token de acesso ausente. Faça login em POST /auth/login.")
    login = ler_token(credenciais.credentials, request.app.state.jwt_segredo)
    if login is None:
        raise NaoAutenticado("Token de acesso inválido ou expirado. Faça login novamente.")
    usuario = servico_usuarios.obter_ativo(sessao, login)
    if usuario is None:
        raise NaoAutenticado("O usuário do token não existe ou está inativo.")
    return usuario


UsuarioDep = Annotated[Usuario, Depends(usuario_atual)]


def exigir_perfis(perfis: frozenset[Perfil]):
    """Dependência que permite a operação apenas aos perfis informados (``403`` aos demais)."""

    def _verificar(usuario: UsuarioDep) -> Usuario:
        if usuario.perfil not in perfis:
            autorizados = ", ".join(sorted(perfil.value for perfil in perfis))
            raise AcessoNegado(
                f"O perfil {usuario.perfil.value} não tem permissão para esta operação "
                f"(perfis autorizados: {autorizados})."
            )
        return usuario

    return _verificar


EditorCatalogoDep = Annotated[Usuario, Depends(exigir_perfis(PERFIS_CATALOGO))]
EditorPrescricoesDep = Annotated[Usuario, Depends(exigir_perfis(PERFIS_PRESCRICOES))]
EditorMicrobiologiaDep = Annotated[Usuario, Depends(exigir_perfis(PERFIS_MICROBIOLOGIA))]
AdministradorDep = Annotated[Usuario, Depends(exigir_perfis(PERFIS_USUARIOS))]
