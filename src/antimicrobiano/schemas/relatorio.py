"""Contratos dos relatórios (RF14)."""

from datetime import date

from pydantic import BaseModel

from antimicrobiano.enums import CategoriaAware


class SensibilidadeAntimicrobiano(BaseModel):
    """Sensibilidade de um microrganismo a um antimicrobiano no período."""

    antimicrobiano: str
    categoria_aware: CategoriaAware
    testados: int
    sensiveis: int
    sensiveis_aumentando_exposicao: int
    resistentes: int
    percentual_sensivel: float
    amostra_suficiente: bool


class PerfilMicrorganismo(BaseModel):
    """Perfil de sensibilidade de um microrganismo."""

    microrganismo: str
    isolados: int
    antimicrobianos: list[SensibilidadeAntimicrobiano]


class AntibiogramaCumulativo(BaseModel):
    """Antibiograma cumulativo institucional (RN19)."""

    inicio: date
    fim: date
    setor: str | None
    minimo_isolados: int
    total_isolados: int
    metodologia: str
    microrganismos: list[PerfilMicrorganismo]


class ConsumoPorCategoria(BaseModel):
    """DOT de uma categoria AWaRe no período."""

    categoria_aware: CategoriaAware
    dot: int
    percentual: float | None


class ConsumoPorAntimicrobiano(BaseModel):
    """DOT de um antimicrobiano no período."""

    antimicrobiano: str
    classe: str
    categoria_aware: CategoriaAware
    dot: int
    pacientes: int


class ConsumoPorSetor(BaseModel):
    """DOT de um setor (unidade) no período."""

    setor: str
    dot: int


class IndicadoresConsumo(BaseModel):
    """Indicadores de consumo em dias de terapia (RF15, RN23)."""

    inicio: date
    fim: date
    setor: str | None
    metodologia: str
    total_dot: int
    percentual_access: float | None
    meta_access_oms: float
    atinge_meta_access: bool | None
    por_categoria: list[ConsumoPorCategoria]
    por_antimicrobiano: list[ConsumoPorAntimicrobiano]
    por_setor: list[ConsumoPorSetor]
