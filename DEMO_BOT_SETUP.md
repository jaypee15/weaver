# Demo Bot Setup Guide

This guide explains how to set up and use the Weaver Demo Bot feature.

## Overview

The Demo Bot is a shared, pre-configured knowledge bot that allows new users to immediately test Weaver's capabilities without uploading their own documents. All users can query the demo bot using their own API keys, and queries count toward their personal daily limits.

## Architecture

```
┌─────────────────────────────────────────────┐
│  User Signs Up                              │
│  ↓                                          │
│  Gets Tenant ID + API Keys                  │
│  ↓                                          │
│  Can Query:                                 │
│  • Demo Bot (00000000-0000-0000-0000-...)  │
│  • Own Bot (after uploading docs)          │
└─────────────────────────────────────────────┘

Access Control:
- User can query demo_bot_id OR their own tenant_id
- Daily limits tracked per user's tenant_id (not per bot)
- Rate limits apply per API key
```

## Setup Steps

### 1. Configuration

The demo bot is configured via environment variables:

```bash
# In .env or env.template
DEMO_BOT_TENANT_ID=00000000-0000-0000-0000-000000000000
DEMO_BOT_ENABLED=true
```

These are already set in:
- `backend/app/config.py`
- `docker-compose.yml`
- `env.template`

### 2. Database Migration

Run the migration to create the demo bot tenant and bot:

```bash
# If migrations are disabled in docker-compose.yml
export RUN_MIGRATIONS=true
docker-compose up -d api

# Or run manually with direct database connection
docker-compose exec api alembic upgrade head
```

This creates:
- **Demo Tenant**: ID `00000000-0000-0000-0000-000000000000`, name "Weaver Demo Bot"
- **Demo Bot**: With a custom system prompt explaining Weaver's features

### 3. Create Demo Bot Admin (Optional but Recommended)

To upload demo content, you need an admin user linked to the demo bot tenant.

**Step 3.1: Create Admin User in Supabase**

1. Go to **Supabase Dashboard** → **Authentication** → **Users**
2. Click **"Add user"**
3. Enter:
   - **Email:** `admin@weaver.com` (or your preferred admin email)
   - **Password:** Set a secure password
   - **Auto Confirm User:** ✅ Enable
4. Click **"Create user"**
5. **Copy the User UUID** from the list (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)

**Step 3.2: Configure Environment Variables**

Add these to your `.env` file:

```bash
# Demo Bot Admin User
DEMO_BOT_ADMIN_UUID=a1b2c3d4-e5f6-7890-abcd-ef1234567890  # From Supabase
DEMO_BOT_ADMIN_EMAIL=admin@weaver.com  # Must match Supabase email
```

**Step 3.3: Run Migration**

The migration will now create the admin profile linked to the demo bot tenant:

```bash
# Restart API to pick up new environment variables
docker-compose restart api

# Or re-run migration if already run
docker-compose exec api alembic downgrade -1
docker-compose exec api alembic upgrade head
```

You should see:
```
✓ Created admin profile for admin@weaver.com (UUID: a1b2c3d4-e5f6-7890-abcd-ef1234567890)
```

### 4. Upload Demo Content

Upload sample documents to the demo bot's knowledge base:

**Option A: Via UI (Recommended)**

1. Open the frontend: `http://localhost:3000`
2. Click **"Sign in with Google"** or use Supabase email/password
3. Log in with the admin credentials you created
4. Go to **Upload** tab
5. Upload 3-5 PDFs about Weaver, RAG, API docs
6. Wait for processing to complete

**Option B: Via API**

First, create an API key for the admin:

```bash
# Login as admin via UI first, then go to API Keys tab and create a key
# Or create via API:
ADMIN_SESSION_TOKEN="your_admin_session_token"
DEMO_TENANT_ID="00000000-0000-0000-0000-000000000000"

curl -X POST "http://localhost:8000/v1/tenants/$DEMO_TENANT_ID/api-keys" \
  -H "Authorization: Bearer $ADMIN_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Demo Admin Key"}'

# Copy the returned API key
API_KEY="returned_api_key"

# Upload documents
curl -X POST "http://localhost:8000/v1/tenants/$DEMO_TENANT_ID/docs:upload" \
  -H "Authorization: Bearer $ADMIN_SESSION_TOKEN" \
  -F "file=@demo_docs/weaver_overview.pdf"
```

**Suggested Demo Content:**
- `weaver_overview.pdf` - Overview of the Weaver platform
- `rag_guide.pdf` - Introduction to RAG (Retrieval-Augmented Generation)
- `integration_examples.pdf` - API integration examples
- `faq.pdf` - Common questions about Weaver

