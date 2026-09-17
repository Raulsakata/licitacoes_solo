from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Licitacao


def _filtros_licitacoes(*, termo: str | None, uf: str | None, municipio: str | None, abertas: bool):
    filters = []
    if termo:
        like = f"%{termo}%"
        filters.append(or_(Licitacao.objeto.ilike(like), Licitacao.orgao_nome.ilike(like), Licitacao.municipio.ilike(like)))
    if uf:
        filters.append(Licitacao.uf == uf.upper())
    if municipio:
        filters.append(Licitacao.municipio.ilike(f"%{municipio}%"))
    if abertas:
        status_aberto = or_(Licitacao.situacao.ilike("%abert%"), Licitacao.situacao.ilike("%receb%"), Licitacao.situacao.ilike("%disputa%"))
        filters.append(or_(Licitacao.data_abertura >= date.today(), status_aberto))
    return filters


async def listar_licitacoes(
    session: AsyncSession, *, page: int = 1, page_size: int = 20, termo: str | None = None,
    uf: str | None = None, municipio: str | None = None, abertas: bool = True,
) -> tuple[list[Licitacao], int]:
    filters = _filtros_licitacoes(termo=termo, uf=uf, municipio=municipio, abertas=abertas)
    count_query = select(func.count()).select_from(Licitacao).where(*filters)
    total = int((await session.execute(count_query)).scalar_one())
    query = select(Licitacao).where(*filters).order_by(Licitacao.data_publicacao.desc().nullslast(), Licitacao.id.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list((await session.execute(query)).scalars().all())
    return items, total


async def resumo_dashboard(session: AsyncSession, *, uf: str | None = None, municipio: str | None = None) -> dict:
    filters = _filtros_licitacoes(termo=None, uf=uf, municipio=municipio, abertas=True)
    total = int((await session.execute(select(func.count()).select_from(Licitacao).where(*filters))).scalar_one())
    exclusivas = int((await session.execute(select(func.count()).select_from(Licitacao).where(*filters, Licitacao.exclusiva_mpe.is_(True)))).scalar_one())
    por_municipio = await session.execute(select(Licitacao.municipio, func.count().label("total")).where(*filters).group_by(Licitacao.municipio).order_by(func.count().desc()).limit(20))
    por_modalidade = await session.execute(select(Licitacao.modalidade, func.count().label("total")).where(*filters).group_by(Licitacao.modalidade).order_by(func.count().desc()).limit(20))
    return {
        "total_abertas": total,
        "total_exclusivas_mpe": exclusivas,
        "por_municipio": [{"municipio": row[0] or "Não informado", "total": row[1]} for row in por_municipio],
        "por_modalidade": [{"modalidade": row[0] or "Não informado", "total": row[1]} for row in por_modalidade],
    }
