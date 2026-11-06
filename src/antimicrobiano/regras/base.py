"""Contratos do motor de regras: alerta, contexto de avaliação e regra (padrão Strategy)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Any, ClassVar

from antimicrobiano.enums import Severidade, TipoAlerta
from antimicrobiano.models import Prescricao


@dataclass(frozen=True)
class Alerta:
    """Alerta explicável: o que foi detectado, por quê (evidências) e o que fazer (RNF10)."""

    tipo: TipoAlerta
    severidade: Severidade
    prescricao_id: int
    paciente_codigo: str
    setor: str
    antimicrobiano: str
    mensagem: str
    recomendacao: str
    evidencias: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ContextoAvaliacao:
    """Dados pré-carregados que as regras consultam, sem acessar o banco."""

    data_referencia: date


class Regra(ABC):
    """Uma regra clínica: recebe uma prescrição ativa e devolve zero ou mais alertas."""

    tipo: ClassVar[TipoAlerta]
    severidade: ClassVar[Severidade]

    @abstractmethod
    def avaliar(self, prescricao: Prescricao, contexto: ContextoAvaliacao) -> list[Alerta]:
        """Avalia a prescrição na data de referência do contexto."""

    def _alerta(
        self, prescricao: Prescricao, mensagem: str, recomendacao: str, **evidencias: Any
    ) -> Alerta:
        return Alerta(
            tipo=self.tipo,
            severidade=self.severidade,
            prescricao_id=prescricao.id,
            paciente_codigo=prescricao.paciente_codigo,
            setor=prescricao.setor,
            antimicrobiano=prescricao.antimicrobiano.nome,
            mensagem=mensagem,
            recomendacao=recomendacao,
            evidencias=evidencias,
        )
