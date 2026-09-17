from fastapi import APIRouter, Depends, HTTPException, Query
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.repositories import listar_licitacoes, resumo_dashboard
from app.models import Licitacao
from app.schemas import DashboardSummary, LicitacaoList
from sqlalchemy import select

router = APIRouter(prefix="/api", tags=["licitacoes"])


@router.get("/licitacoes", response_model=LicitacaoList)
async def get_licitacoes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    termo: str | None = Query(None, max_length=120),
    uf: str | None = Query(None, min_length=2, max_length=2),
    municipio: str | None = Query(None, max_length=150),
    abertas: bool = Query(True),
    session: AsyncSession = Depends(get_session),
) -> LicitacaoList:
    items, total = await listar_licitacoes(session, page=page, page_size=page_size, termo=termo, uf=uf, municipio=municipio, abertas=abertas)
    return LicitacaoList(items=items, total=total, page=page, page_size=page_size)


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard(uf: str | None = None, municipio: str | None = None, session: AsyncSession = Depends(get_session)):
    return await resumo_dashboard(session, uf=uf, municipio=municipio)


@router.get("/licitacoes/{licitacao_id}/triagem-mpe")
async def triagem_mpe(licitacao_id: int, session: AsyncSession = Depends(get_session)):
    licitacao = (await session.execute(select(Licitacao).where(Licitacao.id == licitacao_id))).scalar_one_or_none()
    if licitacao is None:
        raise HTTPException(status_code=404, detail="Licitação não encontrada")
    if licitacao.exclusiva_mpe is True:
        classificacao = "prioridade_alta"
        motivo = "O registro indica participação exclusiva de MPE."
    elif licitacao.participa_mpe is True:
        classificacao = "beneficio_mpe"
        motivo = "O registro indica benefício ou participação de MPE."
    else:
        classificacao = "validacao_manual"
        motivo = "O PNCP não trouxe sinal suficiente para confirmar o benefício."
    return {"licitacao_id": licitacao.id, "municipio": licitacao.municipio, "classificacao": classificacao, "motivo": motivo, "aviso": "Triagem informativa; confirme edital, certidões e requisitos antes de participar."}


@router.get("/empresas/{cnpj}")
async def get_empresa(cnpj: str):
    from app.company_client import CompanyClient

    try:
        return await CompanyClient().buscar_cnpj(cnpj)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="Não foi possível consultar o serviço cadastral") from error


@router.get("/licitacoes/{licitacao_id}/avaliar-empresa/{cnpj}")
async def avaliar_empresa(licitacao_id: int, cnpj: str, session: AsyncSession = Depends(get_session)):
    licitacao = (await session.execute(select(Licitacao).where(Licitacao.id == licitacao_id))).scalar_one_or_none()
    if licitacao is None:
        raise HTTPException(status_code=404, detail="Licitação não encontrada")
    from app.company_client import CompanyClient

    try:
        empresa = await CompanyClient().buscar_cnpj(cnpj)
    except (ValueError, httpx.HTTPError) as error:
        raise HTTPException(status_code=400, detail="Não foi possível consultar o CNPJ informado") from error

    porte = str(empresa.get("porte") or "").lower()
    situacao = str(empresa.get("descricao_situacao_cadastral") or empresa.get("situacao") or "").lower()
    eh_mpe = any(term in porte for term in ("micro", "pequeno", "mei", "epp"))
    ativa = "ativa" in situacao
    beneficio_mpe = licitacao.exclusiva_mpe is True or licitacao.participa_mpe is True
    if not ativa or not eh_mpe:
        classificacao = "nao_elegivel"
    elif beneficio_mpe:
        classificacao = "apta_na_triagem"
    else:
        classificacao = "revisar"
    return {
        "licitacao_id": licitacao.id,
        "numero_controle_pncp": licitacao.numero_controle_pncp,
        "cnpj": "".join(character for character in cnpj if character.isdigit()),
        "empresa": {"razao_social": empresa.get("razao_social"), "porte": empresa.get("porte"), "situacao": empresa.get("descricao_situacao_cadastral")},
        "classificacao": classificacao,
        "motivos": {"empresa_ativa": ativa, "porte_mpe": eh_mpe, "beneficio_mpe_no_edital": beneficio_mpe},
        "aviso": "Resultado preliminar. Confirme CNAE, edital, certidões, regularidade fiscal e demais requisitos.",
    }
