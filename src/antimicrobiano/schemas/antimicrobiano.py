"""Contratos do catálogo de antimicrobianos (RF01, RF02)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from antimicrobiano.enums import CategoriaAware
from antimicrobiano.schemas.comum import AtualizacaoParcial


class AntimicrobianoCriar(BaseModel):
    """Dados para cadastrar um antimicrobiano."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(min_length=2, max_length=80, examples=["Ceftriaxona"])
    classe: str = Field(min_length=2, max_length=80, examples=["Cefalosporina de 3ª geração"])
    categoria_aware: CategoriaAware = Field(examples=["WATCH"])
    uso_restrito: bool = Field(default=False, description="Exige justificativa (RN07).")


class AntimicrobianoAtualizar(AtualizacaoParcial):
    """Campos alteráveis; informe apenas o que mudou."""

    nome: str | None = Field(default=None, min_length=2, max_length=80)
    classe: str | None = Field(default=None, min_length=2, max_length=80)
    categoria_aware: CategoriaAware | None = None
    uso_restrito: bool | None = None
    ativo: bool | None = Field(default=None, description="Use `true` para reativar um item.")


class AntimicrobianoResumo(BaseModel):
    """Representação resumida, usada dentro de outros recursos."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    classe: str
    categoria_aware: CategoriaAware
    uso_restrito: bool


class AntimicrobianoResposta(AntimicrobianoResumo):
    """Antimicrobiano completo."""

    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
