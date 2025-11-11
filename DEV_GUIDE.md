# Development Guide

## Quick Start

### Development Mode (Hot-Reload)

For local development with hot-reload on all services:

```bash
./start-dev.sh
```

This starts:
- **Frontend**: Next.js dev server with hot-reload (changes reflect instantly)
- **Backend API**: FastAPI with volume mount (changes reflect on save)
- **Worker**: Celery with volume mount (restart worker to pick up changes)

### Production Mode

For production-like environment:

```bash
docker-compose up --build
```

This builds optimized production images.

## Development Workflow

### Frontend Changes
1. Edit files in `frontend/`
2. Changes auto-reload in browser (no rebuild needed!)
3. See changes instantly at http://localhost:3000

### Backend API Changes
1. Edit files in `backend/app/`
2. FastAPI auto-reloads (no rebuild needed!)
3. Test at http://localhost:8000

### Worker Changes
1. Edit files in `backend/app/workers/` or `backend/app/services/`
2. Restart worker: `docker-compose restart worker`
3. No full rebuild needed!

### Database Migrations
1. Create migration: `docker-compose exec api alembic revision --autogenerate -m "description"`
2. Apply migration: `docker-compose exec api alembic upgrade head`
3. Check status: `docker-compose exec api alembic current`

## Stopping Services

```bash
docker-compose down
```

Or with cleanup:

```bash
docker-compose down -v  # Also removes volumes
```

## Logs

View logs for specific service:

```bash
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f frontend
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `GOOGLE_API_KEY` - For Gemini embeddings
- `GCS_ACCESS_KEY` / `GCS_SECRET_KEY` - For Google Cloud Storage
- `SUPABASE_URL` / `SUPABASE_KEY` - For authentication

## Tips

- **Backend changes**: Auto-reload enabled, just save and test
- **Frontend changes**: Auto-reload enabled, see changes instantly
- **Worker changes**: Restart with `docker-compose restart worker`
- **New dependencies**: Rebuild that service only (e.g., `docker-compose build frontend`)
- **Database schema changes**: Use Alembic migrations
- **Clear everything**: `docker-compose down -v && docker-compose up --build`

