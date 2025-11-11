# Weaver Quick Start Guide

Get Weaver running locally in 5 minutes!

## Step 1: Prerequisites

Install the following:
- [Python 3.12+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Step 2: Get API Keys

### Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy it for later

### Supabase Setup
1. Go to [Supabase](https://supabase.com)
2. Create a new project
3. Go to Settings → API
4. Copy the URL and anon key
5. Go to Authentication → Providers
6. Enable Google OAuth
7. Configure OAuth callback: `http://localhost:3000/auth/callback`

### Google Cloud Storage (Optional for local dev)
1. Create a GCP project
2. Enable Cloud Storage API
3. Create a bucket named `weaver-docs`
4. Download service account credentials

## Step 3: Configure Environment

Create and edit `.env` file:

```bash
cd ~/makermode/weaver
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Google Gemini
GOOGLE_API_KEY=your_gemini_api_key_here

# Google Cloud Storage
GCS_BUCKET_NAME=weaver-docs
GCS_PROJECT_ID=your_gcp_project_id

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

## Step 4: Start Everything with One Command

```bash
./start.sh
```

That's it! The script will:
- ✅ Build all Docker images (API, Worker, Frontend)
- ✅ Start PostgreSQL with pgvector
- ✅ Start Redis
- ✅ Run Alembic migrations automatically (SQLAlchemy ORM)
- ✅ Start the API server
- ✅ Start Celery workers
- ✅ Start the frontend
- ✅ Wait for everything to be ready

The entire stack starts with a single command!

## Step 5: Access the App

1. Open http://localhost:3000
2. Click "Sign in with Google"
3. Complete OAuth flow
4. You'll be redirected to the dashboard

## Step 6: Test the System

### Upload a Document

1. Go to the "Upload Documents" tab
2. Select a PDF, DOCX, or TXT file (max 200MB)
3. Click "Upload"
4. Wait for processing (check Terminal 2 for worker logs)

### Create an API Key

1. Go to the "API Keys" tab
2. Click "Create New API Key"
3. Copy the key (it's only shown once!)

### Query Your Bot

Using curl:

```bash
curl -X POST http://localhost:8000/v1/tenants/YOUR_TENANT_ID/query \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?"}'
```

Or using the streaming endpoint:

```bash
curl -N http://localhost:8000/v1/tenants/YOUR_TENANT_ID/query/stream?query=Hello \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Stopping the Platform

To stop all services:

```bash
./stop.sh
```

To stop and remove all data (including database):

```bash
docker-compose down -v
```

## Troubleshooting

### "Connection refused" errors
- Make sure Docker is running
- Check service status: `docker-compose ps`
- View logs: `docker-compose logs -f`
- Restart if needed: `docker-compose restart`

### "Invalid API key" errors
- Check that you copied the full key including the `wvr_` prefix
- Verify the key hasn't been revoked in the dashboard

### Services not starting
- Check Docker Desktop is running
- View specific service logs: `docker-compose logs -f api` (or worker, frontend)
- Rebuild images: `docker-compose build --no-cache`

### Database migration errors
- Migrations run automatically on first API startup
- To manually run: `docker-compose exec api psql -h postgres -U weaver -d weaver -f /app/app/db/models.sql`

### Worker not processing jobs
- Check worker logs: `docker-compose logs -f worker`
- Verify Redis is running: `docker-compose ps redis`
- Restart worker: `docker-compose restart worker`

## Next Steps

- Read [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system
- Check [README.md](./README.md) for detailed API documentation
- Review [CONTRIBUTING.md](./CONTRIBUTING.md) if you want to contribute
- Deploy to production using [scripts/deploy.sh](./scripts/deploy.sh)

## Getting Help

- Check the logs in all 3 terminals
- Visit http://localhost:8000/docs for API documentation
- Open an issue on GitHub
- Review the code comments for implementation details

Happy building! 🚀

