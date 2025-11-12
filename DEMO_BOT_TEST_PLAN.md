# Demo Bot Testing Checklist

Use this checklist to verify the demo bot implementation is working correctly.

## Pre-Testing Setup

- [ ] Environment variables set in `.env`:
  ```bash
  DEMO_BOT_TENANT_ID=00000000-0000-0000-0000-000000000000
  DEMO_BOT_ENABLED=true
  ```
- [ ] Migration run successfully: `docker-compose exec api alembic upgrade head`
- [ ] Demo tenant exists in database
- [ ] Demo bot exists in database
- [ ] Demo documents uploaded (3-5 PDFs about Weaver)
- [ ] Demo documents processed successfully (status = 'completed')
- [ ] Embeddings generated for demo documents

## Backend API Tests

### 1. Demo Bot Query (Non-Streaming)

**Test:** User can query demo bot with their API key

```bash
curl -X POST "http://localhost:8000/v1/tenants/00000000-0000-0000-0000-000000000000/query" \
  -H "Authorization: Bearer USER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Weaver?"}'
```

**Expected:**
- [ ] Status: 200 OK
- [ ] Response contains `answer`, `sources`, `confidence`, `latency_ms`
- [ ] `daily_usage.current` increments by 1
- [ ] `daily_usage.limit` is 50
- [ ] `daily_usage.remaining` decreases by 1

### 2. Demo Bot Query (Streaming)

**Test:** Streaming endpoint works for demo bot

```bash
curl -N "http://localhost:8000/v1/tenants/00000000-0000-0000-0000-000000000000/query/stream?query=What+is+Weaver" \
  -H "Authorization: Bearer USER_API_KEY" \
  -H "Accept: text/event-stream"
```

**Expected:**
- [ ] Status: 200 OK
- [ ] Content-Type: text/event-stream
- [ ] SSE events stream correctly
- [ ] `data: {"content": "..."}` events received
- [ ] Final event with sources and confidence
- [ ] `data: [DONE]` at the end

### 3. Access Control

**Test:** User cannot query another user's bot

```bash
curl -X POST "http://localhost:8000/v1/tenants/OTHER_USER_TENANT_ID/query" \
  -H "Authorization: Bearer USER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

**Expected:**
- [ ] Status: 403 Forbidden
- [ ] Error message: "Access denied. You can only query your own bot or the demo bot."

### 4. Daily Limit Tracking

**Test:** Demo bot queries count toward user's daily limit

```bash
# Query demo bot
curl -X POST "http://localhost:8000/v1/tenants/00000000-0000-0000-0000-000000000000/query" \
  -H "Authorization: Bearer USER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "test 1"}'

# Query user's own bot
curl -X POST "http://localhost:8000/v1/tenants/USER_TENANT_ID/query" \
  -H "Authorization: Bearer USER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "test 2"}'

# Check daily usage
curl "http://localhost:8000/v1/tenants/USER_TENANT_ID/usage/daily" \
  -H "Authorization: Bearer USER_SESSION_TOKEN"
```

**Expected:**
- [ ] Both queries count toward the same user daily limit
- [ ] `daily_usage.current` is 2 (or more if previous queries)
- [ ] Daily usage endpoint shows cumulative count

### 5. Disabled Demo Bot

**Test:** Demo bot is disabled when `DEMO_BOT_ENABLED=false`

```bash
# Set DEMO_BOT_ENABLED=false in .env
# Restart API: docker-compose restart api

curl -X POST "http://localhost:8000/v1/tenants/00000000-0000-0000-0000-000000000000/query" \
  -H "Authorization: Bearer USER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

**Expected:**
- [ ] Status: 403 Forbidden
- [ ] Demo bot queries blocked

## Frontend UI Tests

### 1. API Keys Tab - Endpoint Display

**Test:** Both demo and user bot endpoints are shown

- [ ] Navigate to Dashboard → API Keys tab
- [ ] See section "Available Bot Endpoints"
- [ ] Demo Bot card shows:
  - [ ] 🎯 Demo Bot label
  - [ ] "Ready to use" green badge
  - [ ] Correct endpoint URL with demo tenant ID
  - [ ] Description: "Try out Weaver with pre-loaded sample content"
- [ ] Your Bot card shows:
  - [ ] 📚 Your Bot label
  - [ ] "Upload docs first" gray badge (if no docs)
  - [ ] OR "Ready" green badge (if docs exist)
  - [ ] Correct endpoint URL with user's tenant ID
  - [ ] Appropriate description based on status

### 2. Code Examples

**Test:** Code examples show both demo and user bot

