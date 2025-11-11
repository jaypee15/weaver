# Migration Guide: IVFFlat to HNSW

If you're upgrading from version 1.0.0 to 1.1.0, you need to migrate your vector index from IVFFlat to HNSW.

## Why HNSW?

HNSW (Hierarchical Navigable Small World) provides:
- **Better accuracy**: Higher recall than IVFFlat
- **Consistent performance**: No need to tune `lists` parameter
- **Better for small-to-medium datasets**: Works well from day one
- **Simpler configuration**: Just two parameters (m, ef_construction)

## Migration Steps

### Option 1: Fresh Installation (Recommended for Development)

If you're in development with no critical data:

```bash
# Stop all services
./stop.sh

# Remove all data
docker-compose down -v

# Start fresh with new schema
./start.sh
```

The new HNSW index will be created automatically.

### Option 2: In-Place Migration (Production)

For production systems with existing data:

1. **Backup your database**:

```bash
docker-compose exec postgres pg_dump -U weaver weaver > backup.sql
```

2. **Stop the services**:

```bash
./stop.sh
```

3. **Start only the database**:

```bash
docker-compose up -d postgres
```

4. **Connect and migrate**:

```bash
docker-compose exec postgres psql -U weaver -d weaver
```

5. **Run migration SQL**:

```sql
-- Drop old IVFFlat index
DROP INDEX IF EXISTS idx_doc_chunks_embedding;

-- Create new HNSW index
CREATE INDEX idx_doc_chunks_embedding ON doc_chunks 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- Verify
\d doc_chunks
```

6. **Start all services**:

```bash
./start.sh
```

## HNSW Parameters Explained

- **m = 16**: Number of bi-directional links per node
  - Higher = better recall, more memory
  - 16 is a good balance for most use cases
  
- **ef_construction = 64**: Size of dynamic candidate list during construction
  - Higher = better index quality, slower build
  - 64 is recommended for production

## Performance Comparison

| Metric | IVFFlat (lists=100) | HNSW (m=16) |
|--------|---------------------|-------------|
| Recall@10 | ~85% | ~95% |
| Query Time | 10-50ms | 5-20ms |
| Build Time | Fast | Moderate |
| Memory | Low | Moderate |
| Tuning Required | Yes (lists) | Minimal |

## Rollback

If you need to rollback to IVFFlat:

```sql
DROP INDEX IF EXISTS idx_doc_chunks_embedding;

CREATE INDEX idx_doc_chunks_embedding ON doc_chunks 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
```

## Testing After Migration

1. **Verify index exists**:

```sql
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'doc_chunks' AND indexname = 'idx_doc_chunks_embedding';
```

2. **Test a query**:

```bash
curl -X POST http://localhost:8000/v1/tenants/YOUR_TENANT_ID/query \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'
```

3. **Check query performance**:

```sql
EXPLAIN ANALYZE
SELECT id, text, 1 - (embedding <=> '[0.1, 0.2, ...]'::vector) as similarity
FROM doc_chunks
WHERE tenant_id = 'YOUR_TENANT_ID'
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 8;
```

Look for "Index Scan using idx_doc_chunks_embedding" in the output.

## Support

If you encounter issues during migration:
1. Check the backup was created successfully
2. Review logs: `docker-compose logs -f api`
3. Open an issue with migration logs

