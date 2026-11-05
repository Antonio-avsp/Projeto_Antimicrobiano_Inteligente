"""Enumerações do domínio (ver docs/modelo-de-dados.md, seção 4)."""

from enum import StrEnum


class CategoriaAware(StrEnum):
    """Classificação AWaRe da OMS (Access, Watch, Reserve)."""

    ACCESS = "ACCESS"
    WATCH = "WATCH"
    RESERVE = "RESERVE"

    @property
    def nivel(self) -> int:
        """Posição na hierarquia AWaRe usada no descalonamento (RN20)."""
        return _NIVEL_AWARE[self]


_NIVEL_AWARE = {CategoriaAware.ACCESS: 1, CategoriaAware.WATCH: 2, CategoriaAware.RESERVE: 3}
