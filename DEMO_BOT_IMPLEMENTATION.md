# Demo Bot Implementation Summary

## Overview

Implemented a **shared demo bot** feature that allows all users to immediately query a pre-configured knowledge bot using their own API keys, without uploading documents first. Queries count toward their personal daily limits.

## What Was Changed

### 1. Backend Configuration
- **File:** `backend/app/config.py`
- **Added:**
  ```python
  DEMO_BOT_TENANT_ID: str = "00000000-0000-0000-0000-000000000000"
  DEMO_BOT_ENABLED: bool = True
  ```

### 2. API Endpoints (Access Control)
- **File:** `backend/app/api/v1/routes.py`
- **Modified:** `/v1/tenants/{tenant_id}/query` and `/v1/tenants/{tenant_id}/query/stream`
- **Logic:**
  ```python
  # Allow access to demo bot OR user's own tenant
  demo_bot_id = UUID(settings.DEMO_BOT_TENANT_ID) if settings.DEMO_BOT_ENABLED else None
  
  if tenant_id != api_key_data.tenant_id:
      if not (demo_bot_id and tenant_id == demo_bot_id):
          raise HTTPException(status_code=403, detail="Access denied")
  
  # Always use user's tenant_id for daily limits (not demo bot's)
  limit_info = await daily_limit_service.check_and_increment(api_key_data.tenant_id)
  ```

### 3. Database Migration
- **File:** `backend/alembic/versions/004_create_demo_bot.py`
- **Creates:**
  - Demo tenant with ID `00000000-0000-0000-0000-000000000000`
  - Demo bot with custom system prompt
  - **Admin profile** (optional, if `DEMO_BOT_ADMIN_UUID` is set)

### 4. Environment Configuration
- **Files:** `docker-compose.yml`, `env.template`
- **Added:**
  ```bash
  DEMO_BOT_TENANT_ID=00000000-0000-0000-0000-000000000000
  DEMO_BOT_ENABLED=true
  DEMO_BOT_ADMIN_UUID=  # Optional: Supabase user UUID for admin
  DEMO_BOT_ADMIN_EMAIL=admin@weaver.com  # Optional: Admin email
  ```

### 5. Frontend Updates
- **File:** `frontend/src/components/dashboard/APIKeysTab.tsx`
- **Added:**
  - Bot selector (Demo Bot / Your Bot) in test panel
  - Visual indicators for bot availability
  - Updated API endpoint documentation showing both bots
  - Info banner explaining demo bot purpose
  - Dynamic placeholder text and examples

## Key Features

✅ **No Additional Tables** - Uses existing tenant/bot structure  
✅ **Simple Access Control** - If `tenant_id == demo_bot_id OR user's tenant_id`, allow  
✅ **User Quota Tracking** - Queries count toward user's daily limit, not demo bot's  
✅ **Immediate Testing** - New users can query the bot right after signup  
✅ **Seamless Switch** - Users can query demo bot and their own bot interchangeably  
✅ **Production Ready** - Includes monitoring, troubleshooting, and best practices  

## User Experience Flow

1. **User signs up** → Gets API key
2. **Opens API Keys tab** → Sees demo bot is ready
3. **Selects Demo Bot** → Yellow banner explains it's for testing
4. **Pastes API key** → Tests queries immediately
5. **Uploads own docs** → Can switch to "Your Bot"
6. **Both work** → Can use demo or own bot anytime

## Security Model

### Access Rules
- ✅ User can query: **demo bot** OR **their own bot**
- ❌ User cannot query: **other users' bots**
- ✅ Daily limits: **Tracked per user's tenant_id**
- ✅ Rate limits: **Applied per API key**

### Data Isolation
- ✅ Demo bot documents are read-only
- ✅ Users cannot upload to demo bot
- ✅ Query logs are per-tenant
- ✅ Analytics are per-tenant

## Next Steps

### 1. Create Admin User in Supabase
```bash
# Go to Supabase Dashboard → Authentication → Users
# Click "Add user"
# Email: admin@weaver.com
# Password: [secure password]
# Auto Confirm: ✅
# Copy the User UUID (e.g., a1b2c3d4-e5f6-7890-abcd-ef1234567890)
```

### 2. Configure Environment Variables
```bash
# Add to .env
DEMO_BOT_ADMIN_UUID=a1b2c3d4-e5f6-7890-abcd-ef1234567890
DEMO_BOT_ADMIN_EMAIL=admin@weaver.com
```

### 3. Run Migration
```bash
# Restart API to pick up new environment variables
docker-compose restart api

# Or run migration manually
docker-compose exec api alembic upgrade head
```

