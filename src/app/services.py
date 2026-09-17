import json
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Licitacao
from app.pncp_client import PNCPClient


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _first(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if data.get(key) is not None:
            return data[key]
    return None


def _as_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"true", "1", "sim", "s"}


def _mpe_signal(raw: dict[str, Any]) -> tuple[bool | None, bool | None]:
    text = json.dumps(raw, ensure_ascii=False).lower()
    exclusive = any(term in text for term in ("exclusivo para me", "exclusiva para me", "exclusivo para microempresa"))
    participates = _first(raw, "amplaParticipacao", "participacaoMpe", "beneficioMeEpp")
    return _as_bool(participates) if participates is not None else None, exclusive or (True if participates is True else False if participates is False else None)


async def sincronizar_pagina(session: AsyncSession, client: PNCPClient, *, pagina: int = 1, termo: str | None = None) -> int:
    payload = await client.buscar_contratacoes(pagina=pagina, termo=termo)
    records = payload.get("data", payload.get("content", []))
    if isinstance(records, dict):
        records = [records]
    saved = 0
    for raw in records:
        if not isinstance(raw, dict):
            continue
        identifier = _first(raw, "numeroControlePNCP", "numeroControle", "id")
        if not identifier:
            continue
        current = (await session.execute(select(Licitacao).where(Licitacao.numero_controle_pncp == str(identifier)))).scalar_one_or_none()
        participa_mpe, exclusiva_mpe = _mpe_signal(raw)
        values = {
            "numero_controle_pncp": str(identifier),
            "objeto": str(_first(raw, "objetoCompra", "objeto", "descricao") or "Sem objeto informado"),
            "modalidade": _first(raw, "modalidadeNome", "modalidade"),
            "situacao": _first(raw, "situacaoCompraNome", "situacao"),
            "data_publicacao": _parse_date(_first(raw, "dataPublicacaoPncp", "dataPublicacao")),
            "data_abertura": _parse_date(_first(raw, "dataAberturaProposta", "dataAbertura")),
            "valor_total": str(_first(raw, "valorTotalEstimado", "valorTotal") or "") or None,
            "participa_mpe": participa_mpe,
            "exclusiva_mpe": exclusiva_mpe,
            "orgao_cnpj": _first(raw, "orgaoEntidadeCnpj", "cnpjOrgao"),
            "orgao_nome": _first(raw, "orgaoEntidadeRazaoSocial", "razaoSocialOrgao", "orgaoNome"),
            "uf": _first(raw, "unidadeOrgaoUf", "uf"),
            "municipio": _first(raw, "unidadeOrgaoMunicipioNome", "municipio"),
            "url_origem": _first(raw, "linkSistemaOrigem", "urlOrigem"),
            "dados_brutos": json.dumps(raw, ensure_ascii=False),
        }
        if current:
            for key, value in values.items():
                setattr(current, key, value)
        else:
            session.add(Licitacao(**values))
        saved += 1
    await session.commit()
    return saved
