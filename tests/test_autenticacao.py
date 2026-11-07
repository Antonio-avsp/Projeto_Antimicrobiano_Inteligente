"""Autenticação e perfis de acesso — US17 (RF17, RN24, RNF05)."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest

from antimicrobiano import usuarios as cli_usuarios
from antimicrobiano.config import Configuracao, ConfiguracaoInvalida
from antimicrobiano.enums import Perfil
from antimicrobiano.models import Usuario
from antimicrobiano.seguranca import gerar_hash_de_senha, verificar_senha
from tests.conftest import SEGREDO_TESTE, SENHA_TESTE, criar_usuario

SEM_TOKEN = {"Authorization": ""}


# --- Login --------------------------------------------------------------------------------------


def test_login_valido_devolve_token_com_expiracao(app, client):
    criar_usuario(app, "ana.farmacia", Perfil.FARMACEUTICO)

    resposta = client.post("/auth/login", json={"login": "ana.farmacia", "senha": SENHA_TESTE})

    corpo = resposta.json()
    assert resposta.status_code == 200
    assert corpo["token_type"] == "bearer"
    assert corpo["usuario"] == corpo["usuario"] | {
        "login": "ana.farmacia",
        "perfil": "FARMACEUTICO",
    }
    expira_em = datetime.fromisoformat(corpo["expira_em"])
    assert timedelta(minutes=59) < expira_em - datetime.now(UTC) <= timedelta(minutes=60)
    eu = client.get("/auth/me", headers={"Authorization": f"Bearer {corpo['access_token']}"})
    assert eu.json()["login"] == "ana.farmacia"


@pytest.mark.parametrize("credenciais", [("gestor.teste", "senha-errada"), ("ninguem", "x")])
def test_credenciais_invalidas_retornam_401_com_a_mesma_mensagem(client, credenciais):
    login, senha = credenciais

    resposta = client.post("/auth/login", json={"login": login, "senha": senha})

    assert resposta.status_code == 401
    assert resposta.headers["WWW-Authenticate"] == "Bearer"
    assert resposta.json()["codigo"] == "NAO_AUTENTICADO"
    assert resposta.json()["mensagem"] == "Login ou senha inválidos."


def test_login_ignora_maiusculas_e_espacos(client):
    resposta = client.post("/auth/login", json={"login": " GESTOR.Teste ", "senha": SENHA_TESTE})

    assert resposta.status_code == 200


# --- Token --------------------------------------------------------------------------------------


def test_requisicao_sem_token_retorna_401(client):
    resposta = client.get("/alertas", headers=SEM_TOKEN)

    assert resposta.status_code == 401
    assert "Token de acesso ausente" in resposta.json()["mensagem"]


def _token(segredo: str, expira_em: datetime, login: str = "gestor.teste") -> dict:
    valor = jwt.encode({"sub": login, "exp": expira_em}, segredo, algorithm="HS256")
    return {"Authorization": f"Bearer {valor}"}


@pytest.mark.parametrize(
    "cabecalho",
    [
        {"Authorization": "Bearer nao-e-um-jwt"},
        _token(SEGREDO_TESTE, datetime.now(UTC) - timedelta(minutes=1)),
        _token("outro-segredo-com-mais-de-32-caracteres!!", datetime.now(UTC) + timedelta(hours=1)),
    ],
    ids=["mal-formado", "expirado", "assinatura-invalida"],
)
def test_token_invalido_retorna_401(client, cabecalho):
    resposta = client.get("/prescricoes", headers=cabecalho)

    assert resposta.status_code == 401
    assert "inválido ou expirado" in resposta.json()["mensagem"]


def test_token_de_usuario_inativado_deixa_de_valer(app, client):
    with app.state.fabrica_sessoes() as sessao:
        sessao.query(Usuario).filter_by(login="gestor.teste").update({"ativo": False})
        sessao.commit()

    resposta = client.get("/antimicrobianos")

    assert resposta.status_code == 401


def test_rotas_publicas_dispensam_token(client):
    for rota in ("/health", "/docs", "/openapi.json"):
        assert client.get(rota, headers=SEM_TOKEN).status_code == 200


def test_openapi_declara_o_esquema_bearer(client):
    esquema = client.get("/openapi.json").json()

    assert esquema["components"]["securitySchemes"]["Token de acesso"]["scheme"] == "bearer"


# --- Perfis (RN24) ------------------------------------------------------------------------------


def _corpo_prescricao(antimicrobiano_id: int) -> dict:
    return {
        "paciente_codigo": "PAC-0001",
        "setor": "UTI Adulto",
        "antimicrobiano_id": antimicrobiano_id,
        "dose": "1 g",
        "intervalo_horas": 8,
        "via": "IV",
        "indicacao": "EMPIRICA",
        "diagnostico": "Sepse",
        "data_inicio": datetime.now(UTC).date().isoformat(),
        "duracao_prevista_dias": 7,
    }


def test_perfil_sem_papel_de_prescritor_recebe_403_ao_prescrever(client, como, novo_antimicrobiano):
    """Critério da Avaliação Técnica Week_01 (issue 03)."""
    resposta = client.post(
        "/prescricoes",
        json=_corpo_prescricao(novo_antimicrobiano()["id"]),
        headers=como(Perfil.LABORATORIO),
    )

    assert resposta.status_code == 403
    assert resposta.json()["codigo"] == "ACESSO_NEGADO"
    assert "LABORATORIO" in resposta.json()["mensagem"]


def test_laboratorio_nao_pode_inativar_antimicrobiano(client, como, novo_antimicrobiano):
    """Cenário da US17."""
    am = novo_antimicrobiano()

    resposta = client.delete(f"/antimicrobianos/{am['id']}", headers=como(Perfil.LABORATORIO))

    assert resposta.status_code == 403
    assert client.get(f"/antimicrobianos/{am['id']}").json()["ativo"] is True


@pytest.mark.parametrize(
    ("perfil", "metodo", "rota", "corpo", "esperado"),
    [
        (Perfil.FARMACEUTICO, "post", "/antimicrobianos", "catalogo", 201),
        (Perfil.INFECTOLOGISTA, "post", "/antimicrobianos", "catalogo", 403),
        (Perfil.LABORATORIO, "post", "/culturas", "cultura", 201),
        (Perfil.FARMACEUTICO, "post", "/culturas", "cultura", 403),
        (Perfil.INFECTOLOGISTA, "post", "/prescricoes", "prescricao", 201),
        (Perfil.FARMACEUTICO, "post", "/prescricoes", "prescricao", 201),
        (Perfil.GESTOR, "post", "/prescricoes", "prescricao", 201),
    ],
)
def test_matriz_de_permissoes_de_escrita(
    client, como, novo_antimicrobiano, perfil, metodo, rota, corpo, esperado
):
    corpos = {
        "catalogo": {"nome": "Nova", "classe": "Classe", "categoria_aware": "ACCESS"},
        "cultura": {"paciente_codigo": "PAC-0001", "setor": "UTI Adulto", "material": "SANGUE"},
        "prescricao": _corpo_prescricao(novo_antimicrobiano()["id"]),
    }

    resposta = client.request(metodo, rota, json=corpos[corpo], headers=como(perfil))

    assert resposta.status_code == esperado, resposta.text


@pytest.mark.parametrize("perfil", list(Perfil))
def test_todos_os_perfis_consultam_o_painel_e_os_relatorios(client, como, perfil):
    cabecalho = como(perfil)

    for rota in ("/alertas", "/relatorios/indicadores", "/relatorios/antibiograma-cumulativo"):
        assert client.get(rota, headers=cabecalho).status_code == 200


def test_intervencoes_registram_o_autor(client, como, nova_prescricao):
    prescricao = nova_prescricao()
    infecto = como(Perfil.INFECTOLOGISTA)

    reavaliacao = client.post(
        f"/prescricoes/{prescricao['id']}/reavaliacoes", json={"conduta": "MANTER"}, headers=infecto
    ).json()
    encerrada = client.post(
        f"/prescricoes/{prescricao['id']}/encerramento",
        json={"status_final": "CONCLUIDA"},
        headers=infecto,
    ).json()

    assert prescricao["registrado_por"] == "gestor.teste"
    assert reavaliacao["registrado_por"] == "infectologista.teste"
    assert encerrada["encerrado_por"] == "infectologista.teste"


# --- Usuários -----------------------------------------------------------------------------------


def test_gestor_cadastra_usuario_com_senha_apenas_em_hash(app, client):
    novo = {"login": "joao.lab", "nome": "João Lima", "perfil": "LABORATORIO", "senha": "segura123"}

    resposta = client.post("/usuarios", json=novo)

    assert resposta.status_code == 201
    assert "senha" not in resposta.text
    with app.state.fabrica_sessoes() as sessao:
        senha_hash = sessao.query(Usuario.senha_hash).filter_by(login="joao.lab").scalar()
    assert senha_hash.startswith("scrypt$") and "segura123" not in senha_hash
    assert client.post("/usuarios", json=novo).status_code == 409
    assert [u["login"] for u in client.get("/usuarios").json()] == ["gestor.teste", "joao.lab"]


def test_apenas_gestor_administra_usuarios(client, como):
    resposta = client.get("/usuarios", headers=como(Perfil.FARMACEUTICO))

    assert resposta.status_code == 403


@pytest.mark.parametrize(
    ("campo", "valor"), [("login", "Com Espaço"), ("senha", "curta"), ("perfil", "AUDITOR")]
)
def test_dados_invalidos_de_usuario(client, campo, valor):
    dados = {"login": "maria", "nome": "Maria", "perfil": "GESTOR", "senha": "segura123"}

    resposta = client.post("/usuarios", json=dados | {campo: valor})

    assert resposta.status_code == 422
    assert resposta.json()["campos"][0]["campo"] == campo


# --- Segurança e configuração -------------------------------------------------------------------


def test_hash_de_senha():
    senha_hash = gerar_hash_de_senha("correta-123")

    assert verificar_senha("correta-123", senha_hash)
    assert not verificar_senha("errada-123", senha_hash)
    assert not verificar_senha("correta-123", "formato-invalido")
    assert gerar_hash_de_senha("correta-123") != senha_hash  # sal aleatório


def test_segredo_curto_impede_a_inicializacao():
    with pytest.raises(ConfiguracaoInvalida, match="AMI_JWT_SEGREDO"):
        Configuracao(jwt_segredo="curto")


@pytest.mark.parametrize("valor", ["0", "abc"])
def test_expiracao_invalida(monkeypatch, valor):
    monkeypatch.setenv("AMI_JWT_EXPIRACAO_MINUTOS", valor)

    with pytest.raises(ConfiguracaoInvalida, match="AMI_JWT_EXPIRACAO_MINUTOS"):
        Configuracao.do_ambiente()


def test_configuracao_de_autenticacao_pelo_ambiente(monkeypatch):
    monkeypatch.setenv("AMI_JWT_SEGREDO", SEGREDO_TESTE)
    monkeypatch.setenv("AMI_JWT_EXPIRACAO_MINUTOS", "15")

    config = Configuracao.do_ambiente()

    assert (config.jwt_segredo, config.jwt_expiracao_minutos) == (SEGREDO_TESTE, 15)


# --- Linha de comando ---------------------------------------------------------------------------


def test_comando_cria_o_primeiro_gestor(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AMI_DATABASE_URL", f"sqlite:///{tmp_path / 'cli.db'}")
    monkeypatch.setenv("AMI_SENHA_NOVO_USUARIO", "senha-forte-1")
    argumentos = ["criar", "--login", "ana.souza", "--nome", "Ana Souza", "--perfil", "GESTOR"]

    assert cli_usuarios.main(argumentos) == 0
    assert "cadastrado" in capsys.readouterr().out
    assert cli_usuarios.main(argumentos) == 1  # login repetido
    assert "Já existe" in capsys.readouterr().out
    assert (
        cli_usuarios.main(["criar", "--login", "X Y", "--nome", "Ana", "--perfil", "GESTOR"]) == 2
    )