- [ ] Navigate to API Keys tab → Code examples
- [ ] **cURL tab:**
  - [ ] Non-streaming example shows demo bot query
  - [ ] Non-streaming example shows user bot query
  - [ ] Streaming example shows both bots
- [ ] **JavaScript tab:**
  - [ ] Shows demo bot example with `DEMO_BOT_ID`
  - [ ] Shows user bot example with placeholder
- [ ] **Python tab:**
  - [ ] Shows demo bot example
  - [ ] Shows user bot example

### 3. Test Panel - Bot Selector

**Test:** Bot selector works correctly

- [ ] Navigate to API Keys tab → Test Your Bot panel
- [ ] See bot selector with two buttons:
  - [ ] 🎯 Demo Bot
  - [ ] 📚 Your Bot
- [ ] Demo Bot button:
  - [ ] Always enabled
  - [ ] Selected by default (blue background)
- [ ] Your Bot button:
  - [ ] Disabled if no documents (gray, cursor-not-allowed)
  - [ ] Enabled if documents exist
  - [ ] Shows "(Upload docs first)" if disabled
  - [ ] Tooltip on hover explains why disabled

### 4. Test Panel - Info Banner

**Test:** Info banner shows for demo bot

- [ ] Select Demo Bot
- [ ] See yellow info banner appear
- [ ] Banner shows:
  - [ ] "Testing Demo Bot:" in bold
  - [ ] Explanation about pre-loaded content
  - [ ] Encouragement to upload own documents
- [ ] Select Your Bot (if enabled)
- [ ] Info banner disappears

### 5. Test Panel - Query Placeholder

**Test:** Placeholder text changes based on selected bot

- [ ] Select Demo Bot
- [ ] Query textarea placeholder: "Ask about Weaver..."
- [ ] Select Your Bot
- [ ] Query textarea placeholder: "Ask your bot a question..."

### 6. Test Panel - Querying Demo Bot

**Test:** Can query demo bot from test panel

- [ ] Select Demo Bot
- [ ] Paste API key
- [ ] Enter query: "What is Weaver?"
- [ ] Click "Run Test"
- [ ] See response stream in output area
- [ ] Response shows answer, confidence, sources

### 7. Test Panel - Querying Own Bot

**Test:** Can query own bot from test panel (if docs uploaded)

- [ ] Upload at least one document
- [ ] Wait for processing to complete
- [ ] Select Your Bot in test panel
- [ ] Enter query
- [ ] Click "Run Test"
- [ ] See response based on uploaded documents

### 8. Test Panel - Switching Between Bots

**Test:** Can switch between bots seamlessly

- [ ] Query demo bot
- [ ] See results
- [ ] Switch to Your Bot (if enabled)
- [ ] Query own bot
- [ ] See results
- [ ] Switch back to Demo Bot
- [ ] Query demo bot again
- [ ] All queries work correctly

## Edge Cases

### 1. No Documents in Demo Bot

**Test:** Graceful handling when demo bot has no documents

```bash
# If demo bot has no documents
curl -X POST "http://localhost:8000/v1/tenants/00000000-0000-0000-0000-000000000000/query" \
  -H "Authorization: Bearer USER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

**Expected:**
- [ ] Status: 200 OK
- [ ] Answer: "I don't know based on the available information."
- [ ] Confidence: "low"
- [ ] Sources: []

### 2. Invalid API Key

**Test:** Demo bot query fails with invalid key

```bash
curl -X POST "http://localhost:8000/v1/tenants/00000000-0000-0000-0000-000000000000/query" \
  -H "Authorization: Bearer INVALID_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

**Expected:**
- [ ] Status: 401 Unauthorized
- [ ] Error: "Missing API key" or "Invalid API key"

### 3. Daily Limit Exceeded

**Test:** Demo bot queries blocked when daily limit reached

```bash
# Make 50+ queries to reach daily limit
for i in {1..51}; do
  curl -X POST "http://localhost:8000/v1/tenants/00000000-0000-0000-0000-000000000000/query" \
    -H "Authorization: Bearer USER_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"test $i\"}"
done
```

**Expected:**
- [ ] First 50 queries: 200 OK
- [ ] 51st query: 429 Too Many Requests
- [ ] Error: "Daily query limit exceeded (50 queries/day). Resets at midnight UTC."

### 4. Redis Unavailable

**Test:** Demo bot works when Redis is down (graceful degradation)

