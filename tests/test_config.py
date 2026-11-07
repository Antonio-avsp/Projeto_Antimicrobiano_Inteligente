"""Testes da configuração por variáveis de ambiente (RNF02, RNF11)."""

import os
import shutil
import subprocess
from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from antimicrobiano.config import (
    DATABASE_URL_PADRAO,
    VARIAVEIS_PARAMETROS,
    Configuracao,
    ConfiguracaoInvalida,
    ParametrosClinicos,
    ler_arquivo_env,
)
from antimicrobiano.enums import Perfil
from antimicrobiano.main import create_app
from tests.conftest import cabecalho_de, criar_usuario


def test_usa_sqlite_local_por_padrao(monkeypatch):
    monkeypatch.delenv("AMI_DATABASE_URL", raising=False)

    assert Configuracao.do_ambiente().database_url == DATABASE_URL_PADRAO


def test_database_url_pode_ser_sobrescrita(monkeypatch):
    monkeypatch.setenv("AMI_DATABASE_URL", "postgresql://usuario@localhost/ami")

    assert Configuracao.do_ambiente().database_url == "postgresql://usuario@localhost/ami"


# --- #18: parâmetros clínicos configuráveis (RNF11) -------------------------------------------


@pytest.fixture
def sem_variaveis_ami(monkeypatch):
    for variavel in VARIAVEIS_PARAMETROS.values():
        monkeypatch.delenv(variavel, raising=False)


def test_valores_padrao_dos_parametros_clinicos(sem_variaveis_ami):
    parametros = ParametrosClinicos.do_ambiente()

    assert parametros == ParametrosClinicos(
        timeout_dias=3, limite_profilaxia_dias=1, janela_cultura_dias=7, minimo_isolados=30
    )
    assert Configuracao.do_ambiente().parametros == parametros


def test_parametros_sobrescritos_por_variaveis_de_ambiente(monkeypatch):
    monkeypatch.setenv("AMI_TIMEOUT_DIAS", "2")
    monkeypatch.setenv("AMI_LIMITE_PROFILAXIA_DIAS", " 2 ")
    monkeypatch.setenv("AMI_JANELA_CULTURA_DIAS", "10")
    monkeypatch.setenv("AMI_MINIMO_ISOLADOS", "50")

    assert ParametrosClinicos.do_ambiente() == ParametrosClinicos(2, 2, 10, 50)


@pytest.mark.parametrize("valor", ["0", "-1", "abc", "2.5"])
def test_valor_invalido_indica_a_variavel(monkeypatch, valor):
    monkeypatch.setenv("AMI_TIMEOUT_DIAS", valor)

    with pytest.raises(ConfiguracaoInvalida, match="AMI_TIMEOUT_DIAS"):
        ParametrosClinicos.do_ambiente()


def test_parametro_invalido_na_construcao_direta():
    with pytest.raises(ConfiguracaoInvalida, match="minimo_isolados"):
        ParametrosClinicos(minimo_isolados=0)


def test_timeout_de_48_horas_configurado_por_ambiente(monkeypatch, sem_variaveis_ami):
    monkeypatch.setenv("AMI_DATABASE_URL", "sqlite://")
    monkeypatch.setenv("AMI_TIMEOUT_DIAS", "2")
    dois_dias_atras = (date.today() - timedelta(days=2)).isoformat()

    app = create_app()
    with TestClient(app) as cliente:
        criar_usuario(app, "gestor.teste", Perfil.GESTOR)
        cliente.headers.update(cabecalho_de(cliente, "gestor.teste"))
        antimicrobiano = cliente.post(
            "/antimicrobianos",
            json={"nome": "Ceftriaxona", "classe": "Cefalosporina", "categoria_aware": "WATCH"},
        ).json()
        cliente.post(
            "/prescricoes",
            json={
                "paciente_codigo": "PAC-0001",
                "setor": "UTI Adulto",
                "antimicrobiano_id": antimicrobiano["id"],
                "dose": "1 g",
                "intervalo_horas": 24,
                "via": "IV",
                "indicacao": "DIRIGIDA",
                "diagnostico": "Pneumonia",
                "data_inicio": dois_dias_atras,
                "duracao_prevista_dias": 7,
            },
        )
        painel = cliente.get("/alertas").json()

    timeout = next(a for a in painel["alertas"] if a["tipo"] == "TIMEOUT_REAVALIACAO")
    assert timeout["evidencias"]["limite_dias"] == 2
    assert "48 horas" in timeout["mensagem"]


