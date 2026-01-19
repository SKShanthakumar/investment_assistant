from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

# Global MongoDB client
mongo_client: AsyncIOMotorClient = None
mongo_db: AsyncIOMotorDatabase = None


def get_mongo_client() -> AsyncIOMotorClient:
    global mongo_client
    if mongo_client is None:
        mongo_client = AsyncIOMotorClient(settings.mongodb_uri)
    return mongo_client


def get_mongo_db() -> AsyncIOMotorDatabase:
    global mongo_db
    if mongo_db is None:
        client = get_mongo_client()
        mongo_db = client[settings.MONGODB_DB_NAME]
    return mongo_db


async def close_mongo_connection():
    global mongo_client, mongo_db
    if mongo_client:
        mongo_client.close()
        mongo_client = None
        mongo_db = None