### 4. Verify Setup

Test the demo bot:

```bash
# Get any user's API key
USER_API_KEY="test_user_api_key"

# Query the demo bot
curl -X POST "http://localhost:8000/v1/tenants/00000000-0000-0000-0000-000000000000/query" \
  -H "Authorization: Bearer $USER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Weaver?"}'
```

Expected response:
```json
{
  "answer": "Weaver is an AI-powered knowledge bot platform...",
  "sources": [...],
  "confidence": "high",
  "latency_ms": 2500,
  "daily_usage": {
    "current": 1,
    "limit": 50,
    "remaining": 49,
    "redis_available": true
  }
}
```

## How It Works

### Backend Logic

**File**: `backend/app/api/v1/routes.py`

```python
# In query endpoints
demo_bot_id = UUID(settings.DEMO_BOT_TENANT_ID) if settings.DEMO_BOT_ENABLED else None

if tenant_id != api_key_data.tenant_id:
    # Check if querying demo bot
    if not (demo_bot_id and tenant_id == demo_bot_id):
        raise HTTPException(status_code=403, detail="Access denied")

# Always use user's tenant_id for daily limits
limit_info = await daily_limit_service.check_and_increment(api_key_data.tenant_id)
```

**Key Points:**
- ✅ Users can query `demo_bot_id` OR their own `tenant_id`
- ✅ Daily limits tracked against user's `tenant_id`, not the demo bot
- ✅ Rate limits (per minute) apply per API key
- ❌ Users cannot query other users' bots

### Frontend UI

**File**: `frontend/src/components/dashboard/APIKeysTab.tsx`

The frontend provides:

1. **Bot Selector** in Test Panel
   - 🎯 Demo Bot (always enabled)
   - 📚 Your Bot (enabled after uploading docs)

2. **API Endpoint Documentation**
   - Shows both demo bot and user's bot endpoints
   - Visual status indicators (Ready / Upload docs first)
   - Code examples for cURL, JavaScript, Python

3. **In-App Testing**
   - Select demo bot or own bot
   - Test streaming and non-streaming queries
   - See results in real-time

## User Flow

### New User Experience

1. **User signs up** → Gets tenant ID + API key
2. **Lands on Dashboard** → Sees "Test Your Bot" panel
3. **Clicks API Keys tab** → Sees demo bot endpoint is ready
4. **Selects Demo Bot** → Yellow info banner explains it's a demo
5. **Pastes API key** → Tests queries immediately
6. **Sees results** → Understands how Weaver works
7. **Uploads own docs** → Can switch to "Your Bot"
8. **Both work** → Can query demo OR own bot anytime

### Query Counting

- ✅ Demo bot query: Counts toward user's 50/day limit
- ✅ Own bot query: Counts toward user's 50/day limit
- ✅ Combined total: 50 queries/day across both bots
- ✅ Resets: At midnight UTC

## Security

### Access Control

✅ **Allowed:**
- User queries their own bot
- User queries the demo bot
- Admin queries any bot (if role-based auth is added)

❌ **Blocked:**
- User queries another user's bot
- Anonymous queries (API key required)

### Rate Limiting

- **Per-Minute:** 60 requests per API key (configurable via `RATE_LIMIT_RPM`)
- **Per-Day:** 50 queries per tenant (configurable via `MAX_QUERIES_PER_DAY`)
- **Cached:** Duplicate queries use cache (5-minute TTL)

### Data Isolation

- ✅ Demo bot documents are read-only for users
- ✅ Users cannot upload to demo bot (only their own)
- ✅ Query logs are per-tenant
- ✅ Analytics are per-tenant

## Configuration Options

### Disable Demo Bot

To disable the demo bot:

```bash
# In .env
DEMO_BOT_ENABLED=false
```

This will:
- Return 403 for any queries to the demo bot tenant ID
- Hide demo bot option in the UI (optional, requires frontend update)

### Change Demo Bot ID

To use a different tenant ID for the demo bot:

```bash
# In .env
DEMO_BOT_TENANT_ID=your-custom-uuid-here
```

Then:
1. Create a tenant with that ID in the database
2. Upload demo documents to that tenant
3. Restart the API service

## Monitoring

### Check Demo Bot Usage

```bash
# Query logs for demo bot
docker-compose exec api psql $DATABASE_URL -c "
  SELECT 
    DATE(created_at) as date,
    COUNT(*) as queries,
    AVG(latency_ms) as avg_latency
  FROM bot_queries
  WHERE tenant_id = '00000000-0000-0000-0000-000000000000'
  GROUP BY DATE(created_at)
  ORDER BY date DESC
  LIMIT 7;
"
```

