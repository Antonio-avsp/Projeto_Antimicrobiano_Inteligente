"""Configuração da aplicação lida de variáveis de ambiente (prefixo ``AMI_``)."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

DATABASE_URL_PADRAO = "sqlite:///./antimicrobiano.db"
NIVEIS_DE_LOG = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

VARIAVEIS_PARAMETROS = {
    "timeout_dias": "AMI_TIMEOUT_DIAS",
    "limite_profilaxia_dias": "AMI_LIMITE_PROFILAXIA_DIAS",
    "janela_cultura_dias": "AMI_JANELA_CULTURA_DIAS",
    "minimo_isolados": "AMI_MINIMO_ISOLADOS",
}


class ConfiguracaoInvalida(ValueError):
    """Valor de configuração inválido; a mensagem indica a variável de ambiente."""


@dataclass(frozen=True)
class ParametrosClinicos:
    """Parâmetros clínicos do motor de regras e dos relatórios (RNF11).

    Os valores padrão seguem as diretrizes usadas na especificação; protocolos institucionais
    podem ajustá-los por variáveis de ambiente sem alterar o código.
    """

    timeout_dias: int = 3
    """Dias de uso sem reavaliação que disparam o time-out (3 dias = 72 horas — RN12)."""
    limite_profilaxia_dias: int = 1
    """Duração máxima recomendada para profilaxia (1 dia = 24 horas — RN14)."""
    janela_cultura_dias: int = 7
    """Dias antes do início da terapia em que uma cultura é considerada relevante (RN11)."""
    minimo_isolados: int = 30
    """Mínimo de isolados para amostra suficiente no antibiograma cumulativo (RN19)."""

    def __post_init__(self) -> None:
        for nome in VARIAVEIS_PARAMETROS:
            valor = getattr(self, nome)
            if isinstance(valor, bool) or not isinstance(valor, int) or valor < 1:
                raise ConfiguracaoInvalida(
                    f"O parâmetro '{nome}' deve ser um inteiro maior ou igual a 1 "
                    f"(recebido: {valor!r})."
                )

    @classmethod
    def do_ambiente(cls, ambiente: Mapping[str, str] | None = None) -> ParametrosClinicos:
        """Lê ``AMI_TIMEOUT_DIAS``, ``AMI_LIMITE_PROFILAXIA_DIAS``, ``AMI_JANELA_CULTURA_DIAS``
        e ``AMI_MINIMO_ISOLADOS``; variáveis ausentes mantêm o valor padrão."""
        ambiente = os.environ if ambiente is None else ambiente
        valores: dict[str, int] = {}
        for nome, variavel in VARIAVEIS_PARAMETROS.items():
            bruto = ambiente.get(variavel, "").strip()
            if not bruto:
                continue
            try:
                valor = int(bruto)
            except ValueError:
                valor = 0
            if valor < 1:
                raise ConfiguracaoInvalida(
                    f"A variável {variavel} deve ser um número inteiro maior ou igual a 1 "
                    f"(recebido: {bruto!r})."
                )
            valores[nome] = valor
        return cls(**valores)


@dataclass(frozen=True)
class Configuracao:
    """Configuração imutável da aplicação."""

    database_url: str = DATABASE_URL_PADRAO
    parametros: ParametrosClinicos = field(default_factory=ParametrosClinicos)
    log_nivel: str = "INFO"

    def __post_init__(self) -> None:
        if self.log_nivel not in NIVEIS_DE_LOG:
            raise ConfiguracaoInvalida(
                f"A variável AMI_LOG_NIVEL deve ser um destes: {', '.join(NIVEIS_DE_LOG)} "
                f"(recebido: {self.log_nivel!r})."
            )

    @classmethod
    def do_ambiente(cls) -> Configuracao:
        """Monta a configuração a partir das variáveis de ambiente.

        ``AMI_DATABASE_URL`` permite trocar o banco (ex.: PostgreSQL) sem alterar código (RNF02).
        """
        return cls(
            database_url=os.getenv("AMI_DATABASE_URL", DATABASE_URL_PADRAO),
            parametros=ParametrosClinicos.do_ambiente(),
            log_nivel=os.getenv("AMI_LOG_NIVEL", "INFO").strip().upper() or "INFO",
        )
