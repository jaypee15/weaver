# 🚀 Start Here - Weaver Quick Setup

Welcome to Weaver! Get your AI knowledge bot platform running in **under 5 minutes**.

## Prerequisites

- Docker Desktop installed and running
- Google Gemini API key
- Supabase account (for OAuth)

## Setup Steps

### 1. Get Your API Keys

**Google Gemini**:
- Visit https://makersuite.google.com/app/apikey
- Create API key

**Supabase**:
- Go to https://supabase.com
- Create project
- Get URL and anon key from Settings → API
- Enable Google OAuth in Authentication → Providers

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit with your credentials
nano .env  # or use your favorite editor
```

Required variables:
```bash
GOOGLE_API_KEY=your_gemini_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret
```

### 3. Start Everything

```bash
./start.sh
```

That's it! The script will:
- ✅ Build all containers
- ✅ Start PostgreSQL + Redis
- ✅ Run migrations
- ✅ Start API + Workers + Frontend
- ✅ Wait for everything to be ready

### 4. Access Your Platform

- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/metrics

### 5. Stop Everything

```bash
./stop.sh
```

## What You Get

✅ **Complete RAG System**
- Upload documents (PDF, DOCX, TXT, HTML)
- Automatic text extraction and chunking
- Vector embeddings with Gemini
- Semantic search with HNSW index
- AI-powered answers with source citations

✅ **Production-Ready Features**
- Multi-tenant isolation
- API key management
- Rate limiting (60 rpm)
- OAuth authentication
- Analytics dashboard
- Streaming responses
- Prometheus metrics

✅ **Developer Experience**
- Single command startup
- Auto migrations
- Hot reload in dev mode
- Comprehensive logging
- Health checks

## Next Steps

1. **Sign in** at http://localhost:3000
2. **Upload a document** in the dashboard
3. **Create an API key** in the API Keys tab
4. **Query your bot**:

```bash
curl -X POST http://localhost:8000/v1/tenants/YOUR_TENANT_ID/query \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?"}'
```

## Documentation

- **QUICKSTART.md** - Detailed setup guide
- **README.md** - API documentation
- **ARCHITECTURE.md** - System design
- **CHANGELOG.md** - Version history
- **MIGRATION_GUIDE.md** - Upgrade guide

## Troubleshooting

**Services won't start?**
```bash
docker-compose ps  # Check status
docker-compose logs -f  # View logs
```

**Need to reset everything?**
```bash
docker-compose down -v  # Remove all data
./start.sh  # Start fresh
```

## Support

- Check logs: `docker-compose logs -f [service]`
- View service status: `docker-compose ps`
- Restart service: `docker-compose restart [service]`

## What's New in v1.1.0

🎯 **Single Command Startup** - No more juggling multiple terminals
📊 **HNSW Index** - Better accuracy and performance than IVFFlat
🐳 **Fully Dockerized** - Frontend included, everything containerized
⚙️ **Simplified Config** - One .env file for everything

---

**Ready to build amazing AI bots?** Run `./start.sh` and let's go! 🚀

