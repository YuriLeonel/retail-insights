from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from app.models import Base
from typing import AsyncGenerator

load_dotenv()

# Validate required environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "5432")

# Check for required environment variables
if not DB_USER:
    raise ValueError("DB_USER environment variable is required")
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable is required")
if not DB_NAME:
    raise ValueError("DB_NAME environment variable is required")

# Async database URL
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Sync database URL for migrations
SYNC_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    future=True,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Sync engine for migrations (keeping for backward compatibility)
sync_engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Async dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_async_db_dependency() -> AsyncGenerator[AsyncSession, None]:
    """Async database dependency for FastAPI routes"""
    async for session in get_async_db():
        yield session

def get_db():
    """Sync dependency to get database session (for backward compatibility)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_async_db() -> None:
    """Initialize async database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def init_db() -> None:
    """Initialize sync database tables (for backward compatibility)"""
    Base.metadata.create_all(bind=sync_engine)
