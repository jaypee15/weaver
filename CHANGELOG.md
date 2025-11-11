# Changelog

All notable changes to the Weaver project will be documented in this file.

## [1.2.0] - 2025-11-06

### Changed
- **BREAKING**: Migrated from raw SQL to SQLAlchemy ORM + Alembic
  - All database operations now use SQLAlchemy ORM
  - Alembic for versioned database migrations
  - Type-safe models with relationships
  - Automatic migration generation
  - Rollback support

### Added
- SQLAlchemy ORM models for all tables
- Alembic migration system
- Initial migration (001_initial_schema.py)
- SQLALCHEMY_MIGRATION.md documentation
- `app/db/models.py` with full ORM definitions
- Alembic configuration and environment

### Removed
- Raw SQL in `models.sql` (replaced by Alembic migrations)
- Direct psql execution in entrypoint
- Raw SQL queries in repositories (now using ORM)

## [1.1.0] - 2025-11-06

### Changed
- **BREAKING**: Switched from IVFFlat to HNSW index for vector similarity search
  - Better accuracy and recall
  - HNSW parameters: m=16, ef_construction=64
  - Migration required for existing deployments
- **Simplified startup**: Single command deployment with `./start.sh`
  - Automatic database migrations on first run
  - All services containerized (API, Worker, Frontend)
  - Health checks and dependency management
  - No manual setup required
- **Idempotent migrations**: All SQL migrations can be run multiple times safely
  - Uses `CREATE TABLE IF NOT EXISTS`
  - Uses `CREATE INDEX IF NOT EXISTS`
  - Uses `CREATE OR REPLACE FUNCTION`
  - Uses `DROP TRIGGER IF EXISTS` before creating triggers
  - Safe to run on existing databases

### Added
- Automated entrypoint scripts for API and Worker containers
- Health check waiting in startup script
- Frontend Dockerfile for complete containerization
- Single `.env` file at root for all configuration
- `start.sh` - One-command startup script
- `stop.sh` - Clean shutdown script

### Improved
- Docker Compose configuration with proper networking
- Service dependencies and health checks
- Volume management for data persistence
- Development experience (no need for multiple terminals)

## [1.0.0] - 2025-11-06

### Added
- Initial release of Weaver platform
- FastAPI backend with async support
- Celery workers for document processing
- PostgreSQL with pgvector for embeddings
- LangChain-Gemini integration (embeddings + chat)
- Next.js frontend dashboard
- Supabase OAuth authentication
- API key management
- Document ingestion pipeline (PDF/DOCX/TXT/HTML)
- RAG query system with streaming support
- Rate limiting (60 rpm per key)
- Analytics APIs
- Prometheus metrics and Sentry integration
- Docker Compose for local development
- GCP Cloud Run deployment configuration
- GitHub Actions CI/CD pipeline
- Comprehensive documentation

### Features
- One-bot-per-tenant architecture
- Multi-format document support
- Text chunking (800 tokens, 20% overlap)
- Vector similarity search with pgvector
- Confidence scoring
- Source attribution
- Query logging and analytics
- Tenant isolation
- API key rotation and revocation

