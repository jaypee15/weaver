
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.config import settings


# def _assert_worker_uses_transaction_mode() -> None:
#     url = settings.worker_db_url
#     if ":6543/" not in url:
#         raise RuntimeError(f"Worker DB URL is not using Transaction Mode port 6543: {url}")


# _assert_worker_uses_transaction_mode()
# worker_db_url = settings.worker_db_url
worker_db_url = settings.DATABASE_URL


# Worker engine configured for Transaction Mode (pgbouncer)
worker_engine = create_async_engine(
    worker_db_url,
    echo=False,
    poolclass=NullPool,  # No connection pooling - create fresh connections per task
    execution_options={
        "compiled_cache": None,  # Disable SQLAlchemy's compiled statement cache
    },
    connect_args={
        "server_settings": {
            "jit": "off",
        },
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    },
)

WorkerAsyncSessionLocal = sessionmaker(
    worker_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

