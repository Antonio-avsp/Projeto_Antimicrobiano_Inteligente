"""Schemas dos endpoints de sistema."""

from pydantic import BaseModel


class Saude(BaseModel):
    """Resposta do endpoint de verificação de saúde."""

    status: str
    versao: str
    aviso: str
