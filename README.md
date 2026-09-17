# Monitor de Licitacoes PNCP

Plataforma web em FastAPI para importar, armazenar e pesquisar contratacoes publicas do Portal Nacional de Contratacoes Publicas (PNCP).

## Requisitos

- Python 3.11+
- PostgreSQL em producao (Render) ou SQLite local
- Acesso de rede ao PNCP para sincronizacao

## Rodando localmente

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
uvicorn app.main:app --app-dir src --reload
```

Abra `http://localhost:8000`. A documentacao OpenAPI fica em `http://localhost:8000/docs`.

O endpoint `GET /health` testa a conexão real com o banco e retorna `database: ok`. No Render, a URL PostgreSQL recebida pelo serviço é normalizada automaticamente para o driver assíncrono `asyncpg`.

## Dados para o frontend

- `GET /api/licitacoes?uf=SP&municipio=Campinas&abertas=true`: tabela paginada de oportunidades abertas por município.
- `GET /api/dashboard?uf=SP&municipio=Campinas`: cards e séries agregadas por município e modalidade para gráficos.
- `GET /api/licitacoes/{id}/triagem-mpe`: classificação informativa `prioridade_alta`, `beneficio_mpe` ou `validacao_manual`.
- `GET /api/empresas/{cnpj}`: consulta dados cadastrais públicos pela BrasilAPI, incluindo porte, situação, município, UF e opção pelo Simples/MEI.
- `GET /api/licitacoes/{id}/avaliar-empresa/{cnpj}`: cruza o porte e a situação cadastral do CNPJ com o benefício MPE do edital.

O indicador MPE é uma triagem baseada nos campos disponíveis no PNCP. A aptidão definitiva exige conferir o edital, CNAE, certidões, regularidade fiscal e demais requisitos legais.

Para importar uma pagina do PNCP:

```powershell
$env:PYTHONPATH = "src"
python scripts/sync_pncp.py
```

## PostgreSQL local

```powershell
docker compose up --build
```

## Testes

```powershell
pytest
ruff check .
```

## Deploy no Render

O arquivo `render.yaml` cria o servico web, um cron de sincronizacao a cada seis horas e o PostgreSQL. No painel do Render, conecte o repositorio e aplique o Blueprint. O Render injeta `DATABASE_URL`; localmente, mantenha `DATABASE_URL` em `.env`.

## Estrutura

- `src/app/main.py`: aplicacao FastAPI e lifespan
- `src/app/api.py`: endpoints JSON
- `src/app/web.py`: dashboard HTML
- `src/app/pncp_client.py`: cliente HTTP do PNCP
- `src/app/services.py`: normalizacao e sincronizacao idempotente
- `src/app/models.py`: tabelas SQLAlchemy
- `migrations/`: base para evolucao do schema com Alembic
- `scripts/sync_pncp.py`: entrada do cron/manual
