"""Testes da configuração por variáveis de ambiente."""

from antimicrobiano.config import DATABASE_URL_PADRAO, Configuracao


def test_usa_sqlite_local_por_padrao(monkeypatch):
    monkeypatch.delenv("AMI_DATABASE_URL", raising=False)

    assert Configuracao.do_ambiente().database_url == DATABASE_URL_PADRAO


def test_database_url_pode_ser_sobrescrita(monkeypatch):
    monkeypatch.setenv("AMI_DATABASE_URL", "postgresql://usuario@localhost/ami")

    assert Configuracao.do_ambiente().database_url == "postgresql://usuario@localhost/ami"
