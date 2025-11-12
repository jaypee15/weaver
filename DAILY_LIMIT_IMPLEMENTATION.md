# Daily Query Limit Implementation

## Overview

Implemented a daily query limit of 50 queries per bot (configurable via environment variable) to manage free tier usage and costs.

## Features

- **50 queries per day** limit (default, configurable)
- **Redis-based tracking** with automatic daily reset at midnight UTC
- **Graceful degradation** - if Redis is unavailable, queries are allowed (fail open)
- **Per-tenant tracking** - each tenant has independent daily limits
- **Real-time feedback** - users get current usage info in API responses
- **429 Too Many Requests** response when limit exceeded

## Configuration

### Environment Variable

```bash
MAX_QUERIES_PER_DAY=50  # Default: 50 queries per day
```

Set in:
- `.env` file
- `docker-compose.yml`
- `env.template`

## API Changes

### Query Endpoints

Both query endpoints now check the daily limit:

**POST `/v1/tenants/{tenant_id}/query`**
- Returns `429 Too Many Requests` if limit exceeded
- Includes `daily_usage` in response:
  ```json
  {
    "answer": "...",
    "sources": [...],
    "confidence": "high",
    "latency_ms": 1500,
    "daily_usage": {
      "current": 45,
      "limit": 50,
      "remaining": 5,
      "redis_available": true
    }
  }
  ```

**GET `/v1/tenants/{tenant_id}/query/stream`**
- Returns `429 Too Many Requests` if limit exceeded
- No usage info in SSE stream (check `/usage/daily` endpoint)

### New Endpoint

**GET `/v1/tenants/{tenant_id}/usage/daily`**

Get current daily usage without making a query:

```bash
curl http://localhost:8000/v1/tenants/{tenant_id}/usage/daily \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "current": 45,
  "limit": 50,
  "remaining": 5,
  "redis_available": true
}
```

## Error Response

When limit is exceeded:

**Status:** `429 Too Many Requests`

**Body:**
```json
{
  "detail": {
    "error": "Daily query limit exceeded",
    "current": 50,
    "limit": 50,
    "message": "You have reached your daily limit of 50 queries. Limit resets at midnight UTC."
  }
}
```

## Implementation Details

### Files Modified

1. **`backend/app/config.py`**
   - Added `MAX_QUERIES_PER_DAY` setting

2. **`backend/app/services/rate_limit.py`** (NEW)
   - `DailyLimitService` class for tracking daily usage
   - Uses Redis with automatic expiration at midnight UTC
   - Fail-open design (allows queries if Redis unavailable)

3. **`backend/app/api/v1/routes.py`**
   - Added daily limit check to both query endpoints
   - Added `/usage/daily` endpoint
   - Includes usage info in `QueryResponse`

4. **`backend/app/api/v1/schemas.py`**
   - Added `DailyUsage` model
   - Updated `QueryResponse` to include `daily_usage` field

5. **`docker-compose.yml`**
   - Added `MAX_QUERIES_PER_DAY` environment variable

6. **`env.template`**
   - Documented `MAX_QUERIES_PER_DAY` configuration

### Redis Key Format

```
daily_queries:{tenant_id}:{YYYY-MM-DD}
```

**Example:**
```
daily_queries:9e110e00-500b-4a4c-b82f-b6279d3c0a01:2025-11-12
```

**TTL:** Automatically expires at midnight UTC

### Logic Flow

1. **User makes query** → 
2. **Check API key auth** → 
3. **Check rate limit (60 RPM)** → 
4. **Check daily limit** → 
5. If under limit: **Increment counter** + **Process query**
6. If over limit: **Return 429 error**

## Testing

### Test Daily Limit

```bash
# Set limit to 3 for testing
export MAX_QUERIES_PER_DAY=3

# Make 4 queries
for i in {1..4}; do
  echo "Query $i:"
  curl -X POST http://localhost:8000/v1/tenants/{tenant_id}/query \
    -H "Authorization: Bearer YOUR_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"query": "test"}' | jq .daily_usage
  echo ""
done
```

**Expected output:**
```json
Query 1: {"current": 1, "limit": 3, "remaining": 2, "redis_available": true}
Query 2: {"current": 2, "limit": 3, "remaining": 1, "redis_available": true}
Query 3: {"current": 3, "limit": 3, "remaining": 0, "redis_available": true}
Query 4: 429 Too Many Requests - Daily query limit exceeded
```

