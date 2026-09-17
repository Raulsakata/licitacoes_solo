import asyncio

from app.config import get_settings
from app.db import SessionLocal
from app.pncp_client import PNCPClient
from app.services import sincronizar_pagina


async def main() -> None:
    settings = get_settings()
    async with SessionLocal() as session:
        total = await sincronizar_pagina(session, PNCPClient(settings))
    print(f"{total} registros sincronizados")


if __name__ == "__main__":
    asyncio.run(main())
