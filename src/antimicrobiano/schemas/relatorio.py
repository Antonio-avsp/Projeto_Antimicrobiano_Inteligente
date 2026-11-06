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
