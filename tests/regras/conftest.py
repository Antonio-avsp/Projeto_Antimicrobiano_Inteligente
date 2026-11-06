"""Fixtures das regras: expõem as fábricas de objetos de domínio em memória."""

import pytest

from tests.regras.fabricas import fabricar_prescricao


@pytest.fixture
def prescricao():
    return fabricar_prescricao
