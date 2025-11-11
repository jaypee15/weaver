# SQLAlchemy + Alembic Migration Guide

## Overview

Weaver has been migrated from raw SQL to **SQLAlchemy ORM** with **Alembic** for database migrations.

## What Changed

### Before (Raw SQL)
- Single `models.sql` file with raw SQL
- Manual psql execution for migrations
- Raw SQL queries in repositories
- No migration versioning

### After (SQLAlchemy + Alembic)
- SQLAlchemy ORM models in `app/db/models.py`
- Alembic for versioned migrations
- ORM queries in repositories
- Full migration history and rollback support

## New Structure

```
backend/
├── alembic/
│   ├── versions/
│   │   └── 001_initial_schema.py
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
└── app/
    └── db/
        ├── models.py          # SQLAlchemy ORM models
        ├── connection.py      # Database connection
        └── repositories.py    # ORM-based repositories
```

## ORM Models

All tables are now defined as SQLAlchemy models:

```python
from app.db.models import Tenant, User, Bot, Document, DocumentChunk, APIKey, BotQuery
```

### Key Features:
- ✅ Relationships defined between models
- ✅ Automatic UUID generation
- ✅ Timestamps with `func.now()`
- ✅ Indexes and constraints
- ✅ HNSW vector index support
- ✅ Cascade deletes

## Using Alembic

### Running Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

### Creating New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description"

# Create empty migration
alembic revision -m "description"
```

### Example: Adding a New Column

1. Update the model in `app/db/models.py`:
```python
class Tenant(Base):
    # ... existing columns ...
    new_column = Column(String(100))
```

2. Generate migration:
```bash
alembic revision --autogenerate -m "add new_column to tenants"
```

3. Review and edit the generated migration in `alembic/versions/`

4. Apply migration:
```bash
alembic upgrade head
```

## Repository Changes

### Before (Raw SQL)
```python
async def create_key(self, tenant_id, name):
    result = await session.execute(
        """
        INSERT INTO api_keys (tenant_id, name, key_hash)
        VALUES (:tenant_id, :name, :key_hash)
        RETURNING id
        """,
        {"tenant_id": str(tenant_id), ...}
    )
```

### After (ORM)
```python
async def create_key(self, tenant_id, name):
    api_key = APIKey(
        tenant_id=tenant_id,
        name=name,
        key_hash=key_hash,
    )
    session.add(api_key)
    await session.commit()
    await session.refresh(api_key)
```

## Vector Search

Vector similarity search still uses raw SQL (pgvector doesn't have full SQLAlchemy support yet):

```python
from sqlalchemy import text

query = text("""
    SELECT id, text, 1 - (embedding <=> :query_embedding::vector) as similarity
    FROM doc_chunks
    WHERE tenant_id = :tenant_id
    ORDER BY embedding <=> :query_embedding::vector
    LIMIT :top_k
""")
```

## Benefits

### ✅ Advantages
- **Type Safety**: Python type hints and IDE autocomplete
- **Relationships**: Easy navigation between related objects
- **Migrations**: Versioned, reversible migrations
- **Auto-generation**: Alembic can detect model changes
- **Cleaner Code**: Less SQL string concatenation
- **Testability**: Easier to mock and test

### ⚠️ Considerations
- **Learning Curve**: Need to understand SQLAlchemy ORM
- **Performance**: ORM adds slight overhead (minimal with async)
- **Complex Queries**: Some queries still need raw SQL
- **Vector Operations**: pgvector queries use raw SQL

## Migration Workflow

### Development
```bash
# Make model changes
vim app/db/models.py

# Generate migration
alembic revision --autogenerate -m "description"

# Review migration
vim alembic/versions/XXX_description.py

# Apply migration
alembic upgrade head

# Test
./start.sh
```

### Production
```bash
# Backup database first!
pg_dump > backup.sql

# Apply migrations
alembic upgrade head

# Verify
alembic current
```

## Rollback

If something goes wrong:

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision>

# Rollback all
alembic downgrade base
```

## Common Tasks

### Check Current Migration Version
```bash
alembic current
```

### See Pending Migrations
```bash
alembic history
```

### Generate Migration from Model Changes
```bash
alembic revision --autogenerate -m "add new field"
```

### Apply All Pending Migrations
```bash
alembic upgrade head
```

### Create Empty Migration (for data migrations)
```bash
alembic revision -m "migrate data"
```

## Troubleshooting

### "Target database is not up to date"
```bash
alembic stamp head  # Mark current state as up-to-date
```

### "Can't locate revision"
```bash
# Check alembic_version table
psql -c "SELECT * FROM alembic_version"

# Reset if needed
alembic stamp base
alembic upgrade head
```

### "Relation already exists"
The migration tries to create something that exists. Either:
1. Drop the table/index manually
2. Edit the migration to use `IF NOT EXISTS`
3. Skip the migration: `alembic stamp head`

## Best Practices

1. **Always review auto-generated migrations** - Alembic isn't perfect
2. **Test migrations on a copy of production data** before deploying
3. **Keep migrations small and focused** - one logical change per migration
4. **Never edit applied migrations** - create a new migration instead
5. **Backup before migrating production** - always have a rollback plan
6. **Use transactions** - migrations run in transactions by default
7. **Document complex migrations** - add comments explaining why

## Resources

- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Alembic Docs](https://alembic.sqlalchemy.org/)
- [pgvector SQLAlchemy](https://github.com/pgvector/pgvector-python)

