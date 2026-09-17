import re
from typing import Any

import httpx


class CompanyClient:
    """Consulta cadastral pública; não substitui validação documental da empresa."""

    async def buscar_cnpj(self, cnpj: str) -> dict[str, Any]:
        normalized = re.sub(r"\D", "", cnpj)
        if len(normalized) != 14:
            raise ValueError("CNPJ deve conter 14 dígitos")
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"https://brasilapi.com.br/api/cnpj/v1/{normalized}")
            response.raise_for_status()
            return response.json()