import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

# Fallback to sqlite if postgres is not provided
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./backend/app/data/nyaya_vaani.db")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    # SQLite requires connect_args for threads, Postgres ignores it if passed correctly, but we only pass it for sqlite
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        # Create all tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
