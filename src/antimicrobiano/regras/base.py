"""Contratos do motor de regras: alerta, contexto de avaliação e regra (padrão Strategy)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, ClassVar

from antimicrobiano.config import ParametrosClinicos
from antimicrobiano.enums import Severidade, TipoAlerta
from antimicrobiano.models import Cultura, Prescricao


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
    culturas_por_paciente: Mapping[str, Sequence[Cultura]] = field(default_factory=dict)
    parametros: ParametrosClinicos = field(default_factory=ParametrosClinicos)
    prescricoes_ativas_por_paciente: Mapping[str, Sequence[Prescricao]] = field(
        default_factory=dict
    )

    def culturas_relevantes(self, prescricao: Prescricao) -> list[Cultura]:
        """Culturas do paciente coletadas na janela de relevância da prescrição (RN11)."""
        inicio_janela = prescricao.data_inicio - timedelta(days=self.parametros.janela_cultura_dias)
        return [
            cultura
            for cultura in self.culturas_por_paciente.get(prescricao.paciente_codigo, ())
            if inicio_janela <= cultura.data_coleta <= self.data_referencia
        ]

    def outras_prescricoes_ativas(self, prescricao: Prescricao) -> list[Prescricao]:
        """Demais prescrições ativas do mesmo paciente iniciadas até a data de referência."""
        return [
            outra
            for outra in self.prescricoes_ativas_por_paciente.get(prescricao.paciente_codigo, ())
            if outra.id != prescricao.id and outra.data_inicio <= self.data_referencia
        ]


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
