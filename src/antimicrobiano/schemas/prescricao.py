"""Contratos de prescrições (RF03, RF04)."""

from datetime import date, datetime
from typing import Annotated, ClassVar

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, computed_field, field_validator

from antimicrobiano.enums import Indicacao, StatusPrescricao, Via
from antimicrobiano.schemas.antimicrobiano import AntimicrobianoResumo
from antimicrobiano.schemas.comum import AtualizacaoParcial

PADRAO_CODIGO_PACIENTE = r"^PAC-\d{4,10}$"


def _nao_futura(valor: date) -> date:
    if valor > date.today():
        raise ValueError("A data não pode ser posterior à data atual.")
    return valor


CodigoPaciente = Annotated[
    str,
    Field(
        pattern=PADRAO_CODIGO_PACIENTE,
        examples=["PAC-0001"],
        description="Código pseudonimizado: PAC- seguido de 4 a 10 dígitos (RN04, LGPD).",
    ),
]
DataNaoFutura = Annotated[date, AfterValidator(_nao_futura)]


def _vazio_para_nulo(valor: str | None) -> str | None:
    return valor or None


class PrescricaoCriar(BaseModel):
    """Dados para registrar uma prescrição."""

    model_config = ConfigDict(str_strip_whitespace=True)

    paciente_codigo: CodigoPaciente
    setor: str = Field(min_length=2, max_length=60, examples=["UTI Adulto"])
    antimicrobiano_id: int = Field(gt=0, examples=[1])
    dose: str = Field(min_length=1, max_length=40, examples=["1 g"])
    intervalo_horas: int = Field(ge=1, le=168, examples=[8])
    via: Via
    indicacao: Indicacao
    diagnostico: str = Field(min_length=3, max_length=120, examples=["Pneumonia comunitária"])
    data_inicio: DataNaoFutura
    duracao_prevista_dias: int = Field(ge=1, le=90, examples=[7])
    justificativa: str | None = Field(
        default=None, max_length=500, description="Obrigatória para uso restrito (RN07)."
    )

    _justificativa = field_validator("justificativa")(_vazio_para_nulo)


class PrescricaoAtualizar(AtualizacaoParcial):
    """Campos alteráveis de uma prescrição ativa; informe apenas o que mudou."""

    CAMPOS_ANULAVEIS: ClassVar[frozenset[str]] = frozenset({"justificativa"})

    setor: str | None = Field(default=None, min_length=2, max_length=60)
    dose: str | None = Field(default=None, min_length=1, max_length=40)
    intervalo_horas: int | None = Field(default=None, ge=1, le=168)
    via: Via | None = None
    duracao_prevista_dias: int | None = Field(default=None, ge=1, le=90)
    justificativa: str | None = Field(default=None, max_length=500)

    _justificativa = field_validator("justificativa")(_vazio_para_nulo)


class PrescricaoResposta(BaseModel):
    """Prescrição com o antimicrobiano e o dia de terapia atual."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    paciente_codigo: str
    setor: str
    antimicrobiano: AntimicrobianoResumo
    dose: str
    intervalo_horas: int
    via: Via
    indicacao: Indicacao
    diagnostico: str
    data_inicio: date
    duracao_prevista_dias: int
    justificativa: str | None
    status: StatusPrescricao
    data_fim: date | None
    motivo_encerramento: str | None
    criado_em: datetime
    atualizado_em: datetime

    @computed_field
    @property
    def dia_de_terapia(self) -> int:
        """Dia de terapia hoje (ou no término); o dia de início é o dia 1."""
        referencia = self.data_fim or date.today()
        return (referencia - self.data_inicio).days + 1
