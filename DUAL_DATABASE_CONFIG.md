# Dual Database Configuration: Session Mode (API) + Transaction Mode (Workers)

## Overview

Weaver now uses a **dual database configuration** to optimize for both performance and scalability:

- **API**: Uses Supabase **Session Mode** (port `5432`) with prepared statements enabled
- **Workers**: Uses Supabase **Transaction Mode** (port `6543`) for higher connection limits

## Why This Approach?

### The Problem

When uploading multiple documents simultaneously, Celery workers create multiple database connections:
- 4 concurrent workers × 20 pool size = 80 potential connections
- Supabase Session Mode limit: ~15-20 connections
- Result: `MaxClientsInSessionMode` errors

### The Solution

**Session Mode (API - Port 5432)**
- ✅ Supports prepared statements (better performance)
- ✅ Maintains connection state
- ✅ Perfect for API requests (typically low concurrency)
- ⚠️ Limited connections (~15-20)

**Transaction Mode (Workers - Port 6543)**
- ✅ High connection limit (~200)
- ✅ Perfect for burst workloads (multiple uploads)
- ✅ Workers are short-lived transactions anyway
- ⚠️ Cannot use prepared statements (disabled via `statement_cache_size=0`)

## Configuration

### 1. Environment Variables

Add to your `.env` file:

```bash
# API uses Session Mode (port 5432) - prepared statements enabled
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Workers use Transaction Mode (port 6543) - high connection limits
WORKER_DATABASE_URL=postgresql+asyncpg://user:password@host:6543/dbname
```

**Note:** If `WORKER_DATABASE_URL` is not set, workers will fall back to using `DATABASE_URL`.

### 2. Get Supabase Connection Strings

In your Supabase Dashboard:

1. Go to **Project Settings** → **Database**
2. Under **Connection string**, find:
   - **Session mode** - Use for `DATABASE_URL`
   - **Transaction mode** - Use for `WORKER_DATABASE_URL`
3. Copy both connection strings

Example:
```bash
# Session Mode (port 5432)
DATABASE_URL=postgresql+asyncpg://postgres.xxx:password@aws-0-region.pooler.supabase.com:5432/postgres

# Transaction Mode (port 6543)
WORKER_DATABASE_URL=postgresql+asyncpg://postgres.xxx:password@aws-0-region.pooler.supabase.com:6543/postgres
```

### 3. Restart Services

```bash
docker-compose down
docker-compose up -d --build
```

## Architecture

### API Database Connection
**File:** `backend/app/db/connection.py`

```python
engine = create_async_engine(
    settings.DATABASE_URL,  # Port 5432
    pool_size=20,
    max_overflow=40,
    # Prepared statements enabled (default)
)
```

### Worker Database Connection
**File:** `backend/app/workers/db.py`

```python
worker_engine = create_async_engine(
    settings.worker_db_url,  # Port 6543
    pool_size=5,  # Smaller pool for workers
    max_overflow=10,
    connect_args={
        "statement_cache_size": 0,  # Required for Transaction Mode
    },
)
```

### Worker Tasks Integration
**File:** `backend/app/workers/tasks.py`

Workers automatically use the worker connection via monkey-patching:

```python
from app.workers.db import WorkerAsyncSessionLocal
from app.db import connection
connection.AsyncSessionLocal = WorkerAsyncSessionLocal
```

This ensures all repository operations in workers use Transaction Mode.

## How It Works

### API Requests
1. User makes API call to FastAPI
2. API uses `DATABASE_URL` (Session Mode, port 5432)
3. Prepared statements are cached for better performance
4. Connection pool: 20 + 40 overflow = 60 max connections
5. Supabase handles this easily with Session Mode

### Document Processing
1. User uploads 4 documents
2. 4 Celery workers start processing
3. Each worker uses `WORKER_DATABASE_URL` (Transaction Mode, port 6543)
4. Connection pool: 5 + 10 overflow = 15 max per worker
5. Total: 4 × 15 = 60 connections
6. Transaction Mode supports 200+ connections ✅

## Connection Pool Sizing

### API (Session Mode)
```python
pool_size=20         # Base connections
max_overflow=40      # Additional when needed
# Total: 60 max connections
```

Reasoning:
- API requests are typically sequential
- Most endpoints complete quickly (< 1 second)
- 20 base + 40 overflow is plenty for API traffic

