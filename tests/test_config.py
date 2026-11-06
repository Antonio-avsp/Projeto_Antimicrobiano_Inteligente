"""Testes da configuração por variáveis de ambiente (RNF02, RNF11)."""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from antimicrobiano.config import (
    DATABASE_URL_PADRAO,
    VARIAVEIS_PARAMETROS,
    Configuracao,
    ConfiguracaoInvalida,
    ParametrosClinicos,
)
from antimicrobiano.main import create_app


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

    with TestClient(create_app()) as cliente:
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