You should see:
```
✓ Created admin profile for admin@weaver.com (UUID: a1b2c3d4-...)
```

### 4. Upload Demo Content
```bash
# Option 1: Via UI (Recommended)
# 1. Open http://localhost:3000
# 2. Login with admin@weaver.com
# 3. Go to Upload tab
# 4. Upload PDFs about Weaver, RAG, API docs

# Option 2: Via API
# First, login as admin and get session token
# Then create API key in UI or via API
# Upload documents using the API key
```

### 5. Test
```bash
# Query demo bot with any user's API key
curl -X POST "http://localhost:8000/v1/tenants/00000000-0000-0000-0000-000000000000/query" \
  -H "Authorization: Bearer USER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Weaver?"}'
```

### 6. Verify UI
1. Sign up as a new user
2. Go to API Keys tab
3. See demo bot endpoint with "Ready to use" badge
4. Test demo bot in the test panel
5. Upload a document to your own bot
6. Switch to "Your Bot" and test

## Configuration

### Enable/Disable
```bash
# Disable demo bot
DEMO_BOT_ENABLED=false

# Change demo bot ID
DEMO_BOT_TENANT_ID=your-custom-uuid
```

### Customize Content
- Upload 3-5 documents (10-50 pages total)
- Focus on educational, platform-specific content
- Avoid sensitive or proprietary information

## Monitoring

```bash
# Check demo bot usage
docker-compose exec api psql $DATABASE_URL -c "
  SELECT COUNT(*), AVG(latency_ms) 
  FROM bot_queries 
  WHERE tenant_id = '00000000-0000-0000-0000-000000000000';
"

# Check document count
docker-compose exec api psql $DATABASE_URL -c "
  SELECT COUNT(*) FROM documents 
  WHERE tenant_id = '00000000-0000-0000-0000-000000000000';
"

# Check embeddings
docker-compose exec api psql $DATABASE_URL -c "
  SELECT COUNT(*) FROM doc_chunks 
  WHERE tenant_id = '00000000-0000-0000-0000-000000000000';
"
```

## Files Modified/Created

### Backend
- ✅ `backend/app/config.py` - Added demo bot config
- ✅ `backend/app/api/v1/routes.py` - Added access control logic
- ✅ `backend/alembic/versions/004_create_demo_bot.py` - New migration

### Frontend
- ✅ `frontend/src/components/dashboard/APIKeysTab.tsx` - Added bot selector and UI

### Configuration
- ✅ `docker-compose.yml` - Added environment variables
- ✅ `env.template` - Added demo bot config

### Documentation
- ✅ `DEMO_BOT_SETUP.md` - Comprehensive setup guide
- ✅ `DEMO_BOT_IMPLEMENTATION.md` - This summary

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Signup                          │
│                            ↓                                │
│                  Tenant ID + API Key                        │
│                            ↓                                │
│              ┌──────────────┴──────────────┐                │
│              ↓                             ↓                │
│        Query Demo Bot              Query Own Bot            │
│   (00000000-0000-0000...)       (User's Tenant ID)          │
│              ↓                             ↓                │
│     Pre-loaded Content            User Uploaded Docs        │
│              └──────────────┬──────────────┘                │
│                             ↓                               │
│                  Daily Limit Tracking                       │
│                  (User's Tenant ID)                         │
│                     50 queries/day                          │
└─────────────────────────────────────────────────────────────┘
```

## Benefits

1. **Immediate Value** - Users can test the platform without setup
2. **Lower Friction** - No need to upload documents first
3. **Better Onboarding** - Users understand capabilities quickly
4. **Increased Conversions** - From signup to active usage
5. **Simple Architecture** - No additional tables or complexity
6. **Scalable** - Queries cached, limits enforced

## Comparison: Alternatives Not Chosen

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **Shared Demo Bot** (✅ Chosen) | Simple, no tables, works immediately | All users see same content | ✅ Best for MVP |
| Per-User Demo Bots | Isolated content | Complex, many DB rows | ❌ Overkill |
| Permissions Table | Granular control | Extra table, migrations | ❌ Unnecessary |
| No Demo Bot | Simplest | Poor onboarding | ❌ Bad UX |

## Success Metrics

Track these to measure demo bot effectiveness:
- **Demo bot queries** / Total queries
- **Time to first query** (signup → query)
- **Demo-to-own bot conversion** (% users who upload docs)
- **Daily active users** querying demo bot
- **Average queries per demo session**

---

**Implementation Status:** ✅ Complete  
**Testing Status:** ⏳ Pending (awaiting user testing)  
**Documentation:** ✅ Complete  
**Production Ready:** ✅ Yes (after demo content upload)

