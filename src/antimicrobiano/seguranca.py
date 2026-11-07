"""Senhas com hash scrypt e tokens JWT de acesso (RF17, RNF05)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt

from antimicrobiano.enums import Perfil

ALGORITMO = "HS256"
_SCRYPT = {"n": 2**14, "r": 8, "p": 1}


def gerar_hash_de_senha(senha: str) -> str:
    """Hash scrypt com sal aleatório no formato ``scrypt$n$r$p$sal$hash`` (base64)."""
    sal = secrets.token_bytes(16)
    resumo = hashlib.scrypt(senha.encode(), salt=sal, **_SCRYPT)
    codificar = lambda dado: base64.b64encode(dado).decode()  # noqa: E731
    return (
        f"scrypt${_SCRYPT['n']}${_SCRYPT['r']}${_SCRYPT['p']}${codificar(sal)}${codificar(resumo)}"
    )


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Compara a senha com o hash em tempo constante."""
    try:
        algoritmo, n, r, p, sal, resumo = senha_hash.split("$")
        if algoritmo != "scrypt":
            return False
        calculado = hashlib.scrypt(
            senha.encode(), salt=base64.b64decode(sal), n=int(n), r=int(r), p=int(p)
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(calculado, base64.b64decode(resumo))


@dataclass(frozen=True)
class Token:
    """Token de acesso emitido no login."""

    valor: str
    expira_em: datetime


def criar_token(login: str, perfil: Perfil, segredo: str, minutos: int) -> Token:
    """Emite um JWT assinado com o login (``sub``), o perfil e a expiração."""
    agora = datetime.now(UTC)
    expira_em = agora + timedelta(minutes=minutos)
    carga = {"sub": login, "perfil": perfil.value, "iat": agora, "exp": expira_em}
    return Token(jwt.encode(carga, segredo, algorithm=ALGORITMO), expira_em)


def ler_token(valor: str, segredo: str) -> str | None:
    """Devolve o login do token válido, ou ``None`` se inválido, adulterado ou expirado."""
    try:
        carga = jwt.decode(
            valor, segredo, algorithms=[ALGORITMO], options={"require": ["exp", "sub"]}
        )
    except jwt.PyJWTError:
        return None
    return carga["sub"]
