"""
Worker-specific database connection configuration.

Workers use Transaction Mode (port 6543) for higher connection limits,
while the API uses Session Mode (port 5432) for prepared statements.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings


# Worker engine configured for Transaction Mode (pgbouncer)
# - Uses WORKER_DATABASE_URL (port 6543)
# - Disables prepared statements (statement_cache_size=0)
# - Smaller pool size (workers are I/O bound, not connection bound)
worker_engine = create_async_engine(
    settings.worker_db_url,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "server_settings": {"jit": "off"},
        "statement_cache_size": 0,  # Required for transaction mode
    },
)

WorkerAsyncSessionLocal = sessionmaker(
    worker_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

