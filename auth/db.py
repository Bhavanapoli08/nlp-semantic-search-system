import os

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        uri = os.environ.get("MONGO_URI", "mongodb://mongo:27017")
        _client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    db_name = os.environ.get("MONGO_DB", "research_search")
    return get_client()[db_name]


def users_col() -> AsyncIOMotorCollection:
    return get_db()["users"]


def papers_col() -> AsyncIOMotorCollection:
    return get_db()["papers"]


def saved_col() -> AsyncIOMotorCollection:
    return get_db()["saved_papers"]


async def ensure_indexes() -> None:
    await users_col().create_index("email", unique=True)
    await papers_col().create_index([("owner_id", 1), ("created_at", -1)])
    await papers_col().create_index(
        [("title", "text"), ("authors", "text"), ("summary", "text"), ("abstract", "text")]
    )
    await saved_col().create_index([("owner_id", 1), ("created_at", -1)])
    await saved_col().create_index([("owner_id", 1), ("paper_id", 1)], unique=True)
