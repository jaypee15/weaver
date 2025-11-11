# Weaver - AI-Powered Knowledge Bot Platform

Weaver enables businesses to create and deploy AI customer-service bots trained on their own documents.

## Architecture

- **Backend**: FastAPI (Python 3.12)
- **Workers**: Celery + Redis
- **Database**: PostgreSQL + pgvector (HNSW index)
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Storage**: Google Cloud Storage (HMAC keys)
- **LLM**: Google Gemini (via LangChain)
- **Auth**: Supabase OAuth
- **Frontend**: React 18 + Vite + TypeScript
- **State Management**: Zustand + TanStack Query
- **Styling**: Tailwind CSS + shadcn/ui

## Features

- One bot per tenant architecture
- API key authentication
- Document ingestion (PDF, DOCX, TXT, HTML)
- RAG-based query answering
- Rate limiting (60 rpm per key)
- Real-time streaming responses
- Analytics dashboard

## Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL with pgvector
- Redis
- Google Cloud account
- Supabase account

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/weaver
REDIS_URL=redis://localhost:6379/0
GOOGLE_API_KEY=your_gemini_api_key
GCS_BUCKET_NAME=weaver-docs
GCS_PROJECT_ID=your_gcp_project
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

### Local Development

1. **Copy and configure environment variables**:

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

2. **Start everything with a single command**:

```bash
./start.sh
```

That's it! The script will:
- Build all Docker images
- Start PostgreSQL, Redis, API, Worker, and Frontend
- Run Alembic migrations automatically
- Wait for all services to be ready

Visit http://localhost:3000

**Note**: Migrations are now managed by Alembic (not raw SQL). See `SQLALCHEMY_MIGRATION.md` for details.

3. **To stop everything**:

```bash
./stop.sh
```

## API Endpoints

### Query Bot

```bash
POST /v1/tenants/{tenant_id}/query
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
  "query": "How do I reset my password?"
}
```

### Stream Query

```bash
GET /v1/tenants/{tenant_id}/query/stream?query=<query>
Authorization: Bearer <API_KEY>
```

### Upload Document

```bash
POST /v1/tenants/{tenant_id}/docs:upload
Authorization: Bearer <SESSION_TOKEN>
Content-Type: multipart/form-data

file: <file>
```

### Manage API Keys

```bash
# Create
POST /v1/tenants/{tenant_id}/api-keys
Authorization: Bearer <SESSION_TOKEN>

# List
GET /v1/tenants/{tenant_id}/api-keys
Authorization: Bearer <SESSION_TOKEN>

# Revoke
DELETE /v1/tenants/{tenant_id}/api-keys/{key_id}
Authorization: Bearer <SESSION_TOKEN>
```

## Deployment

### Build Docker Images

```bash
docker build -t gcr.io/PROJECT_ID/weaver-api:latest -f infra/docker/Dockerfile --target api .
docker build -t gcr.io/PROJECT_ID/weaver-worker:latest -f infra/docker/Dockerfile --target worker .
```

### Push to GCR

```bash
docker push gcr.io/PROJECT_ID/weaver-api:latest
docker push gcr.io/PROJECT_ID/weaver-worker:latest
```

### Deploy to Cloud Run

```bash
gcloud run services replace infra/deploy/cloudrun.yaml
```

## Database Migrations

Weaver uses **Alembic** for database migrations:

```bash
# Check current migration version
alembic current

# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "description"

# Rollback one migration
alembic downgrade -1
```

See `SQLALCHEMY_MIGRATION.md` for complete guide.

## Testing

```bash
cd backend
pytest tests/
```

## Monitoring

- Prometheus metrics: `/metrics`
- Health check: `/health`
- Sentry for error tracking

## License

Proprietary

