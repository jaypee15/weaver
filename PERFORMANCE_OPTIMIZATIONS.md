# Performance Optimizations

This document outlines all performance optimizations implemented to reduce query latency from ~10.9s to 1-3s.

## Summary of Changes

| Optimization | Expected Impact | Implementation Status |
|-------------|----------------|----------------------|
| Detailed timing logs | Diagnostic tool | ✅ Completed |
| Reduce TOP_K (8 → 3) | 30-40% faster retrieval | ✅ Completed |
| Faster LLM model (gemini-1.5-flash-8b) | 2-3x faster generation | ✅ Completed |
| Redis embedding cache | 200-500ms saved per query | ✅ Completed |
| Optimized HNSW index | 20-30% faster vector search | ✅ Completed |
| Query result caching | <100ms for repeated queries | ✅ Completed |
| Reduced chunk size (800 → 500) | 20-30% fewer tokens | ✅ Completed |
| Improved DB connection pooling | 50-100ms saved | ✅ Completed |
| Composite DB indexes | 30-50% faster filtering | ✅ Completed |

## Detailed Changes

### 1. Timing Logs (Diagnostic)

**Files Modified:**
- `backend/app/services/query.py`
- `backend/app/services/retrieval.py`

**What Changed:**
Added detailed performance logging to identify bottlenecks:
- Embedding generation time
- Vector search time
- LLM generation time
- Total query time

**How to Monitor:**
Check API logs for entries like:
```
Query performance - tenant:xxx | timings:{'retrieval_ms': 450, 'llm_ms': 2100, 'total_ms': 2600} | chunks:3
Retrieval breakdown - embedding:320ms | vector_search:130ms | top_k:3
```

### 2. Reduced TOP_K Results (8 → 3)

**Files Modified:**
- `backend/app/config.py`

**What Changed:**
```python
TOP_K_RESULTS: int = 3  # Reduced from 8
```

**Why:**
- Fewer chunks = faster vector search
- Fewer tokens for LLM to process
- Still provides sufficient context for most queries

**Trade-off:** Slightly less context for complex queries (can be overridden per-query if needed)

### 3. Faster LLM Model

**Files Modified:**
- `backend/app/services/llm.py`

**What Changed:**
```python
model="gemini-1.5-flash-8b"  # Changed from gemini-2.5-flash
```

**Why:**
- Flash-8B is 2-3x faster than standard Flash
- Optimized for speed with minimal quality loss
- Lower cost per token

**Trade-off:** Slightly less sophisticated responses for very complex queries

### 4. Redis Embedding Cache

**Files Modified:**
- `backend/app/services/embeddings.py`

**What Changed:**
- Added Redis caching layer for query embeddings
- Cache key: MD5 hash of query text
- TTL: 1 hour
- Graceful degradation if Redis unavailable

**Why:**
- Embedding generation takes 200-500ms
- Identical/similar queries reuse cached embeddings
- No quality loss (deterministic embeddings)

**Cache Hit Rate:** Expected 20-40% for typical FAQ-style queries

### 5. Optimized HNSW Index

**Files Modified:**
- `backend/alembic/versions/004_optimize_performance.py` (new migration)

**What Changed:**
```sql
CREATE INDEX idx_doc_chunks_embedding_hnsw 
ON doc_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 32, ef_construction = 128)  -- Increased from m=16, ef_construction=64
```

**Why:**
- Higher `m` = more connections per node = better recall
- Higher `ef_construction` = better index quality
- Trade-off: Slightly larger index size, but much faster search

**To Apply:**
```bash
cd backend
alembic upgrade head
```

### 6. Query Result Caching

**Files Modified:**
- `backend/app/services/query.py`

**What Changed:**
- Full query response caching in Redis
- Cache key: `query:{tenant_id}:{md5(query)}`
- TTL: 5 minutes
- Cached queries still logged for analytics

**Why:**
- Identical queries return instantly (<10ms)
- Great for repeated questions
- Reduces LLM API costs

