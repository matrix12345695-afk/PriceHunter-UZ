import asyncio
import asyncpg

from app.core.settings import settings


async def main():
    print("Connecting...")
    print(settings.DATABASE_URL)

    conn = await asyncpg.connect(
        settings.DATABASE_URL.replace("+asyncpg", ""),
        ssl="require",
    )

    print("✅ CONNECTED!")

    version = await conn.fetchval("SELECT version();")
    print(version)

    await conn.close()


asyncio.run(main())