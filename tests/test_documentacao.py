"""Sincronização documentação × código (regra em docs/README.md)."""

import re
from pathlib import Path

import pytest

from antimicrobiano import __version__
from antimicrobiano.enums import TipoAlerta

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"


def _ler(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "documento", sorted(p.name for p in DOCS.glob("*.md") if p.name != "README.md")
)
def test_todo_documento_esta_no_indice(documento):
    assert f"]({documento})" in _ler(DOCS / "README.md")


def test_indice_informa_versao_e_data_de_cada_documento():
    linhas = [
        linha
        for linha in _ler(DOCS / "README.md").splitlines()
        if re.match(r"\| \[[^]]+\]\([\w./-]+\.md\)", linha)
    ]
    assert linhas
    for linha in linhas:
        assert re.search(r"\| v\d+\.\d+\.\d+ \| \d{2}/\d{2}/\d{4} \|$", linha), linha


def test_todo_requisito_funcional_esta_na_matriz_de_rastreabilidade():
    requisitos = set(re.findall(r"\*\*\[(RF\d{2})\]\*\*", _ler(DOCS / "requisitos.md")))
    matriz = set(re.findall(r"^\| (RF\d{2}) \|", _ler(DOCS / "rastreabilidade.md"), re.M))

    assert requisitos
    assert requisitos == matriz


def test_requisitos_implementados_apontam_testes_existentes():
    for linha in _ler(DOCS / "rastreabilidade.md").splitlines():
        if linha.startswith("| RF") and linha.rstrip().endswith("✅ |"):
            for teste in re.findall(r"`(tests/[\w/]+\.py)`", linha):
                assert (RAIZ / teste).is_file(), f"{teste} citado na matriz não existe"


def test_todo_tipo_de_alerta_esta_documentado():
    requisitos = _ler(DOCS / "requisitos.md")
    readme = _ler(RAIZ / "README.md")

    for tipo in TipoAlerta:
        assert f"`{tipo.value}`" in requisitos
        assert f"`{tipo.value}`" in readme


def test_versao_do_pacote_registrada_no_changelog():
    assert f"## [{__version__}]" in _ler(RAIZ / "CHANGELOG.md")
