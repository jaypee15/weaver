# Weaver Architecture

## Overview

Weaver is a multi-tenant SaaS platform for creating AI-powered knowledge bots. The system follows a one-bot-per-tenant model with API key authentication.

## System Components

### Backend API (FastAPI)

- **Framework**: FastAPI (Python 3.12)
- **Authentication**: 
  - Dashboard: Supabase OAuth (Google)
  - Bot API: API Key (Argon2 hashed)
- **Rate Limiting**: Redis token bucket (60 rpm default)
- **Observability**: Prometheus metrics, Sentry, structured JSON logging

**Key Endpoints**:
- `POST /v1/tenants/{tenant_id}/query` - Query bot
- `GET /v1/tenants/{tenant_id}/query/stream` - SSE streaming
- `POST /v1/tenants/{tenant_id}/docs:upload` - Upload documents
- `POST /v1/tenants/{tenant_id}/api-keys` - Manage API keys
- `GET /v1/tenants/{tenant_id}/analytics/*` - Analytics

### Workers (Celery)

- **Queue**: Redis
- **Tasks**:
  - Document extraction (PDF, DOCX, TXT, HTML)
  - Text chunking (800 tokens, 20% overlap)
  - Embedding generation (Gemini embedding-001, 1536-dim)
  - Vector upsert to pgvector

### Database (PostgreSQL + pgvector)

**ORM**: SQLAlchemy 2.0 (async)
**Migrations**: Alembic (versioned, auto-generated)

**Schema**:
- `tenants` - Tenant metadata
- `users` - User accounts (linked to Supabase)
- `bots` - Bot config (1:1 with tenants)
- `docs` - Document metadata
- `doc_chunks` - Text chunks with embeddings (vector(1536))
- `api_keys` - Hashed API keys
- `bot_queries` - Query logs for analytics

**Indexes**:
- HNSW on `doc_chunks.embedding` for fast cosine similarity search (m=16, ef_construction=64)
- B-tree indexes on foreign keys and frequently queried columns

**Models**: All tables defined as SQLAlchemy ORM models in `app/db/models.py` with relationships

### Storage (Google Cloud Storage)

- Bucket structure: `gs://weaver/{tenant_id}/docs/{filename}`
- Stores original uploaded documents
- Used by workers for extraction

### LLM & Embeddings (Google Gemini via LangChain)

- **Embeddings**: `gemini-embedding-001` (1536 dimensions)
- **Chat**: `gemini-pro` (temperature 0.2)
- **Integration**: LangChain-Google-GenAI
  - `GoogleGenerativeAIEmbeddings` for embeddings
  - `ChatGoogleGenerativeAI` for chat completion

### Frontend (Next.js)

- **Framework**: Next.js 14 + React 18
- **Styling**: Tailwind CSS
- **Auth**: Supabase Auth Helpers
- **Features**:
  - Document upload
  - API key management
  - Analytics dashboard

## Data Flow

### Document Ingestion

```
User uploads file
    ↓
FastAPI receives file
    ↓
Upload to GCS (gs://weaver/{tenant_id}/docs/)
    ↓
Create doc record in DB (status: pending)
    ↓
Enqueue Celery task
    ↓
Worker downloads from GCS
    ↓
Extract text (PyMuPDF, python-docx, html2text)
    ↓
Chunk text (800 tokens, 20% overlap)
    ↓
Generate embeddings (Gemini via LangChain)
    ↓
Upsert to doc_chunks table
    ↓
Update doc status to completed
```

### Query Processing

```
Client sends query with API key
    ↓
Verify API key (hash check)
    ↓
Check rate limit (Redis)
    ↓
Embed query (Gemini via LangChain)
    ↓
Search similar chunks (pgvector cosine similarity, top-k=8)
    ↓
Build prompt with context
    ↓
Generate answer (Gemini via LangChain)
    ↓
Calculate confidence (based on similarity scores)
    ↓
Log query to bot_queries
    ↓
Return response with sources
```

## Security

### API Key Management

- Keys generated with `secrets.token_urlsafe(48)`
- Prefix: `wvr_`
- Hashed with Argon2id before storage
- Verification via constant-time comparison
- Revocable per key
- Rotatable without downtime

### Tenant Isolation

- All queries filtered by `tenant_id`
- Separate GCS namespaces
- Row-level security via application logic
- No cross-tenant data leakage

### Rate Limiting

- Redis sliding window (token bucket)
- Per API key limits (default 60 rpm)
- Configurable per key
- Returns 429 on exceed

## Scalability

### Horizontal Scaling

- **API**: Cloud Run auto-scales (1-10 instances)
- **Workers**: Multiple Celery workers (3+ recommended)
- **Database**: PostgreSQL with read replicas
- **Redis**: Redis Cluster for high availability

### Performance Optimizations

- HNSW index on embeddings (m=16, ef_construction=64) - better accuracy than IVFFlat
- Connection pooling (SQLAlchemy)
- Async I/O (FastAPI + asyncpg)
- Batch embedding generation
- Cached embeddings (no re-computation)

## Monitoring

### Metrics (Prometheus)

- `weaver_queries_total` - Query count by tenant/confidence
- `weaver_query_latency_seconds` - Query latency histogram
- `weaver_ingestion_total` - Ingestion job count by status
- `weaver_active_tenants` - Active tenant gauge
- `weaver_api_errors_total` - Error count by endpoint

### Logging

- Structured JSON logs
- Fields: `request_id`, `tenant_id`, `latency_ms`, `status`
- Centralized via GCP Logging

### Error Tracking

- Sentry integration
- Automatic error capture
- Performance monitoring (10% sample rate)

## Deployment

### Local Development

```bash
# Single command to start everything
./start.sh

# To stop
./stop.sh
```

The startup script automatically:
- Builds and starts all Docker containers
- Runs database migrations
- Waits for all services to be healthy
- Displays access URLs and logs

### Production (GCP)

- **API**: Cloud Run (managed, auto-scaling)
- **Workers**: Compute Engine or GKE
- **Database**: Cloud SQL (PostgreSQL with pgvector)
- **Redis**: Memorystore
- **Storage**: Cloud Storage
- **Secrets**: Secret Manager

## Future Enhancements

- Fine-tuning support
- Human-in-the-loop editor
- Multi-language support
- Advanced analytics (A/B testing)
- Third-party integrations (Slack, Zendesk)
- Usage-based billing

