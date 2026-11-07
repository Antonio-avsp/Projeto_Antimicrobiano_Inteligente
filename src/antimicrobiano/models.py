"""Entidades ORM (ver docs/modelo-de-dados.md)."""

from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from antimicrobiano.database import Base
from antimicrobiano.enums import (
    CategoriaAware,
    Conduta,
    Indicacao,
    Interpretacao,
    Material,
    Perfil,
    StatusCultura,
    StatusPrescricao,
    Via,
)


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


class Prescricao(Auditavel, Base):
    """Prescrição de antimicrobiano para um paciente pseudonimizado (RF03, RF04)."""

    __tablename__ = "prescricoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    paciente_codigo: Mapped[str] = mapped_column(String(15), index=True)
    setor: Mapped[str] = mapped_column(String(60))
    antimicrobiano_id: Mapped[int] = mapped_column(ForeignKey("antimicrobianos.id"))
    dose: Mapped[str] = mapped_column(String(40))
    intervalo_horas: Mapped[int]
    via: Mapped[Via] = mapped_column(_enum(Via))
    indicacao: Mapped[Indicacao] = mapped_column(_enum(Indicacao))
    diagnostico: Mapped[str] = mapped_column(String(120))
    data_inicio: Mapped[date]
    duracao_prevista_dias: Mapped[int]
    justificativa: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[StatusPrescricao] = mapped_column(
        _enum(StatusPrescricao), default=StatusPrescricao.ATIVA
    )
    data_fim: Mapped[date | None]
    motivo_encerramento: Mapped[str | None] = mapped_column(String(300))
    registrado_por: Mapped[str | None] = mapped_column(String(40))
    encerrado_por: Mapped[str | None] = mapped_column(String(40))

    antimicrobiano: Mapped[Antimicrobiano] = relationship(lazy="joined")
    reavaliacoes: Mapped[list[Reavaliacao]] = relationship(
        back_populates="prescricao",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="(Reavaliacao.data_reavaliacao, Reavaliacao.id)",
    )

    def dia_de_terapia(self, data_referencia: date) -> int:
        """Dia de terapia na data de referência; o dia de início é o dia 1 (RN11)."""
        referencia = min(data_referencia, self.data_fim) if self.data_fim else data_referencia
        return (referencia - self.data_inicio).days + 1


class Reavaliacao(Base):
    """Reavaliação estruturada (time-out) de uma prescrição (RF05)."""

    __tablename__ = "reavaliacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    prescricao_id: Mapped[int] = mapped_column(ForeignKey("prescricoes.id"), index=True)
    data_reavaliacao: Mapped[date]
    conduta: Mapped[Conduta] = mapped_column(_enum(Conduta))
    observacao: Mapped[str | None] = mapped_column(String(500))
    registrado_por: Mapped[str | None] = mapped_column(String(40))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)

    prescricao: Mapped[Prescricao] = relationship(back_populates="reavaliacoes")


class Cultura(Auditavel, Base):
    """Cultura microbiológica de um paciente pseudonimizado (RF06)."""

    __tablename__ = "culturas"

    id: Mapped[int] = mapped_column(primary_key=True)
    paciente_codigo: Mapped[str] = mapped_column(String(15), index=True)
    setor: Mapped[str] = mapped_column(String(60))
    material: Mapped[Material] = mapped_column(_enum(Material))
    data_coleta: Mapped[date]
    status: Mapped[StatusCultura] = mapped_column(
        _enum(StatusCultura), default=StatusCultura.PENDENTE
    )
    microrganismo: Mapped[str | None] = mapped_column(String(120))
    data_resultado: Mapped[date | None]

    antibiograma: Mapped[list[ItemAntibiograma]] = relationship(
        back_populates="cultura",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="ItemAntibiograma.id",
    )


class ItemAntibiograma(Base):
    """Interpretação de um antimicrobiano testado em uma cultura (RN10)."""

    __tablename__ = "itens_antibiograma"
    __table_args__ = (UniqueConstraint("cultura_id", "antimicrobiano_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cultura_id: Mapped[int] = mapped_column(ForeignKey("culturas.id", ondelete="CASCADE"))
    antimicrobiano_id: Mapped[int] = mapped_column(ForeignKey("antimicrobianos.id"))
    interpretacao: Mapped[Interpretacao] = mapped_column(_enum(Interpretacao))

    cultura: Mapped[Cultura] = relationship(back_populates="antibiograma")
    antimicrobiano: Mapped[Antimicrobiano] = relationship(lazy="joined")


class Usuario(Auditavel, Base):
    """Usuário da API com perfil de acesso (RF17)."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(120))
    perfil: Mapped[Perfil] = mapped_column(_enum(Perfil))
    senha_hash: Mapped[str] = mapped_column(String(255))
    ativo: Mapped[bool] = mapped_column(default=True)