# --- Arquivo .env e .env.example ----------------------------------------------------------------

RAIZ = Path(__file__).resolve().parent.parent


def test_leitura_do_arquivo_env(tmp_path):
    arquivo = tmp_path / ".env"
    arquivo.write_text(
        '# comentário\n\nAMI_A=1\nexport AMI_B = dois \nAMI_C="com # cerquilha"\n'
        "AMI_D='aspas simples'\nAMI_E=valor # comentário no fim\nAMI_F=\n",
        encoding="utf-8",
    )

    assert ler_arquivo_env(arquivo) == {
        "AMI_A": "1",
        "AMI_B": "dois",
        "AMI_C": "com # cerquilha",
        "AMI_D": "aspas simples",
        "AMI_E": "valor",
        "AMI_F": "",
    }
    assert ler_arquivo_env(tmp_path / "inexistente") == {}


@pytest.mark.parametrize("linha", ["SEM_IGUAL", "1INVALIDA=x", "COM ESPACO=x"])
def test_linha_invalida_no_arquivo_env(tmp_path, linha):
    arquivo = tmp_path / ".env"
    arquivo.write_text(f"AMI_OK=1\n{linha}\n", encoding="utf-8")

    with pytest.raises(ConfiguracaoInvalida, match="Linha 2"):
        ler_arquivo_env(arquivo)


def test_configuracao_lida_do_arquivo_e_sistema_tem_prioridade(tmp_path, monkeypatch):
    arquivo = tmp_path / "config.env"
    arquivo.write_text("AMI_TIMEOUT_DIAS=5\nAMI_LOG_NIVEL=debug\n", encoding="utf-8")
    monkeypatch.setenv("AMI_ARQUIVO_ENV", str(arquivo))
    monkeypatch.delenv("AMI_TIMEOUT_DIAS", raising=False)
    monkeypatch.setenv("AMI_LOG_NIVEL", "ERROR")

    config = Configuracao.do_ambiente()

    assert config.parametros.timeout_dias == 5
    assert config.log_nivel == "ERROR"


def test_env_example_documenta_e_configura_a_aplicacao(monkeypatch):
    """Critério da issue: um clone limpo roda apenas com o .env.example copiado."""
    exemplo = RAIZ / ".env.example"
    variaveis = ler_arquivo_env(exemplo)
    for variavel in list(os.environ):
        if variavel.startswith("AMI_"):
            monkeypatch.delenv(variavel)
    monkeypatch.setenv("AMI_ARQUIVO_ENV", str(exemplo))

    config = Configuracao.do_ambiente()

    assert set(VARIAVEIS_PARAMETROS.values()) <= set(variaveis)
    assert {"AMI_DATABASE_URL", "AMI_JWT_SEGREDO", "AMI_LOG_NIVEL", "AMI_SENHA_DEMO"} <= set(
        variaveis
    )
    assert config.database_url == variaveis["AMI_DATABASE_URL"]
    assert config.parametros == ParametrosClinicos()
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    assert all(f"`{variavel}`" in readme for variavel in variaveis)


@pytest.mark.skipif(shutil.which("git") is None, reason="git indisponível")
def test_env_ignorado_e_env_example_versionado():
    def ignorado(caminho: str) -> bool:
        return (
            subprocess.run(["git", "check-ignore", "-q", caminho], cwd=RAIZ, check=False).returncode
            == 0
        )

    assert ignorado(".env")
    assert not ignorado(".env.example")
