"""Schemas compartilhados entre os recursos."""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

AVISO_APOIO_A_DECISAO = (
    "Ferramenta de apoio à decisão para fins acadêmicos: não substitui o julgamento clínico. "
    "Utilize apenas dados fictícios."
)


class CampoComErro(BaseModel):
    """Campo rejeitado na validação da requisição."""

    campo: str = Field(examples=["categoria_aware"])
    local: str = Field(examples=["body"], description="body, query, path ou header.")
    mensagem: str = Field(
        examples=["Valor inválido; use um destes: 'ACCESS', 'WATCH' ou 'RESERVE'."]
    )


class Erro(BaseModel):
    """Formato único das respostas de erro da API."""

    codigo: str = Field(examples=["RECURSO_NAO_ENCONTRADO"])
    mensagem: str = Field(examples=["Antimicrobiano 999 não encontrado."])
    campos: list[CampoComErro] = []
    id_requisicao: str | None = Field(
        default=None, description="Mesmo valor do cabeçalho X-Request-ID e do log da requisição."
    )


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


RESPOSTA_404 = {404: {"model": Erro, "description": "Recurso não encontrado"}}
RESPOSTA_409 = {409: {"model": Erro, "description": "Conflito de unicidade ou de estado"}}
RESPOSTA_422 = {422: {"model": Erro, "description": "Dados inválidos ou regra de negócio violada"}}