```bash
# Stop Redis
docker-compose stop redis

# Query demo bot
curl -X POST "http://localhost:8000/v1/tenants/00000000-0000-0000-0000-000000000000/query" \
  -H "Authorization: Bearer USER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

**Expected:**
- [ ] Status: 200 OK (query still works)
- [ ] `daily_usage.redis_available` is `false`
- [ ] Warning logged in API logs
- [ ] Query proceeds without caching

## Database Verification

### 1. Check Demo Tenant

```bash
docker-compose exec api psql $DATABASE_URL -c "
  SELECT id, name, created_at 
  FROM tenants 
  WHERE id = '00000000-0000-0000-0000-000000000000';
"
```

**Expected:**
- [ ] 1 row returned
- [ ] Name: "Weaver Demo Bot"

### 2. Check Demo Bot

```bash
docker-compose exec api psql $DATABASE_URL -c "
  SELECT tenant_id, name, system_prompt 
  FROM bots 
  WHERE tenant_id = '00000000-0000-0000-0000-000000000000';
"
```

**Expected:**
- [ ] 1 row returned
- [ ] Name: "Demo Bot"
- [ ] System prompt mentions Weaver

### 3. Check Demo Documents

```bash
docker-compose exec api psql $DATABASE_URL -c "
  SELECT filename, status, size_bytes 
  FROM documents 
  WHERE tenant_id = '00000000-0000-0000-0000-000000000000';
"
```

**Expected:**
- [ ] 3-5 documents returned
- [ ] All status = 'completed'
- [ ] Reasonable file sizes

### 4. Check Demo Embeddings

```bash
docker-compose exec api psql $DATABASE_URL -c "
  SELECT COUNT(*) as chunk_count, COUNT(DISTINCT doc_id) as doc_count
  FROM doc_chunks 
  WHERE tenant_id = '00000000-0000-0000-0000-000000000000';
"
```

**Expected:**
- [ ] chunk_count > 0 (at least 50-100 chunks)
- [ ] doc_count matches number of processed documents

### 5. Check Query Logs

```bash
docker-compose exec api psql $DATABASE_URL -c "
  SELECT 
    api_key_id, 
    query, 
    confidence, 
    latency_ms,
    created_at
  FROM bot_queries 
  WHERE tenant_id = '00000000-0000-0000-0000-000000000000'
  ORDER BY created_at DESC 
  LIMIT 5;
"
```

**Expected:**
- [ ] Queries logged with demo tenant ID
- [ ] Various `api_key_id` values (different users)
- [ ] Reasonable latency values

## Performance Checks

### 1. Query Latency

**Test:** Demo bot queries perform well

- [ ] Average latency < 3 seconds
- [ ] 95th percentile < 5 seconds
- [ ] Cached queries < 500ms

### 2. Redis Cache Hits

**Test:** Demo bot queries are cached

```bash
# Check Redis stats
docker-compose exec redis redis-cli INFO stats | grep keyspace_hits

# Make duplicate query
curl -X POST "http://localhost:8000/v1/tenants/00000000-0000-0000-0000-000000000000/query" \
  -H "Authorization: Bearer USER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Weaver?"}'

# Check API logs
docker logs weaver-api-1 | grep "Cache HIT"
```

**Expected:**
- [ ] First query: Cache MISS
- [ ] Second query (within 5 min): Cache HIT
- [ ] Keyspace hits increase in Redis stats

## Monitoring

### 1. API Logs

**Check:** Logs show demo bot activity

```bash
docker logs weaver-api-1 | grep "00000000-0000-0000-0000-000000000000"
```

**Expected:**
- [ ] Query performance logs
- [ ] Retrieval breakdown logs
- [ ] Cache hit/miss logs

### 2. Database Metrics

**Check:** Query logs accumulate

```bash
docker-compose exec api psql $DATABASE_URL -c "
  SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_queries,
    AVG(latency_ms) as avg_latency,
    COUNT(DISTINCT api_key_id) as unique_users
  FROM bot_queries
  WHERE tenant_id = '00000000-0000-0000-0000-000000000000'
  GROUP BY DATE(created_at)
  ORDER BY date DESC
  LIMIT 7;
"
```

**Expected:**
- [ ] Daily query counts visible
- [ ] Multiple unique users
- [ ] Average latency reasonable

## Summary

- [ ] **All backend API tests passed**
- [ ] **All frontend UI tests passed**
- [ ] **All edge cases handled**
- [ ] **Database verification passed**
- [ ] **Performance checks passed**
- [ ] **Monitoring works**

## Notes

Document any issues or observations:

---

**Tested By:** ________________  
**Date:** ________________  
**Environment:** [ ] Local  [ ] Staging  [ ] Production  
**Status:** [ ] ✅ All Passed  [ ] ⚠️ Issues Found  [ ] ❌ Failed

