"""Contratos do painel de alertas (RF07 a RF13)."""

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict

from antimicrobiano.enums import Severidade, TipoAlerta


class AlertaResposta(BaseModel):
    """Alerta explicável gerado pelo motor de regras (RNF10)."""

    model_config = ConfigDict(from_attributes=True)

    tipo: TipoAlerta
    severidade: Severidade
    prescricao_id: int
    paciente_codigo: str
    setor: str
    antimicrobiano: str
    mensagem: str
    recomendacao: str
    evidencias: dict[str, Any]


class ResumoAlertas(BaseModel):
    """Quantidade de alertas por severidade e por tipo (inclui zeros)."""

    por_severidade: dict[Severidade, int]
    por_tipo: dict[TipoAlerta, int]


class PainelAlertas(BaseModel):
    """Alertas da data de referência, filtrados e ordenados por severidade (RN21)."""

    data_referencia: date
    aviso: str
    total: int
    resumo: ResumoAlertas
    alertas: list[AlertaResposta]