### Check Document Count

```bash
# Count demo bot documents
docker-compose exec api psql $DATABASE_URL -c "
  SELECT 
    COUNT(*) as total_docs,
    COUNT(*) FILTER (WHERE status = 'completed') as processed,
    COUNT(*) FILTER (WHERE status = 'failed') as failed
  FROM documents
  WHERE tenant_id = '00000000-0000-0000-0000-000000000000';
"
```

### Check Embeddings

```bash
# Count demo bot chunks
docker-compose exec api psql $DATABASE_URL -c "
  SELECT 
    COUNT(*) as total_chunks,
    COUNT(DISTINCT doc_id) as unique_docs
  FROM doc_chunks
  WHERE tenant_id = '00000000-0000-0000-0000-000000000000';
"
```

## Troubleshooting

### Users Can't Query Demo Bot

**Symptom:** 403 Forbidden error when querying demo bot

**Possible Causes:**
1. `DEMO_BOT_ENABLED=false` in environment
2. Demo bot tenant ID doesn't match configuration
3. API key is invalid

**Fix:**
```bash
# Check config
docker-compose exec api env | grep DEMO_BOT

# Verify tenant exists
docker-compose exec api psql $DATABASE_URL -c "
  SELECT id, name FROM tenants 
  WHERE id = '00000000-0000-0000-0000-000000000000';
"
```

### Demo Bot Returns Empty Results

**Symptom:** "I don't know based on the available information."

**Possible Causes:**
1. No documents uploaded to demo bot
2. Documents failed processing
3. Embeddings not generated

**Fix:**
```bash
# Check documents
docker-compose exec api psql $DATABASE_URL -c "
  SELECT filename, status, error_message 
  FROM documents 
  WHERE tenant_id = '00000000-0000-0000-0000-000000000000';
"

# Check chunks
docker-compose exec api psql $DATABASE_URL -c "
  SELECT COUNT(*) FROM doc_chunks 
  WHERE tenant_id = '00000000-0000-0000-0000-000000000000';
"
```

### Demo Bot Queries Too Slow

**Symptom:** High latency (>5 seconds) for demo bot queries

**Possible Causes:**
1. Too many chunks (increase `TOP_K_RESULTS`)
2. HNSW index not optimized
3. Redis cache not working

**Fix:**
```bash
# Check index
docker-compose exec api psql $DATABASE_URL -c "
  SELECT schemaname, tablename, indexname 
  FROM pg_indexes 
  WHERE tablename = 'doc_chunks';
"

# Check Redis cache
docker-compose exec redis redis-cli INFO stats | grep keyspace_hits
```

## Best Practices

### Content Recommendations

For the demo bot, upload content that:
- ✅ Explains what Weaver is and how it works
- ✅ Provides example use cases
- ✅ Shows API integration examples
- ✅ Answers common questions
- ✅ Demonstrates RAG capabilities
- ❌ Avoid sensitive or proprietary information
- ❌ Keep content generic and educational

### Document Size

- **Recommended:** 3-5 documents, 10-50 pages total
- **Max:** Follow your `MAX_FILE_SIZE_MB` limit (default: 200MB)
- **Format:** PDF works best (PyMuPDF for text extraction)

### Query Examples

Pre-populate the UI with sample queries:
- "What is Weaver?"
- "How does RAG work?"
- "How do I integrate the API?"
- "What are the rate limits?"
- "Can I use this for customer support?"

## Future Enhancements

Potential improvements:
1. **Multi-language demo bots** (English, Spanish, etc.)
2. **Industry-specific demos** (Healthcare, Legal, Finance)
3. **Query suggestions** based on demo bot content
4. **Analytics dashboard** for demo bot usage
5. **A/B testing** different demo bot configurations
6. **Feedback collection** on demo bot responses

## Summary

✅ **Implemented:**
- Backend access control for demo bot
- Frontend bot selector with visual states
- API endpoint documentation with examples
- In-app test panel with streaming support
- Daily usage tracking per user

🎯 **Next Steps:**
1. Run migration: `docker-compose exec api alembic upgrade head`
2. Upload demo content via API or UI
3. Test with a user API key
4. Monitor usage and performance

---

**Documentation Version:** 1.0  
**Last Updated:** 2025-11-12  
**Related Files:**
- `backend/app/config.py` - Configuration
- `backend/app/api/v1/routes.py` - Access control logic
- `frontend/src/components/dashboard/APIKeysTab.tsx` - UI
- `backend/alembic/versions/004_create_demo_bot.py` - Migration

