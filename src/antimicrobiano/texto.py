"""Utilitários de texto."""

import re
import unicodedata


def normalizar(texto: str) -> str:
    """Normaliza um texto para comparação (RN01).

    Remove acentos, converte para minúsculas e elimina espaços extras:
    ``"  Ceftriaxôna "`` e ``"CEFTRIAXONA"`` resultam em ``"ceftriaxona"``.
    """
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acentos = "".join(c for c in decomposto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acentos).strip().casefold()
