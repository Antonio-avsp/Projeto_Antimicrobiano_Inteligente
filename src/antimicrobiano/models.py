"""Entidades ORM (ver docs/modelo-de-dados.md)."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from antimicrobiano.database import Base
from antimicrobiano.enums import CategoriaAware


def agora_utc() -> datetime:
    """Data e hora atual em UTC (auditoria — RNF09)."""
    return datetime.now(UTC)


def _enum(tipo: type) -> SAEnum:
    """Enumeração persistida como texto (portável entre SGBDs)."""
    return SAEnum(tipo, native_enum=False, length=30)


class Auditavel:
    """Colunas de auditoria comuns às entidades."""

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=agora_utc, onupdate=agora_utc
    )


class Antimicrobiano(Auditavel, Base):
    """Item do catálogo de antimicrobianos do hospital (RF01, RF02)."""

    __tablename__ = "antimicrobianos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80))
    nome_normalizado: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    classe: Mapped[str] = mapped_column(String(80))
    categoria_aware: Mapped[CategoriaAware] = mapped_column(_enum(CategoriaAware))
    uso_restrito: Mapped[bool] = mapped_column(default=False)
    ativo: Mapped[bool] = mapped_column(default=True)
