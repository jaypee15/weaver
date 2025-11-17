"""
Worker-specific database connection configuration.

Workers use Transaction Mode (port 6543) for higher connection limits,
while the API uses Session Mode (port 5432) for prepared statements.

IMPORTANT: Workers use NullPool to avoid connection pool persistence issues
with asyncio.run() creating fresh event loops per task.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.config import settings


def _assert_worker_uses_transaction_mode() -> None:
    url = settings.worker_db_url
    if ":6543/" not in url:
        raise RuntimeError(f"Worker DB URL is not using Transaction Mode port 6543: {url}")


_assert_worker_uses_transaction_mode()


# Worker engine configured for Transaction Mode (pgbouncer)
# - Uses WORKER_DATABASE_URL (port 6543)
# - Disables prepared statements (required for pgbouncer transaction mode)
# - Uses NullPool to prevent connection reuse across different event loops
#   (each asyncio.run() creates a new loop, so pooled connections become invalid)
worker_engine = create_async_engine(
    settings.worker_db_url,
    echo=False,
    poolclass=NullPool,  # No connection pooling - create fresh connections per task
    connect_args={
        "server_settings": {
            "jit": "off",
        },
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "prepared_statement_name_func": lambda: None,  # Disable prepared statement naming
    },
)

WorkerAsyncSessionLocal = sessionmaker(
    worker_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