**Cache Hit Rate:** Expected 10-30% depending on query patterns

### 7. Reduced Chunk Size

**Files Modified:**
- `backend/app/config.py`

**What Changed:**
```python
CHUNK_SIZE: int = 500  # Reduced from 800
CHUNK_OVERLAP_PCT: int = 10  # Reduced from 20
```

**Why:**
- Smaller chunks = fewer tokens for LLM
- Faster LLM processing
- More precise context retrieval

**Trade-off:** May need to re-chunk existing documents (run re-ingestion if needed)

### 8. Improved Database Connection Pooling

**Files Modified:**
- `backend/app/db/connection.py`

**What Changed:**
```python
pool_size=20,  # Increased from 10
max_overflow=40,  # Increased from 20
pool_recycle=3600,  # Recycle connections every hour
connect_args={
    "server_settings": {
        "jit": "off"  # Disable JIT for faster simple queries
    }
}
```

**Why:**
- Larger pool = fewer connection waits
- Pool recycling prevents stale connections
- JIT disabled for simple queries (faster execution)

### 9. Composite Database Indexes

**Files Modified:**
- `backend/alembic/versions/004_optimize_performance.py` (new migration)

**What Changed:**
```sql
CREATE INDEX idx_doc_chunks_tenant_embedding 
ON doc_chunks (tenant_id) 
INCLUDE (embedding, text, page_num, chunk_metadata)
```

**Why:**
- PostgreSQL can filter by tenant_id first, then do vector search
- Included columns avoid additional table lookups
- Much faster for multi-tenant scenarios

**To Apply:**
```bash
cd backend
alembic upgrade head
```

## Expected Performance Improvements

### Before Optimizations
- Average latency: **10,939ms** (~11 seconds)
- Breakdown (estimated):
  - Embedding: 300-500ms
  - Vector search: 200-400ms
  - LLM generation: 8,000-10,000ms (gemini-2.5-flash with 8 chunks)

### After Optimizations
- **First-time query:** 1,500-3,000ms (5-7x faster)
  - Embedding: 300-500ms (or <10ms if cached)
  - Vector search: 50-150ms (optimized index + fewer results)
  - LLM generation: 1,000-2,000ms (faster model + fewer tokens)

- **Cached query:** <100ms (100x faster)
  - Embedding: <10ms (Redis cache hit)
  - Vector search: 0ms (full result cached)
  - LLM generation: 0ms (full result cached)

### Cache Hit Rates (Estimated)
- Embedding cache: 20-40% (for similar/repeated queries)
- Full query cache: 10-30% (for identical queries)
- Combined improvement: 30-50% of queries will be significantly faster

## Monitoring & Tuning

### 1. Check Performance Logs
```bash
docker logs weaver-api-1 | grep "Query performance"
docker logs weaver-api-1 | grep "Retrieval breakdown"
docker logs weaver-api-1 | grep "Cache HIT"
```

### 2. Monitor Cache Hit Rates
```bash
# Connect to Redis
docker exec -it weaver-redis-1 redis-cli

# Check cache statistics
INFO stats

# Check cached keys
KEYS emb:*
KEYS query:*
```

### 3. Analyze Query Patterns
Check the analytics dashboard for:
- Average latency trends
- Query volume patterns
- Low-confidence queries (may need more context)

### 4. Fine-Tuning Options

If queries are still slow:

**A. Increase cache TTL** (if queries are repetitive)
```python
# backend/app/services/embeddings.py
self.cache_ttl = 7200  # 2 hours instead of 1

# backend/app/services/query.py
self.query_cache_ttl = 600  # 10 minutes instead of 5
```

**B. Adjust TOP_K** (if context is insufficient)
```python
# backend/app/config.py
TOP_K_RESULTS: int = 5  # Increase from 3 (more context, slower)
```

**C. Use faster model for simple queries** (already using fastest)
```python
# backend/app/services/llm.py
model="gemini-1.5-flash-8b"  # Already optimal
```

