from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=10000)
db = client[settings.mongodb_db]

async def healthcheck():
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False
