from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.repositories import listar_licitacoes, resumo_dashboard

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="src/app/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, termo: str | None = None, uf: str | None = None, municipio: str | None = None, session: AsyncSession = Depends(get_session)):
    items, total = await listar_licitacoes(session, termo=termo, uf=uf, municipio=municipio, abertas=True)
    summary = await resumo_dashboard(session, uf=uf, municipio=municipio)
    return templates.TemplateResponse("dashboard.html", {"request": request, "items": items, "total": total, "summary": summary, "termo": termo or "", "uf": uf or "", "municipio": municipio or ""})
