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
- **AI-powered bot configuration** - Generate system prompts from simple business info (no prompt engineering needed)
- **Shared demo bot** for instant user onboarding (no document upload required)
- API key authentication
- Document ingestion (PDF, DOCX, TXT, HTML)
- RAG-based query answering
- Rate limiting (60 rpm per key)
- **Daily query limits** (50 queries/day, configurable)
- Real-time streaming responses
- Analytics dashboard
- **High-performance query engine (1.5-3s average latency)**
- **Redis caching for embeddings and queries**
- **Optimized HNSW vector search**

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

### Configure Bot Personality

```bash
# Generate system prompt from business info (AI-powered)
POST /v1/tenants/{tenant_id}/bot/generate-prompt
Authorization: Bearer <SESSION_TOKEN>
Content-Type: application/json

{
  "business_name": "Acme Corp",
  "industry": "E-commerce",
  "description": "We sell premium widgets online",
  "tone": "friendly",
  "primary_goal": "Help customers find products",
  "special_instructions": "Always mention free shipping over $50"
}

# Update bot configuration
PUT /v1/tenants/{tenant_id}/bot
Authorization: Bearer <SESSION_TOKEN>
Content-Type: application/json

{
  "system_prompt": "You are Acme Corp's AI assistant...",
  "business_info": { ... }
}
```

**See also:**
- `BOT_SETTINGS_QUICK_START.md` - User guide
- `BUSINESS_INFO_PROMPT_GENERATION.md` - Technical details

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
- Performance logs: `docker logs weaver-api-1 | grep "Query performance"`
- Cache metrics: `docker exec -it weaver-redis-1 redis-cli INFO stats`

## Performance

Weaver is optimized for production use with:
- **1.5-3s average query latency** (down from 10.9s)
- **<100ms for cached queries**
- **40-60% cost reduction** on LLM/embedding API calls
- **Redis caching** for embeddings and full query results
- **Optimized HNSW index** for fast vector search
- **Efficient connection pooling** and database indexes

For details, see:
- `PERFORMANCE_OPTIMIZATIONS.md` - Technical documentation
- `APPLY_PERFORMANCE_FIXES.md` - Quick start guide
- `PERFORMANCE_CHANGES_SUMMARY.md` - Changes overview

## Demo Bot

Weaver includes a **shared demo bot** that allows new users to test the platform immediately without uploading documents.

### Key Features
- ✅ All users can query the demo bot using their own API keys
- ✅ Queries count toward the user's personal daily limit (50/day)
- ✅ No setup required - works right after signup
- ✅ Helps users understand RAG capabilities before uploading own docs
- ✅ Seamless switch between demo bot and own bot

### Setup
1. Create admin user in Supabase Dashboard
2. Set `DEMO_BOT_ADMIN_UUID` and `DEMO_BOT_ADMIN_EMAIL` in `.env`
3. Run migrations: `docker-compose exec api alembic upgrade head`
4. Login as admin and upload demo content (PDFs about Weaver, RAG, API docs)
5. Users can now select "Demo Bot" in the API Keys tab

For complete setup instructions, see:
- `DEMO_BOT_ADMIN_SETUP.md` - Quick start (5 minutes)
- `DEMO_BOT_SETUP.md` - Comprehensive guide
- `DEMO_BOT_IMPLEMENTATION.md` - Technical overview

## License

Proprietary

