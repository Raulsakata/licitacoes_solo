from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Orgao(Base):
    __tablename__ = "orgaos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Empresa(Base):
    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, index=True)
    razao_social: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nome_fantasia: Mapped[str | None] = mapped_column(String(255), nullable=True)
    porte: Mapped[str | None] = mapped_column(String(80), nullable=True)
    situacao_cadastral: Mapped[str | None] = mapped_column(String(80), nullable=True)
    municipio: Mapped[str | None] = mapped_column(String(150), nullable=True)
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True)
    simples_nacional: Mapped[bool | None] = mapped_column(nullable=True)
    mei: Mapped[bool | None] = mapped_column(nullable=True)
    dados_brutos: Mapped[str | None] = mapped_column(Text(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Licitacao(Base):
    __tablename__ = "licitacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero_controle_pncp: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    objeto: Mapped[str] = mapped_column(Text())
    modalidade: Mapped[str | None] = mapped_column(String(120), nullable=True)
    situacao: Mapped[str | None] = mapped_column(String(120), nullable=True)
    data_publicacao: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    data_abertura: Mapped[date | None] = mapped_column(Date, nullable=True)
    valor_total: Mapped[str | None] = mapped_column(String(40), nullable=True)
    participa_mpe: Mapped[bool | None] = mapped_column(nullable=True, index=True)
    exclusiva_mpe: Mapped[bool | None] = mapped_column(nullable=True, index=True)
    orgao_cnpj: Mapped[str | None] = mapped_column(String(14), nullable=True, index=True)
    orgao_nome: Mapped[str | None] = mapped_column(String(255), nullable=True)
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True, index=True)
    municipio: Mapped[str | None] = mapped_column(String(150), nullable=True)
    url_origem: Mapped[str | None] = mapped_column(String(500), nullable=True)
    dados_brutos: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
