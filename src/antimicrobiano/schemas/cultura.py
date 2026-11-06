"""Contratos de culturas e antibiogramas (RF06, RN10)."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from antimicrobiano.enums import Interpretacao, Material, StatusCultura
from antimicrobiano.schemas.antimicrobiano import AntimicrobianoResumo
from antimicrobiano.schemas.prescricao import CodigoPaciente, DataNaoFutura


class CulturaCriar(BaseModel):
    """Registro da coleta; a cultura nasce PENDENTE."""

    model_config = ConfigDict(str_strip_whitespace=True)

    paciente_codigo: CodigoPaciente
    setor: str = Field(min_length=2, max_length=60, examples=["UTI Adulto"])
    material: Material
    data_coleta: DataNaoFutura = Field(default_factory=date.today, description="Padrão: hoje.")


class ItemAntibiogramaEntrada(BaseModel):
    """Antimicrobiano testado e sua interpretação."""

    antimicrobiano_id: int = Field(gt=0)
    interpretacao: Interpretacao


class ResultadoCultura(BaseModel):
    """Resultado da cultura; um novo envio substitui integralmente o anterior."""

    model_config = ConfigDict(str_strip_whitespace=True)

    resultado: Literal[StatusCultura.POSITIVA, StatusCultura.NEGATIVA]
    microrganismo: str | None = Field(default=None, max_length=120, examples=["Escherichia coli"])
    data_resultado: DataNaoFutura = Field(default_factory=date.today, description="Padrão: hoje.")
    antibiograma: list[ItemAntibiogramaEntrada] = Field(default_factory=list)

    @field_validator("microrganismo")
    @classmethod
    def _normalizar_espacos(cls, valor: str | None) -> str | None:
        return " ".join(valor.split()) or None if valor else None

    @model_validator(mode="after")
    def _validar_consistencia(self):
        if self.resultado == StatusCultura.POSITIVA and not self.microrganismo:
            raise ValueError("Cultura positiva exige o microrganismo isolado.")
        if self.resultado == StatusCultura.NEGATIVA and (self.microrganismo or self.antibiograma):
            raise ValueError("Cultura negativa não possui microrganismo nem antibiograma.")
        ids = [item.antimicrobiano_id for item in self.antibiograma]
        if len(ids) != len(set(ids)):
            raise ValueError("Cada antimicrobiano pode aparecer apenas uma vez no antibiograma.")
        return self


class ItemAntibiogramaResposta(BaseModel):
    """Item do antibiograma com o antimicrobiano resumido."""

    model_config = ConfigDict(from_attributes=True)

    antimicrobiano: AntimicrobianoResumo
    interpretacao: Interpretacao


class CulturaResposta(BaseModel):
    """Cultura com resultado e antibiograma."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    paciente_codigo: str
    setor: str
    material: Material
    data_coleta: date
    status: StatusCultura
    microrganismo: str | None
    data_resultado: date | None
    antibiograma: list[ItemAntibiogramaResposta]
    criado_em: datetime
    atualizado_em: datetime
