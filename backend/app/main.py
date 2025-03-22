from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from app.api import auth, documents, dashboard
from app.core.database import init_db

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Legal Document Analyzer API",
    description="API for analyzing legal documents using AI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    app.mongodb = app.mongodb_client[os.getenv("MONGODB_DB", "legal_analyzer")]
    await init_db()

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Legal Document Analyzer API",
        "status": "active",
        "version": "1.0.0"
    }

# Import and include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["users"]) 