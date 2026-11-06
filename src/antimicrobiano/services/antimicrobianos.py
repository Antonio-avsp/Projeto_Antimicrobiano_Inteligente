"""Casos de uso do catálogo de antimicrobianos (UC01 — RF01, RF02, RN01–RN03)."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from antimicrobiano.enums import CategoriaAware
from antimicrobiano.erros import ConflitoDeEstado, RecursoNaoEncontrado
from antimicrobiano.models import Antimicrobiano
from antimicrobiano.schemas.antimicrobiano import AntimicrobianoAtualizar, AntimicrobianoCriar
from antimicrobiano.texto import normalizar

MENSAGEM_NOME_DUPLICADO = "Já existe um antimicrobiano com este nome."


def _garantir_nome_disponivel(sessao: Session, nome: str, ignorar_id: int | None = None) -> None:
    """RN01: o nome é único sem diferenciar maiúsculas, acentos e espaços extras."""
    existente = sessao.scalar(
        select(Antimicrobiano).where(Antimicrobiano.nome_normalizado == normalizar(nome))
    )
    if existente is not None and existente.id != ignorar_id:
        raise ConflitoDeEstado(MENSAGEM_NOME_DUPLICADO)


def _salvar(sessao: Session, antimicrobiano: Antimicrobiano) -> Antimicrobiano:
    sessao.add(antimicrobiano)
    try:
        sessao.commit()
    except IntegrityError as erro:  # concorrência: a restrição única é a garantia final
        sessao.rollback()
        raise ConflitoDeEstado(MENSAGEM_NOME_DUPLICADO) from erro
    sessao.refresh(antimicrobiano)
    return antimicrobiano


def criar(sessao: Session, dados: AntimicrobianoCriar) -> Antimicrobiano:
    """Cadastra um antimicrobiano ativo (RF01)."""
    _garantir_nome_disponivel(sessao, dados.nome)
    antimicrobiano = Antimicrobiano(**dados.model_dump(), nome_normalizado=normalizar(dados.nome))
    return _salvar(sessao, antimicrobiano)


def listar(
    sessao: Session,
    categoria_aware: CategoriaAware | None = None,
    uso_restrito: bool | None = None,
    ativo: bool | None = True,
    busca: str | None = None,
) -> list[Antimicrobiano]:
    """Lista o catálogo ordenado por nome, com filtros opcionais (RF02)."""
    consulta = select(Antimicrobiano).order_by(Antimicrobiano.nome_normalizado)
    if categoria_aware is not None:
        consulta = consulta.where(Antimicrobiano.categoria_aware == categoria_aware)
    if uso_restrito is not None:
        consulta = consulta.where(Antimicrobiano.uso_restrito == uso_restrito)
    if ativo is not None:
        consulta = consulta.where(Antimicrobiano.ativo == ativo)
    if busca:
        consulta = consulta.where(Antimicrobiano.nome_normalizado.contains(normalizar(busca)))
    return list(sessao.scalars(consulta))


def obter(sessao: Session, antimicrobiano_id: int) -> Antimicrobiano:
    """Retorna o antimicrobiano, ativo ou inativo, ou lança 404."""
    antimicrobiano = sessao.get(Antimicrobiano, antimicrobiano_id)
    if antimicrobiano is None:
        raise RecursoNaoEncontrado(f"Antimicrobiano {antimicrobiano_id} não encontrado.")
    return antimicrobiano


def atualizar(
    sessao: Session, antimicrobiano_id: int, dados: AntimicrobianoAtualizar
) -> Antimicrobiano:
    """Atualiza apenas os campos informados (RF02)."""
    antimicrobiano = obter(sessao, antimicrobiano_id)
    alteracoes = dados.model_dump(exclude_unset=True)
    if "nome" in alteracoes:
        _garantir_nome_disponivel(sessao, alteracoes["nome"], ignorar_id=antimicrobiano.id)
        antimicrobiano.nome_normalizado = normalizar(alteracoes["nome"])
    for campo, valor in alteracoes.items():
        setattr(antimicrobiano, campo, valor)
    return _salvar(sessao, antimicrobiano)


def inativar(sessao: Session, antimicrobiano_id: int) -> None:
    """Exclusão lógica: preserva o histórico de prescrições e antibiogramas (RN03)."""
    antimicrobiano = obter(sessao, antimicrobiano_id)
    antimicrobiano.ativo = False
    _salvar(sessao, antimicrobiano)
