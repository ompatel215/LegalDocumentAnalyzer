from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
from typing import Generator
import os

async def get_db() -> Generator:
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    try:
        yield client[os.getenv("MONGODB_DB", "legal_analyzer")]
    finally:
        client.close()

# Database indexes setup
async def setup_indexes(db: AsyncIOMotorClient):
    # Users collection indexes
    await db.users.create_index("email", unique=True)
    
    # Documents collection indexes
    await db.documents.create_index([("user_id", 1), ("upload_date", -1)])
    await db.documents.create_index("analysis_status")
    
    # Create text index for document content
    await db.documents.create_index([
        ("title", "text"),
        ("content", "text")
    ])

# Initialize database
async def init_db():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    db = client[os.getenv("MONGODB_DB", "legal_analyzer")]
    
    # Create collections if they don't exist
    if "users" not in await db.list_collection_names():
        await db.create_collection("users")
    
    if "documents" not in await db.list_collection_names():
        await db.create_collection("documents")
    
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.documents.create_index([("user_id", 1), ("upload_date", -1)])
    
    print("Database initialized successfully") 