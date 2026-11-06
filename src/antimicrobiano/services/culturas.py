"""Casos de uso de culturas e antibiogramas (UC04 — RF06, RN10)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from antimicrobiano.enums import StatusCultura
from antimicrobiano.erros import RecursoNaoEncontrado, RegraDeNegocioViolada
from antimicrobiano.models import Antimicrobiano, Cultura, ItemAntibiograma
from antimicrobiano.schemas.cultura import CulturaCriar, ResultadoCultura


def registrar_coleta(sessao: Session, dados: CulturaCriar) -> Cultura:
    """Registra a coleta; o resultado é informado depois (status PENDENTE)."""
    cultura = Cultura(**dados.model_dump())
    sessao.add(cultura)
    sessao.commit()
    sessao.refresh(cultura)
    return cultura


def listar(
    sessao: Session, paciente_codigo: str | None = None, status: StatusCultura | None = None
) -> list[Cultura]:
    """Lista culturas da coleta mais recente para a mais antiga."""
    consulta = select(Cultura).order_by(Cultura.data_coleta.desc(), Cultura.id.desc())
    if paciente_codigo:
        consulta = consulta.where(Cultura.paciente_codigo == paciente_codigo)
    if status is not None:
        consulta = consulta.where(Cultura.status == status)
    return list(sessao.scalars(consulta))


def obter(sessao: Session, cultura_id: int) -> Cultura:
    """Retorna a cultura ou lança 404."""
    cultura = sessao.get(Cultura, cultura_id)
    if cultura is None:
        raise RecursoNaoEncontrado(f"Cultura {cultura_id} não encontrada.")
    return cultura


def _garantir_antimicrobianos_existentes(sessao: Session, ids: list[int]) -> None:
    existentes = set(sessao.scalars(select(Antimicrobiano.id).where(Antimicrobiano.id.in_(ids))))
    faltantes = sorted(set(ids) - existentes)
    if faltantes:
        lista = ", ".join(str(item) for item in faltantes)
        raise RegraDeNegocioViolada(
            f"Antimicrobiano(s) do antibiograma não encontrado(s): {lista}."
        )


def registrar_resultado(sessao: Session, cultura_id: int, dados: ResultadoCultura) -> Cultura:
    """Registra (ou corrige) o resultado e o antibiograma da cultura (RN10)."""
    cultura = obter(sessao, cultura_id)
    if dados.data_resultado < cultura.data_coleta:
        raise RegraDeNegocioViolada(
            f"A data do resultado não pode ser anterior à coleta ({cultura.data_coleta:%d/%m/%Y})."
        )
    _garantir_antimicrobianos_existentes(
        sessao, [item.antimicrobiano_id for item in dados.antibiograma]
    )

    cultura.antibiograma.clear()
    sessao.flush()  # remove os itens antigos antes de inserir os novos (restrição única)
    cultura.status = StatusCultura(dados.resultado)
    cultura.microrganismo = dados.microrganismo
    cultura.data_resultado = dados.data_resultado
    cultura.antibiograma.extend(
        ItemAntibiograma(antimicrobiano_id=item.antimicrobiano_id, interpretacao=item.interpretacao)
        for item in dados.antibiograma
    )
    sessao.commit()
    sessao.refresh(cultura)
    return cultura
