from typing import Any

import httpx

from app.config import Settings


class PNCPClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def buscar_contratacoes(self, *, pagina: int = 1, tamanho: int | None = None, termo: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"pagina": pagina, "tamanhoPagina": tamanho or self.settings.sync_page_size}
        if termo:
            params["termo"] = termo
        async with httpx.AsyncClient(base_url=self.settings.pncp_base_url, timeout=self.settings.pncp_timeout_seconds) as client:
            response = await client.get("/v1/contratacoes/publicacao", params=params)
            response.raise_for_status()
            return response.json()
