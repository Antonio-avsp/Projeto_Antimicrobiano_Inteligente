"""Configuração da aplicação lida de variáveis de ambiente (prefixo ``AMI_``).

Além das variáveis do sistema, é lido o arquivo ``.env`` do diretório atual (copie o
``.env.example``). As variáveis já definidas no sistema têm prioridade sobre o arquivo.
``AMI_ARQUIVO_ENV`` indica outro arquivo; vazio desliga a leitura.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

DATABASE_URL_PADRAO = "sqlite:///./antimicrobiano.db"
NIVEIS_DE_LOG = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
TAMANHO_MINIMO_SEGREDO = 32

VARIAVEIS_PARAMETROS = {
    "timeout_dias": "AMI_TIMEOUT_DIAS",
    "limite_profilaxia_dias": "AMI_LIMITE_PROFILAXIA_DIAS",
    "janela_cultura_dias": "AMI_JANELA_CULTURA_DIAS",
    "minimo_isolados": "AMI_MINIMO_ISOLADOS",
}


class ConfiguracaoInvalida(ValueError):
    """Valor de configuração inválido; a mensagem indica a variável de ambiente."""


ARQUIVO_ENV_PADRAO = ".env"
_NOME_DE_VARIAVEL = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def ler_arquivo_env(caminho: str | Path) -> dict[str, str]:
    """Lê um arquivo ``CHAVE=valor`` (uma por linha); ``#`` inicia comentário.

    Aceita ``export CHAVE=valor`` e valores entre aspas simples ou duplas. Arquivo inexistente
    resulta em dicionário vazio.
    """
    arquivo = Path(caminho)
    if not arquivo.is_file():
        return {}
    valores: dict[str, str] = {}
    for numero, linha in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), start=1):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        chave, separador, valor = linha.removeprefix("export ").partition("=")
        chave, valor = chave.strip(), valor.strip()
        if not separador or not _NOME_DE_VARIAVEL.match(chave):
            raise ConfiguracaoInvalida(
                f"Linha {numero} de {arquivo} inválida: use o formato CHAVE=valor."
            )
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1]
        elif " #" in valor:
            valor = valor.split(" #", 1)[0].rstrip()
        valores[chave] = valor
    return valores


def ambiente_completo() -> dict[str, str]:
    """Variáveis do arquivo ``.env`` sobrepostas pelas variáveis do sistema."""
    caminho = os.environ.get("AMI_ARQUIVO_ENV", ARQUIVO_ENV_PADRAO)
    return {**(ler_arquivo_env(caminho) if caminho else {}), **os.environ}


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
        ambiente = ambiente_completo() if ambiente is None else ambiente
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
    jwt_segredo: str | None = None
    """Segredo de assinatura dos tokens (AMI_JWT_SEGREDO). Sem ele, um segredo temporário é
    gerado na inicialização e os tokens deixam de valer quando a API reinicia."""
    jwt_expiracao_minutos: int = 60

    def __post_init__(self) -> None:
        if self.jwt_segredo is not None and len(self.jwt_segredo) < TAMANHO_MINIMO_SEGREDO:
            raise ConfiguracaoInvalida(
                f"A variável AMI_JWT_SEGREDO deve ter pelo menos {TAMANHO_MINIMO_SEGREDO} "
                "caracteres."
            )
        if self.jwt_expiracao_minutos < 1:
            raise ConfiguracaoInvalida(
                "A variável AMI_JWT_EXPIRACAO_MINUTOS deve ser um número inteiro maior ou igual "
                f"a 1 (recebido: {self.jwt_expiracao_minutos!r})."
            )
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
        ambiente = ambiente_completo()
        return cls(
            database_url=ambiente.get("AMI_DATABASE_URL") or DATABASE_URL_PADRAO,
            parametros=ParametrosClinicos.do_ambiente(ambiente),
            log_nivel=ambiente.get("AMI_LOG_NIVEL", "").strip().upper() or "INFO",
            jwt_segredo=ambiente.get("AMI_JWT_SEGREDO") or None,
            jwt_expiracao_minutos=_inteiro_do_ambiente(ambiente, "AMI_JWT_EXPIRACAO_MINUTOS", 60),
        )


def _inteiro_do_ambiente(ambiente: Mapping[str, str], variavel: str, padrao: int) -> int:
    bruto = ambiente.get(variavel, "").strip()
    if not bruto:
        return padrao
    try:
        return int(bruto)
    except ValueError:
        raise ConfiguracaoInvalida(
            f"A variável {variavel} deve ser um número inteiro (recebido: {bruto!r})."
        ) from None