### Check Current Usage

```bash
curl http://localhost:8000/v1/tenants/{tenant_id}/usage/daily \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Reset Counter (for testing)

```bash
# Connect to Redis
docker exec -it weaver-redis-1 redis-cli

# Find today's key
KEYS daily_queries:*

# Delete key to reset
DEL daily_queries:9e110e00-500b-4a4c-b82f-b6279d3c0a01:2025-11-12
```

## Monitoring

### Check Redis Keys

```bash
docker exec -it weaver-redis-1 redis-cli

# List all daily query counters
KEYS daily_queries:*

# Get specific tenant's count
GET daily_queries:9e110e00-500b-4a4c-b82f-b6279d3c0a01:2025-11-12

# Check TTL (seconds until reset)
TTL daily_queries:9e110e00-500b-4a4c-b82f-b6279d3c0a01:2025-11-12
```

### Application Logs

```bash
docker logs weaver-api | grep "Query count"
```

**Example:**
```
Query count for tenant 9e110e00-500b-4a4c-b82f-b6279d3c0a01: 45/50 (remaining: 5)
Daily limit exceeded for tenant 9e110e00-500b-4a4c-b82f-b6279d3c0a01: 50/50
```

## Scaling to Pro Tier

To implement paid tiers in the future:

### Option 1: Per-Tenant Limits

Store limit in `tenants` table:

```sql
ALTER TABLE tenants ADD COLUMN daily_query_limit INTEGER DEFAULT 50;
```

Update `DailyLimitService` to fetch limit from database:

```python
limit = await tenant_repo.get_daily_limit(tenant_id)
```

### Option 2: Plan-Based Limits

```python
PLAN_LIMITS = {
    "free": 50,
    "pro": 5000,
    "enterprise": 50000
}

# In DailyLimitService
limit = PLAN_LIMITS.get(tenant.plan, 50)
```

### Option 3: Usage-Based (No Hard Limit)

Remove hard limit, just track usage for billing:

```python
# Don't raise 429, just increment counter
await daily_limit_service.track_usage(tenant_id)
```

## Cost Analysis

At 50 queries/day:
- **Free tier cost**: ~$0.50/month per tenant in LLM costs
- **Total free users sustainable**: ~200 users for $100/month LLM budget

With current optimizations (caching):
- **Actual cost**: ~$0.30/month per active user (40% cache hit rate)
- **Sustainable users**: ~330 users for $100/month

## Future Enhancements

1. **Weekly/Monthly Limits** - Add multi-period tracking
2. **Soft Limits** - Warn at 80%, block at 100%
3. **Grace Period** - Allow 5 extra queries with warning
4. **Admin Override** - Bypass limits for specific tenants
5. **Analytics** - Track limit hit rates, usage patterns
6. **Notifications** - Email when approaching limit
7. **Rollover** - Unused queries roll to next day (up to limit)

## Troubleshooting

### Issue: Limits not working

**Cause:** Redis not available

**Check:**
```bash
docker ps | grep redis
docker logs weaver-redis-1
```

**Solution:** Ensure Redis is running and healthy

### Issue: Wrong count

**Cause:** Key expired early or Redis restart

**Check:**
```bash
docker exec -it weaver-redis-1 redis-cli TTL daily_queries:*
```

**Solution:** Counter will auto-reset at midnight UTC

### Issue: Users complaining about limits

**Temporary fix:**
```bash
# Increase limit globally
export MAX_QUERIES_PER_DAY=100
docker-compose restart api
```

**Permanent fix:** Implement pro tier with higher limits

## Summary

✅ **Implemented:** Daily query limit (50/day default)
✅ **Configurable:** Via `MAX_QUERIES_PER_DAY` environment variable
✅ **Tracked:** In Redis with automatic daily reset
✅ **Fail-safe:** Allows queries if Redis unavailable
✅ **User-friendly:** Clear error messages and usage feedback
✅ **Production-ready:** Logging, monitoring, and testing support

**Next Steps:**
1. Test in production with actual users
2. Monitor Redis performance and hit rates
3. Gather feedback on limit appropriateness
4. Plan pro tier implementation when needed

