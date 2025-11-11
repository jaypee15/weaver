# Database Migrations

## Overview

Weaver uses **idempotent SQL migrations** that can be run multiple times safely without causing errors or duplicating data.

## How Migrations Work

### Automatic Migrations

Migrations run automatically when the API container starts:

```bash
./start.sh  # Migrations run automatically
```

The entrypoint script:
1. Waits for PostgreSQL to be ready
2. Runs `/app/app/db/models.sql`
3. Exits if migration fails
4. Continues to start API if successful

### Manual Migrations

To run migrations manually:

```bash
# If services are running
docker-compose exec api psql -h postgres -U weaver -d weaver -f /app/app/db/models.sql

# Or connect directly to database
docker-compose exec postgres psql -U weaver -d weaver -f /path/to/models.sql
```

## Idempotency Features

All migration statements are idempotent:

### Extensions
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### Tables
```sql
CREATE TABLE IF NOT EXISTS tenants (...);
```

### Indexes
```sql
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);
```

### Functions
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column() ...
```

### Triggers
```sql
DROP TRIGGER IF EXISTS update_tenants_updated_at ON tenants;
CREATE TRIGGER update_tenants_updated_at ...
```

### Constraints
The `create_bot_for_tenant()` function uses:
```sql
INSERT INTO bots (...) VALUES (...)
ON CONFLICT (tenant_id) DO NOTHING;
```

## Safe to Run Multiple Times

You can safely run migrations:
- ✅ On first deployment
- ✅ After updates
- ✅ Multiple times in a row
- ✅ On existing databases
- ✅ In development and production

**No data loss or duplication will occur.**

## Migration Strategy

### Development
Migrations run automatically on every `./start.sh`

### Production
1. **Blue-Green Deployment**: Run migrations before switching traffic
2. **Rolling Updates**: Migrations are backward compatible
3. **Rollback**: Keep previous schema version for quick rollback

## Verifying Migrations

Check if migrations were applied:

```sql
-- Check extensions
SELECT * FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp');

-- Check tables
\dt

-- Check indexes
\di

-- Check triggers
SELECT tgname, tgrelid::regclass FROM pg_trigger WHERE tgname LIKE '%updated_at%';

-- Check functions
\df update_updated_at_column
\df create_bot_for_tenant
```

## Migration Logs

View migration logs:

```bash
# During startup
docker-compose logs -f api | grep -i migration

# Or check container logs
docker logs weaver-api 2>&1 | grep -i migration
```

## Troubleshooting

### "relation already exists"
This should not happen with idempotent migrations. If it does:
```sql
-- Check what exists
\dt
\di

-- Migrations should handle this automatically
```

### "permission denied"
Ensure the database user has proper permissions:
```sql
GRANT ALL PRIVILEGES ON DATABASE weaver TO weaver;
GRANT ALL ON SCHEMA public TO weaver;
```

### "could not create unique index"
This means duplicate data exists. Clean up before re-running:
```sql
-- Find duplicates
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;

-- Remove duplicates (carefully!)
-- Then re-run migrations
```

## Future Migrations

When adding new migrations:

1. **Always use idempotent statements**:
   - `CREATE TABLE IF NOT EXISTS`
   - `CREATE INDEX IF NOT EXISTS`
   - `CREATE OR REPLACE FUNCTION`
   - `DROP TRIGGER IF EXISTS` before `CREATE TRIGGER`

2. **Test idempotency**:
   ```bash
   # Run twice to ensure no errors
   psql -f migrations.sql
   psql -f migrations.sql
   ```

3. **Handle data migrations carefully**:
   ```sql
   -- Use WHERE NOT EXISTS for data inserts
   INSERT INTO table (col) 
   SELECT 'value' 
   WHERE NOT EXISTS (SELECT 1 FROM table WHERE col = 'value');
   ```

4. **Document breaking changes**:
   - Add to CHANGELOG.md
   - Update MIGRATION_GUIDE.md
   - Notify users

## Migration File Location

`/Users/macintosh/makermode/weaver/backend/app/db/models.sql`

This single file contains all schema definitions and is run on every deployment.

## Best Practices

1. ✅ Always use `IF NOT EXISTS` for tables and indexes
2. ✅ Always use `CREATE OR REPLACE` for functions
3. ✅ Always use `DROP IF EXISTS` before creating triggers
4. ✅ Use `ON CONFLICT DO NOTHING` for data inserts
5. ✅ Test migrations on a copy of production data
6. ✅ Keep migrations fast (< 1 second for most operations)
7. ✅ Document any manual steps required
8. ✅ Version control all migration files

## Schema Versioning

Currently using a single migration file. For future versions:

```
backend/app/db/
├── models.sql          # Current schema (idempotent)
├── migrations/
│   ├── 001_initial.sql
│   ├── 002_add_hnsw.sql
│   └── 003_add_analytics.sql
└── version.txt         # Track applied migrations
```

Consider migration tools like:
- Alembic (SQLAlchemy)
- Flyway
- Liquibase

For now, the single idempotent file works well for the MVP.

