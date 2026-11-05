"""Configuração da aplicação lida de variáveis de ambiente (prefixo ``AMI_``)."""

from __future__ import annotations

import os
from dataclasses import dataclass

DATABASE_URL_PADRAO = "sqlite:///./antimicrobiano.db"


@dataclass(frozen=True)
class Configuracao:
    """Configuração imutável da aplicação."""

    database_url: str = DATABASE_URL_PADRAO

    @classmethod
    def do_ambiente(cls) -> Configuracao:
        """Monta a configuração a partir das variáveis de ambiente.

        ``AMI_DATABASE_URL`` permite trocar o banco (ex.: PostgreSQL) sem alterar código (RNF02).
        """
        return cls(database_url=os.getenv("AMI_DATABASE_URL", DATABASE_URL_PADRAO))