### Workers (Transaction Mode)
```python
pool_size=5          # Base connections per worker
max_overflow=10      # Additional when needed per worker
# Total per worker: 15 max
# With 4 workers: 60 total
```

Reasoning:
- Workers are I/O bound (GCS downloads, embedding API calls)
- Small pool size is sufficient
- Transaction Mode allows many more connections if needed

## Troubleshooting

### Error: "prepared statement does not exist"

**Symptom:**
```
asyncpg.exceptions.InvalidSQLStatementNameError: 
prepared statement "__asyncpg_stmt_13__" does not exist
```

**Cause:** Using Transaction Mode without disabling prepared statements.

**Solution:** Ensure `statement_cache_size=0` in worker connection config (already configured in `backend/app/workers/db.py`).

### Error: "MaxClientsInSessionMode"

**Symptom:**
```
MaxClientsInSessionMode: max clients reached - in Session mode 
max clients are limited to pool_size
```

**Cause:** Workers are using Session Mode instead of Transaction Mode.

**Solution:** 
1. Verify `WORKER_DATABASE_URL` is set to port `6543`
2. Restart worker container: `docker-compose restart worker`
3. Check worker logs: `docker logs weaver-worker`

### Workers Still Using Session Mode

**Check:**
```bash
# View worker environment
docker exec weaver-worker env | grep DATABASE

# Should show:
WORKER_DATABASE_URL=postgresql+asyncpg://...6543/postgres
```

**If not set:**
1. Add `WORKER_DATABASE_URL` to your `.env` file
2. Restart: `docker-compose down && docker-compose up -d`

## Performance Impact

### API
- ✅ **No performance loss** - prepared statements still enabled
- ✅ **Better caching** - connection state maintained
- ✅ **Lower latency** - query planning cached

### Workers
- ⚠️ **~5-10% slower queries** - no prepared statements
- ✅ **Much better throughput** - higher connection limits
- ✅ **No connection errors** - can handle burst loads
- ✅ **Net positive** - workers are I/O bound anyway

The slight query performance loss in workers is negligible compared to:
- GCS download time: ~500ms
- Embedding generation: ~2-3 seconds per chunk
- Text extraction: ~100-500ms

## Monitoring

### Check Connection Usage

```bash
# API connections
docker logs weaver-api-1 | grep "pool"

# Worker connections
docker logs weaver-worker | grep "pool"
```

### Supabase Dashboard

1. Go to **Database** → **Connection pooling**
2. Monitor:
   - Session mode connections (should be low)
   - Transaction mode connections (can be higher)

## Migration from Single Database

If you were previously using a single `DATABASE_URL`:

1. **Add `WORKER_DATABASE_URL`** to `.env` with port `6543`
2. **Restart services**: `docker-compose down && docker-compose up -d`
3. **Test upload**: Upload 4 documents simultaneously
4. **Check logs**: Should see no connection errors

**That's it!** The configuration automatically falls back to `DATABASE_URL` if `WORKER_DATABASE_URL` is not set, so it's backward compatible.

## Production Recommendations

### For Supabase Users
✅ **Use this dual configuration** - it's the recommended approach
✅ **Keep API on Session Mode** - better performance
✅ **Keep Workers on Transaction Mode** - higher scalability

### Connection Pool Tuning
- **API**: Adjust `pool_size` based on concurrent API users
- **Workers**: Adjust based on Celery concurrency setting
- **Monitor**: Use Supabase dashboard to track actual usage

### Cost Optimization
- Transaction Mode has **no additional cost**
- Both modes use the same database
- Only difference is the pooler configuration

## Summary

| Aspect | API (Session) | Workers (Transaction) |
|--------|---------------|----------------------|
| **Port** | 5432 | 6543 |
| **Prepared Statements** | ✅ Enabled | ❌ Disabled |
| **Connection Limit** | ~15-20 | ~200 |
| **Pool Size** | 20+40 | 5+10 per worker |
| **Use Case** | API requests | Document processing |
| **Performance** | Optimal | Slightly slower queries, but I/O bound |

This configuration provides the **best of both worlds**: API gets maximum performance, workers get maximum scalability.

---

**Questions?** Check the logs or contact support if you encounter any issues.

Last Updated: November 2024 | Version 1.0

