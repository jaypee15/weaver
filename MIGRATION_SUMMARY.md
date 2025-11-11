# SQLAlchemy + Alembic Migration Summary

## What Was Changed

### ✅ Completed Migration from Raw SQL to SQLAlchemy ORM + Alembic

**Date**: November 6, 2025  
**Version**: 1.2.0

---

## Key Changes

### 1. **ORM Models Created** (`app/db/models.py`)

All database tables are now defined as SQLAlchemy ORM models:

- `Tenant` - Tenant metadata with relationships
- `User` - User accounts linked to tenants
- `Bot` - Bot configuration (1:1 with tenants)
- `Document` - Document metadata
- `DocumentChunk` - Text chunks with 1536-dim embeddings
- `APIKey` - Hashed API keys with rate limits
- `BotQuery` - Query logs for analytics

**Features**:
- Type-safe Python classes
- Automatic UUID generation
- Relationships between models (e.g., `tenant.docs`, `document.chunks`)
- Timestamps with `func.now()`
- HNSW vector index support

### 2. **Alembic Migration System**

**Structure**:
```
backend/
├── alembic/
│   ├── versions/
│   │   └── 001_initial_schema.py  # Initial migration
│   ├── env.py                      # Alembic environment
│   └── script.py.mako              # Migration template
├── alembic.ini                     # Alembic config
```

**Benefits**:
- ✅ Versioned migrations
- ✅ Auto-generation from model changes
- ✅ Rollback support
- ✅ Migration history tracking
- ✅ Idempotent by design

### 3. **Repositories Refactored**

All repositories now use ORM instead of raw SQL:

**Before**:
```python
result = await session.execute(
    "INSERT INTO api_keys (tenant_id, name) VALUES (:tid, :name)",
    {"tid": str(tenant_id), "name": name}
)
```

**After**:
```python
api_key = APIKey(tenant_id=tenant_id, name=name)
session.add(api_key)
await session.commit()
```

**Exception**: Vector similarity search still uses raw SQL (pgvector limitation).

### 4. **Entrypoint Updated**

**Before**: `psql -f models.sql`  
**After**: `alembic upgrade head`

Migrations now run automatically on container startup.

### 5. **Dependencies Updated**

Added to `requirements.txt`:
```
alembic==1.13.1
```

---

## Files Modified

| File | Change |
|------|--------|
| `app/db/models.py` | **Created** - ORM models |
| `app/db/repositories.py` | **Refactored** - ORM queries |
| `app/db/connection.py` | **Updated** - Added `init_db()` |
| `backend/entrypoint.sh` | **Updated** - Use Alembic |
| `alembic/` | **Created** - Migration system |
| `alembic.ini` | **Created** - Alembic config |
| `requirements.txt` | **Updated** - Added Alembic |
| `models.sql` | **Deprecated** - Renamed to `.deprecated` |

---

## Documentation Added

| Document | Purpose |
|----------|---------|
| `SQLALCHEMY_MIGRATION.md` | Complete guide to using Alembic |
| `MIGRATION_SUMMARY.md` | This file - quick overview |
| `CHANGELOG.md` | Updated with v1.2.0 changes |
| `README.md` | Updated with Alembic info |
| `ARCHITECTURE.md` | Updated with ORM details |
| `QUICKSTART.md` | Updated migration notes |

---

## How to Use

### Running Migrations

```bash
# Check current version
alembic current

# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Creating New Migrations

```bash
# 1. Edit models in app/db/models.py
vim app/db/models.py

# 2. Auto-generate migration
alembic revision --autogenerate -m "add new column"

# 3. Review generated migration
vim alembic/versions/XXX_add_new_column.py

# 4. Apply migration
alembic upgrade head
```

### Example: Adding a Column

```python
# 1. Update model
class Tenant(Base):
    # ... existing columns ...
    new_field = Column(String(100))

# 2. Generate migration
alembic revision --autogenerate -m "add new_field to tenants"

# 3. Apply
alembic upgrade head
```

---

## Benefits

### ✅ Advantages

1. **Type Safety**: Python type hints, IDE autocomplete
2. **Relationships**: Easy navigation (e.g., `tenant.docs`)
3. **Migrations**: Versioned, reversible
4. **Auto-generation**: Alembic detects changes
5. **Cleaner Code**: Less SQL string manipulation
6. **Testability**: Easier to mock and test
7. **Maintainability**: More Pythonic

### ⚠️ Considerations

1. **Learning Curve**: Need to understand SQLAlchemy
2. **Performance**: Minimal overhead with async
3. **Complex Queries**: Some still need raw SQL
4. **Vector Ops**: pgvector queries use raw SQL

---

## Migration Workflow

### Development

```bash
# 1. Make model changes
vim app/db/models.py

# 2. Generate migration
alembic revision --autogenerate -m "description"

# 3. Review migration
vim alembic/versions/XXX_description.py

# 4. Apply
alembic upgrade head

# 5. Test
./start.sh
```

### Production

```bash
# 1. Backup database
pg_dump weaver > backup.sql

# 2. Apply migrations
alembic upgrade head

# 3. Verify
alembic current
```

---

## Rollback Plan

If something goes wrong:

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision>

# Restore from backup
psql weaver < backup.sql
```

---

## Common Commands

```bash
# Show migration history
alembic history

# Show current version
alembic current

# Show SQL without executing
alembic upgrade head --sql

# Stamp current state (without running migrations)
alembic stamp head
```

---

## Testing

All existing functionality remains the same. The API and endpoints work identically.

**To test**:
```bash
# Start the platform
./start.sh

# Check migrations applied
docker-compose exec api alembic current

# Test API endpoints
curl http://localhost:8000/health
```

---

## Resources

- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [pgvector-python](https://github.com/pgvector/pgvector-python)
- Project: `SQLALCHEMY_MIGRATION.md` for detailed guide

---

## Questions?

See `SQLALCHEMY_MIGRATION.md` for:
- Detailed Alembic usage
- Troubleshooting
- Best practices
- Advanced scenarios
