from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Monitor de Licitacoes"
    environment: str = "development"
    database_url: str = "sqlite+aiosqlite:///./licitacoes.db"
    pncp_base_url: str = "https://pncp.gov.br/api/consulta"
    pncp_timeout_seconds: int = 30
    sync_page_size: int = 50
    secret_key: str = "change-me"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
