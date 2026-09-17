from datetime import date

from pydantic import BaseModel, ConfigDict


class LicitacaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_controle_pncp: str
    objeto: str
    modalidade: str | None = None
    situacao: str | None = None
    data_publicacao: date | None = None
    data_abertura: date | None = None
    valor_total: str | None = None
    participa_mpe: bool | None = None
    exclusiva_mpe: bool | None = None
    orgao_nome: str | None = None
    uf: str | None = None
    municipio: str | None = None
    url_origem: str | None = None


class LicitacaoList(BaseModel):
    items: list[LicitacaoRead]
    total: int
    page: int
    page_size: int


class DashboardSummary(BaseModel):
    total_abertas: int
    total_exclusivas_mpe: int
    por_municipio: list[dict]
    por_modalidade: list[dict]
