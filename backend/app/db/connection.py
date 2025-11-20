from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_size=5, 
    max_overflow=5, 
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_timeout=30,  # Timeout waiting for connection from pool
    echo_pool=False,  # Disable pool logging unless debugging
    connect_args={
        "statement_cache_size": 0,
        "server_settings": {
            "jit": "off",  # Disable JIT for faster simple queries
            "statement_timeout": "10000",  # 10s query timeout
        },
        "command_timeout": 10,  # Connection command timeout
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