**D. Pre-warm cache** (for known common queries)
Create a script to pre-populate the cache with common questions.

## Migration Instructions

### 1. Apply Database Migrations
```bash
cd backend
alembic upgrade head
```

This will:
- Drop old HNSW index
- Create optimized HNSW index (m=32, ef_construction=128)
- Add composite index for tenant filtering
- Run ANALYZE for better query planning

### 2. Restart Services
```bash
docker-compose down
docker-compose up -d --build
```

### 3. Monitor Performance
```bash
# Watch API logs
docker logs -f weaver-api-1

# Make a test query and check timing logs
curl -X POST http://localhost:8000/v1/tenants/{tenant_id}/query \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is your product about?"}'
```

### 4. Optional: Re-chunk Documents
If you want to take advantage of the new chunk size (500 instead of 800):
```bash
# This would require a re-ingestion script (not implemented yet)
# For now, new documents will use the new chunk size
```

## Rollback Instructions

If you need to revert these changes:

### 1. Revert Database Migration
```bash
cd backend
alembic downgrade -1
```

### 2. Revert Code Changes
```bash
git revert <commit-hash>
```

### 3. Update Configuration
```python
# backend/app/config.py
TOP_K_RESULTS: int = 8
CHUNK_SIZE: int = 800
CHUNK_OVERLAP_PCT: int = 20

# backend/app/services/llm.py
model="gemini-2.5-flash"
```

## Cost Implications

### Reduced Costs
- **LLM API calls:** 30-50% reduction due to:
  - Fewer tokens per query (smaller chunks, fewer results)
  - Faster model (lower cost per token)
  - Query caching (10-30% of queries skip LLM entirely)

- **Embedding API calls:** 20-40% reduction due to:
  - Embedding caching

### Increased Costs
- **Redis memory:** Minimal (~10-50MB for typical workload)
- **Database storage:** Minimal (~5-10% increase for additional indexes)

**Net Impact:** 40-60% cost reduction for typical workloads

## Troubleshooting

### Issue: Cache not working
**Symptoms:** No "Cache HIT" logs, performance not improved

**Solution:**
1. Check Redis is running: `docker ps | grep redis`
2. Check Redis connection: `docker exec -it weaver-redis-1 redis-cli PING`
3. Check Redis URL in `.env`: `REDIS_URL=redis://redis:6379/0`

### Issue: Migration fails
**Symptoms:** `alembic upgrade head` errors

**Solution:**
1. Check database connection
2. Ensure pgvector extension is installed
3. Run migration with verbose output: `alembic upgrade head --sql`

### Issue: Queries still slow
**Symptoms:** Latency still >5s

**Solution:**
1. Check timing logs to identify bottleneck
2. Verify HNSW index was created: `\d+ doc_chunks` in psql
3. Check if LLM model changed: Look for "gemini-1.5-flash-8b" in logs
4. Monitor cache hit rates

## Next Steps

### Future Optimizations (Not Implemented)
1. **Hybrid search:** Combine vector search with keyword search
2. **Async LLM streaming:** Start streaming response before all chunks retrieved
3. **Query rewriting:** Optimize user queries before embedding
4. **Semantic caching:** Cache similar (not just identical) queries
5. **CDN for static responses:** Cache common answers at edge
6. **Database read replicas:** Separate read/write workloads
7. **Batch query processing:** Process multiple queries in parallel

### Monitoring Improvements
1. Add Prometheus metrics for cache hit rates
2. Add Grafana dashboard for performance visualization
3. Set up alerts for slow queries (>5s)
4. Track P50, P95, P99 latencies

## References

- [pgvector HNSW tuning](https://github.com/pgvector/pgvector#hnsw)
- [Gemini model comparison](https://ai.google.dev/gemini-api/docs/models/gemini)
- [Redis caching best practices](https://redis.io/docs/manual/patterns/)
- [PostgreSQL index optimization](https://www.postgresql.org/docs/current/indexes.html)

