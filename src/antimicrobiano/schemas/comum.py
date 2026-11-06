"""Schemas compartilhados entre os recursos."""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, model_validator

AVISO_APOIO_A_DECISAO = (
    "Ferramenta de apoio à decisão para fins acadêmicos: não substitui o julgamento clínico. "
    "Utilize apenas dados fictícios."
)


class MensagemErro(BaseModel):
    """Erro de negócio (404, 409 ou 422)."""

    detail: str


class AtualizacaoParcial(BaseModel):
    """Base para PATCH: campos omitidos não mudam; ``null`` só é aceito em campos anuláveis."""

    model_config = ConfigDict(str_strip_whitespace=True)

    CAMPOS_ANULAVEIS: ClassVar[frozenset[str]] = frozenset()

    @model_validator(mode="after")
    def _rejeitar_nulos(self):
        for campo in self.model_fields_set:
            if getattr(self, campo) is None and campo not in self.CAMPOS_ANULAVEIS:
                raise ValueError(f"O campo '{campo}' não pode ser nulo.")
        return self


RESPOSTA_404 = {404: {"model": MensagemErro, "description": "Recurso não encontrado"}}
RESPOSTA_409 = {409: {"model": MensagemErro, "description": "Conflito de unicidade ou de estado"}}
RESPOSTA_422_NEGOCIO = {
    422: {"description": "Dados inválidos ou regra de negócio violada"},
}
