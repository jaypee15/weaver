This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
.github/
  workflows/
    deploy-cloudrun-dockerhub.yml
backend/
  alembic/
    versions/
      001_initial_schema.py
      002_rename_users_to_profiles.py
      003_optimize_performance.py
      004_create_demo_bot.py
      004_performance_improvements.py
    env.py
    script.py.mako
  app/
    api/
      v1/
        analytics.py
        routes.py
        schemas.py
    auth/
      api_key.py
      oauth.py
      types.py
      utils.py
    db/
      connection.py
      models.py
      repositories.py
    middleware/
      rate_limit.py
    observability/
      logging.py
      metrics.py
    services/
      cache.py
      embeddings.py
      ingestion.py
      llm.py
      prompt_generator.py
      query.py
      rate_limit.py
      retrieval.py
      storage.py
    workers/
      db.py
      tasks.py
    config.py
    main.py
  tests/
    test_api.py
    test_chunking.py
    test_embeddings.py
  alembic.ini
  entrypoint.sh
  requirements.txt
demo_docs/
  faq.txt
  integration_examples.txt
  rag_guide.txt
  weaver_overview.txt
frontend/
  app/
    dashboard/
      page.tsx
  src/
    components/
      dashboard/
        AnalyticsTab.new.tsx
        AnalyticsTab.tsx
        APIKeysTab.tsx
        BotSettingsTab.tsx
        UploadTab.tsx
      ui/
        button.tsx
        card.tsx
        dialog.tsx
        input.tsx
        select.tsx
        skeleton.tsx
        sonner.tsx
        tabs.tsx
    hooks/
      useAnalytics.ts
      useAPIKeys.ts
      useBot.ts
      useDailyUsage.ts
      useDebounce.ts
      useDocuments.ts
    lib/
      axios.ts
      gtag.ts
      supabase.ts
      utils.ts
    pages/
      AuthCallback.tsx
      Dashboard.tsx
      Login.tsx
    store/
      authStore.ts
    types/
      index.ts
    App.tsx
    index.css
    main.tsx
    vite-env.d.ts
  .eslintrc.cjs
  .gitignore
  Dockerfile
  Dockerfile.dev
  index.html
  nginx.conf
  package.json
  postcss.config.js
  tailwind.config.js
  tsconfig.json
  tsconfig.node.json
  vite.config.ts
infra/
  deploy/
    cloudrun.yaml
  docker/
    Dockerfile
scripts/
  deploy.sh
  setup.sh
worker/
  celery.py
  entrypoint.sh
  health_server.py
.alembic_commands.md
.env.example
.gitignore
ARCHITECTURE.md
BOT_SETTINGS_QUICK_START.md
DEMO_BOT_ADMIN_IMPLEMENTATION.md
DEMO_BOT_ADMIN_SETUP.md
DEMO_BOT_IMPLEMENTATION.md
DEMO_BOT_SETUP.md
docker-compose.dev.yml
docker-compose.yml
env.template
QUICK_REFERENCE.md
QUICKSTART.md
README.md
START_HERE.md
start-dev.sh
start.sh
stop.sh
```

# Files

## File: backend/alembic/versions/002_rename_users_to_profiles.py
````python
"""rename users to profiles

Revision ID: 002
Revises: 001
Create Date: 2025-11-09

"""
from alembic import op
import sqlalchemy as sa


revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename users table to profiles
    op.rename_table('users', 'profiles')
    
    # Rename indexes
    op.execute('ALTER INDEX IF EXISTS idx_users_tenant_id RENAME TO idx_profiles_tenant_id')
    op.execute('ALTER INDEX IF EXISTS idx_users_email RENAME TO idx_profiles_email')


def downgrade() -> None:
    # Rename back to users
    op.rename_table('profiles', 'users')
    
    # Rename indexes back
    op.execute('ALTER INDEX IF EXISTS idx_profiles_tenant_id RENAME TO idx_users_tenant_id')
    op.execute('ALTER INDEX IF EXISTS idx_profiles_email RENAME TO idx_users_email')
````

## File: backend/alembic/versions/003_optimize_performance.py
````python
"""Optimize performance: improve HNSW index and add composite indexes

Revision ID: 003
Revises: 002
Create Date: 2025-11-12 02:52:15

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old HNSW index
    op.execute('DROP INDEX IF EXISTS idx_doc_chunks_embedding')
    
    # Create optimized HNSW index with better parameters
    op.execute('''
        CREATE INDEX idx_doc_chunks_embedding_hnsw 
        ON doc_chunks 
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 32, ef_construction = 128)
    ''')
    
    # Create composite index for tenant filtering
    # Note: Not including embedding in INCLUDE clause to avoid 8KB index row size limit
    op.execute('''
        CREATE INDEX IF NOT EXISTS idx_doc_chunks_tenant_id_only 
        ON doc_chunks (tenant_id)
    ''')
    
    # Update statistics for better query planning
    op.execute('ANALYZE doc_chunks')


def downgrade() -> None:
    # Drop optimized indexes
    op.execute('DROP INDEX IF EXISTS idx_doc_chunks_embedding_hnsw')
    op.execute('DROP INDEX IF EXISTS idx_doc_chunks_tenant_id_only')
    
    # Recreate original index
    op.execute('''
        CREATE INDEX idx_doc_chunks_embedding 
        ON doc_chunks 
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    ''')
````

## File: backend/alembic/versions/004_create_demo_bot.py
````python
"""Create demo bot tenant and admin user

Revision ID: 004
Revises: 003
Create Date: 2025-11-12 03:30:00

"""
from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create demo tenant
    op.execute("""
        INSERT INTO tenants (id, name, created_at, updated_at)
        VALUES (
            '00000000-0000-0000-0000-000000000000',
            'Weaver Demo Bot',
            NOW(),
            NOW()
        )
        ON CONFLICT (id) DO NOTHING
    """)
    
    # Create demo bot with custom system prompt
    # config_json stores per-bot customizations (system_prompt)
    # Global settings (temperature, top_k) remain in environment variables
    # Note: tenant trigger creates a bot automatically, so we update it instead
    op.execute("""
        INSERT INTO bots (id, tenant_id, name, config_json, created_at, updated_at)
        VALUES (
            '00000000-0000-0000-0000-000000000001',
            '00000000-0000-0000-0000-000000000000',
            'Demo Bot',
            '{"system_prompt": "You are the Weaver Demo Bot, an AI assistant that helps users learn about the Weaver platform. Your role is to explain how RAG (Retrieval-Augmented Generation) works, demonstrate best practices for building AI-powered knowledge bots, and encourage users to upload their own documents to create custom bots. Always be helpful, educational, and enthusiastic about the platform''s capabilities. When answering questions, cite the provided documentation and encourage exploration of Weaver''s features."}'::jsonb,
            NOW(),
            NOW()
        )
        ON CONFLICT (tenant_id) 
        DO UPDATE SET
            id = '00000000-0000-0000-0000-000000000001',
            name = 'Demo Bot',
            config_json = '{"system_prompt": "You are the Weaver Demo Bot, an AI assistant that helps users learn about the Weaver platform. Your role is to explain how RAG (Retrieval-Augmented Generation) works, demonstrate best practices for building AI-powered knowledge bots, and encourage users to upload their own documents to create custom bots. Always be helpful, educational, and enthusiastic about the platform''s capabilities. When answering questions, cite the provided documentation and encourage exploration of Weaver''s features."}'::jsonb,
            updated_at = NOW()
    """)
    
    # Create admin profile if DEMO_BOT_ADMIN_UUID is set
    # This UUID must match a Supabase auth.users.id
    admin_uuid = os.getenv('DEMO_BOT_ADMIN_UUID')
    admin_email = os.getenv('DEMO_BOT_ADMIN_EMAIL', 'admin@weaver.com')
    
    if admin_uuid:
        # Validate UUID format (basic check)
        try:
            import uuid
            uuid.UUID(admin_uuid)
            
            op.execute(f"""
                INSERT INTO profiles (id, tenant_id, email, role, created_at, updated_at)
                VALUES (
                    '{admin_uuid}',
                    '00000000-0000-0000-0000-000000000000',
                    '{admin_email}',
                    'owner',
                    NOW(),
                    NOW()
                )
                ON CONFLICT (id) DO NOTHING
            """)
            print(f"✓ Created admin profile for {admin_email} (UUID: {admin_uuid})")
        except ValueError:
            print(f"⚠ WARNING: Invalid DEMO_BOT_ADMIN_UUID format: {admin_uuid}. Skipping admin creation.")
    else:
        print("ℹ DEMO_BOT_ADMIN_UUID not set. Skipping admin profile creation.")
        print("  To create an admin later:")
        print("  1. Create user in Supabase Dashboard")
        print("  2. Set DEMO_BOT_ADMIN_UUID and DEMO_BOT_ADMIN_EMAIL")
        print("  3. Re-run migration or manually insert profile")


def downgrade() -> None:
    # Remove admin profile if it was created
    admin_uuid = os.getenv('DEMO_BOT_ADMIN_UUID')
    if admin_uuid:
        op.execute(f"DELETE FROM profiles WHERE id = '{admin_uuid}'")
    
    # Remove demo bot and tenant
    op.execute("DELETE FROM bots WHERE tenant_id = '00000000-0000-0000-0000-000000000000'")
    op.execute("DELETE FROM tenants WHERE id = '00000000-0000-0000-0000-000000000000'")
````

## File: backend/alembic/versions/004_performance_improvements.py
````python
"""performance improvements

Revision ID: 004_performance_improvements
Revises: 003_optimize_performance
Create Date: 2025-11-17

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_performance_improvements'
down_revision = '003_optimize_performance'
branch_labels = None
depends_on = None


def upgrade():
    # Add composite index for tenant-specific vector search
    # This helps when filtering by tenant_id before vector search
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_doc_chunks_tenant_embedding 
        ON doc_chunks 
        USING hnsw (embedding vector_cosine_ops) 
        WHERE tenant_id IS NOT NULL
    """)
    
    # Add index for created_at on bot_queries for faster analytics queries
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bot_queries_tenant_created 
        ON bot_queries (tenant_id, created_at DESC)
    """)


def downgrade():
    op.execute('DROP INDEX CONCURRENTLY IF EXISTS idx_doc_chunks_tenant_embedding')
    op.execute('DROP INDEX CONCURRENTLY IF EXISTS idx_bot_queries_tenant_created')
````

## File: backend/alembic/env.py
````python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.config import settings
from app.db.connection import Base
from app.db.models import *

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Convert async database URL to sync for migrations
sync_url = settings.DATABASE_URL.replace('+asyncpg', '').replace('postgresql+asyncpg', 'postgresql')
config.set_main_option('sqlalchemy.url', sync_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
````

## File: backend/alembic/script.py.mako
````
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
````

## File: backend/app/api/v1/analytics.py
````python
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.auth.oauth import get_current_user, User
from app.db.repositories import AnalyticsRepository

router = APIRouter()


@router.get("/tenants/{tenant_id}/analytics/queries")
async def get_query_analytics(
    tenant_id: UUID,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: User = Depends(get_current_user),
):
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    analytics_repo = AnalyticsRepository()
    
    if start_date:
        start = datetime.fromisoformat(start_date)
    else:
        start = datetime.now() - timedelta(days=30)
    
    if end_date:
        end = datetime.fromisoformat(end_date)
    else:
        end = datetime.now()
    
    data = await analytics_repo.get_query_stats(tenant_id, start, end)
    
    return data


@router.get("/tenants/{tenant_id}/analytics/top-queries")
async def get_top_queries(
    tenant_id: UUID,
    limit: int = 10,
    user: User = Depends(get_current_user),
):
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    analytics_repo = AnalyticsRepository()
    top_queries = await analytics_repo.get_top_queries(tenant_id, limit)
    
    return {"queries": top_queries}


@router.get("/tenants/{tenant_id}/analytics/unanswered")
async def get_unanswered_queries(
    tenant_id: UUID,
    limit: int = 20,
    user: User = Depends(get_current_user),
):
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    analytics_repo = AnalyticsRepository()
    unanswered = await analytics_repo.get_unanswered_queries(tenant_id, limit)
    
    return {"queries": unanswered}
````

## File: backend/app/auth/api_key.py
````python
import secrets
from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, Header, Depends
from pydantic import BaseModel

from app.auth.utils import verify_key_hash
from app.auth.types import APIKeyData
from app.db.repositories import APIKeyRepository


async def verify_api_key(
    authorization: Optional[str] = Header(None),
) -> APIKeyData:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    api_key = authorization.replace("Bearer ", "")
    
    if not api_key.startswith("wvr_"):
        raise HTTPException(status_code=401, detail="Invalid API key format")
    
    api_key_repo = APIKeyRepository()
    key_data = await api_key_repo.verify_key(api_key)
    
    if not key_data:
        raise HTTPException(status_code=401, detail="Invalid or revoked API key")
    
    await api_key_repo.update_last_used(key_data.key_id)
    
    return key_data
````

## File: backend/app/auth/oauth.py
````python
from typing import Optional
from uuid import UUID
from fastapi import HTTPException, Header, Depends
from pydantic import BaseModel
from supabase import create_client, Client

from app.config import settings
from app.db.repositories import ProfileRepository


class User(BaseModel):
    id: UUID
    email: str
    tenant_id: UUID
    role: str


def get_supabase_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


async def verify_supabase_token(
    authorization: Optional[str] = Header(None),
) -> dict:
    """Verify Supabase JWT token without database lookup - for signup flow"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization token")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        supabase = get_supabase_client()
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {
            "id": UUID(user_response.user.id),
            "email": user_response.user.email
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> User:
    """Get current user with tenant mapping from our database"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization token")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        supabase = get_supabase_client()
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = user_response.user.id
        email = user_response.user.email
        
        # Look up user's tenant mapping in our application database
        profile_repo = ProfileRepository()
        app_user = await profile_repo.get_by_id(UUID(user_id))
        
        if not app_user:
            # User authenticated with Supabase but not set up in our app yet
            raise HTTPException(
                status_code=404, 
                detail="User not found in application. Please complete signup."
            )

        return User(
            id=UUID(user_id),
            email=email,
            tenant_id=app_user["tenant_id"],
            role=app_user["role"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


def require_admin_or_owner(user: User, tenant_id: UUID) -> None:
    """
    Check if user has admin or owner role and belongs to the tenant.
    Raises HTTPException if not authorized.
    """
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    if user.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Admin or owner access required")
````

## File: backend/app/auth/types.py
````python
from pydantic import BaseModel
from uuid import UUID


class APIKeyData(BaseModel):
    key_id: UUID
    tenant_id: UUID
    rate_limit_rpm: int
````

## File: backend/app/auth/utils.py
````python
"""Authentication utility functions"""
import secrets
from passlib.hash import argon2


def generate_api_key() -> str:
    """Generate a new API key with 'wvr_' prefix"""
    return f"wvr_{secrets.token_urlsafe(48)}"


def hash_api_key(key: str) -> str:
    """Hash an API key using Argon2"""
    return argon2.hash(key)


def verify_key_hash(key: str, key_hash: str) -> bool:
    """Verify an API key against its hash"""
    try:
        return argon2.verify(key, key_hash)
    except Exception:
        return False
````

## File: backend/app/db/models.py
````python
from sqlalchemy import Column, String, Integer, BigInteger, Boolean, Text, TIMESTAMP, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid

from app.db.connection import Base


class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    plan_tier = Column(String(50), default='free')
    storage_used_bytes = Column(BigInteger, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    users = relationship("Profile", back_populates="tenant", cascade="all, delete-orphan")
    bots = relationship("Bot", back_populates="tenant", cascade="all, delete-orphan", uselist=False)
    docs = relationship("Document", back_populates="tenant", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="tenant", cascade="all, delete-orphan")
    bot_queries = relationship("BotQuery", back_populates="tenant", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"
    
    # Primary key is Supabase auth.users.id (provided by Supabase Auth)
    id = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    role = Column(String(50), default='member')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    tenant = relationship("Tenant", back_populates="users")
    
    __table_args__ = (
        Index('idx_profiles_tenant_id', 'tenant_id'),
        Index('idx_profiles_email', 'email'),
    )


class Bot(Base):
    __tablename__ = "bots"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    config_json = Column(JSONB, default={})
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    tenant = relationship("Tenant", back_populates="bots")
    
    __table_args__ = (
        UniqueConstraint('tenant_id', name='bots_tenant_id_unique'),
        Index('idx_bots_tenant_id', 'tenant_id'),
    )


class Document(Base):
    __tablename__ = "docs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    filename = Column(String(500), nullable=False)
    gcs_path = Column(String(1000), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    status = Column(String(50), default='pending')
    error_message = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    tenant = relationship("Tenant", back_populates="docs")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_docs_tenant_id', 'tenant_id'),
        Index('idx_docs_status', 'status'),
    )


class DocumentChunk(Base):
    __tablename__ = "doc_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_id = Column(UUID(as_uuid=True), ForeignKey('docs.id', ondelete='CASCADE'), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    embedding = Column(Vector(1536))
    text = Column(Text, nullable=False)
    page_num = Column(Integer)
    chunk_index = Column(Integer, nullable=False)
    chunk_metadata = Column(JSONB, default={})
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    document = relationship("Document", back_populates="chunks")
    tenant = relationship("Tenant")
    
    __table_args__ = (
        Index('idx_doc_chunks_doc_id', 'doc_id'),
        Index('idx_doc_chunks_tenant_id', 'tenant_id'),
        Index('idx_doc_chunks_embedding', 'embedding', postgresql_using='hnsw',
              postgresql_with={'m': 16, 'ef_construction': 64},
              postgresql_ops={'embedding': 'vector_cosine_ops'}),
    )


class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255))
    key_hash = Column(String(255), nullable=False)
    rate_limit_rpm = Column(Integer, default=60)
    revoked = Column(Boolean, default=False)
    last_used_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    tenant = relationship("Tenant", back_populates="api_keys")
    bot_queries = relationship("BotQuery", back_populates="api_key")
    
    __table_args__ = (
        Index('idx_api_keys_tenant_id', 'tenant_id'),
        Index('idx_api_keys_revoked', 'revoked'),
    )


class BotQuery(Base):
    __tablename__ = "bot_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    api_key_id = Column(UUID(as_uuid=True), ForeignKey('api_keys.id', ondelete='SET NULL'))
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    confidence = Column(String(50))
    latency_ms = Column(Integer)
    sources = Column(JSONB, default=[])
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant", back_populates="bot_queries")
    api_key = relationship("APIKey", back_populates="bot_queries")
    
    __table_args__ = (
        Index('idx_bot_queries_tenant_id', 'tenant_id'),
        Index('idx_bot_queries_api_key_id', 'api_key_id'),
        Index('idx_bot_queries_created_at', 'created_at'),
        Index('idx_bot_queries_confidence', 'confidence'),
    )
````

## File: backend/app/middleware/rate_limit.py
````python
import time
from fastapi import HTTPException
import redis.asyncio as redis

from app.config import settings
from app.auth.types import APIKeyData

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def check_rate_limit(api_key_data: APIKeyData):
    key = f"rate_limit:{api_key_data.tenant_id}:{api_key_data.key_id}"
    window = 60
    limit = api_key_data.rate_limit_rpm
    
    current_time = int(time.time())
    window_start = current_time - window
    
    pipe = redis_client.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zcard(key)
    pipe.zadd(key, {str(current_time): current_time})
    pipe.expire(key, window + 1)
    
    results = await pipe.execute()
    request_count = results[1]
    
    if request_count >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {limit} requests per minute.",
        )
````

## File: backend/app/observability/logging.py
````python
import logging
import sys
from app.config import settings


def setup_logging():
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(module)s"}',
        handlers=[logging.StreamHandler(sys.stdout)],
    )
````

## File: backend/app/observability/metrics.py
````python
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
from fastapi import FastAPI

query_counter = Counter(
    "weaver_queries_total",
    "Total number of queries",
    ["tenant_id", "confidence"],
)

query_latency = Histogram(
    "weaver_query_latency_seconds",
    "Query latency in seconds",
    ["tenant_id"],
)

ingestion_counter = Counter(
    "weaver_ingestion_total",
    "Total number of ingestion jobs",
    ["tenant_id", "status"],
)

active_tenants = Gauge(
    "weaver_active_tenants",
    "Number of active tenants",
)

api_errors = Counter(
    "weaver_api_errors_total",
    "Total API errors",
    ["endpoint", "status_code"],
)


def setup_metrics(app: FastAPI):
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
````

## File: backend/app/services/prompt_generator.py
````python
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings


class PromptGeneratorService:
    """Generates optimal system prompts from business information using LLM"""
    
    def __init__(self):
        # Use fast model for prompt generation
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.7,  # Slightly higher for creativity
        )
    
    async def generate_from_business_info(
        self,
        business_name: str,
        industry: str,
        description: str,
        tone: str,
        primary_goal: str,
        special_instructions: Optional[str] = None,
    ) -> str:
        """Generate a system prompt tailored to the business"""
        
        # Map tone to specific instructions
        tone_guidelines = {
            "professional": "professional, polished, and business-appropriate",
            "friendly": "warm, conversational, and approachable",
            "technical": "precise, detailed, and technically accurate",
            "casual": "relaxed, informal, and easy-going",
            "formal": "formal, academic, and authoritative",
        }
        
        tone_description = tone_guidelines.get(tone, "professional")
        
        # Meta-prompt for generating the system prompt
        meta_prompt = f"""You are an expert at writing system prompts for AI chatbots. 

Given the following business information, create an optimal system prompt that will guide an AI assistant to respond perfectly for this business.

**Business Information:**
- Business Name: {business_name}
- Industry: {industry}
- What they do: {description}
- Desired Tone: {tone_description}
- Primary Goal: {primary_goal}
{f"- Special Instructions: {special_instructions}" if special_instructions else ""}

**Requirements for the system prompt:**
1. Define the AI's role clearly (e.g., "You are {business_name}'s AI assistant")
2. Specify the tone: {tone_description}
3. Explain the primary goal: {primary_goal}
4. Include guidelines for answering based on provided context
5. Specify how to handle questions without sufficient context
6. Include any relevant disclaimers or limitations
7. Encourage citing sources when appropriate
{f"8. Incorporate these special instructions: {special_instructions}" if special_instructions else ""}

**Output Format:**
Write ONLY the system prompt itself (2-4 paragraphs), ready to be used directly. Do not include any meta-commentary, explanations, or markdown formatting. Start with "You are..." and write in second person.

Generate the system prompt now:"""

        messages = [
            SystemMessage(content="You are an expert system prompt engineer. You write clear, effective prompts that guide AI assistants to behave optimally for specific businesses."),
            HumanMessage(content=meta_prompt),
        ]
        
        response = await self.llm.ainvoke(messages)
        system_prompt = response.content.strip()
        
        # Clean up any markdown or extra formatting
        system_prompt = system_prompt.replace("```", "").strip()
        
        return system_prompt
````

## File: backend/app/services/rate_limit.py
````python
"""
Daily query limit tracking service
"""
import logging
from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException, status

from app.services.cache import cache_service
from app.config import settings

logger = logging.getLogger(__name__)


class DailyLimitService:
    """Track and enforce daily query limits per tenant"""
    
    @staticmethod
    def _get_daily_key(tenant_id: UUID) -> str:
        """Generate Redis key for daily query count"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return f"daily_queries:{tenant_id}:{today}"
    
    @staticmethod
    async def check_and_increment(tenant_id: UUID) -> dict:
        """
        Check if tenant is within daily limit and increment counter.
        Returns dict with current count and limit info.
        Raises HTTPException if limit exceeded.
        """
        if not cache_service.is_available:
            # If Redis unavailable, allow queries (fail open)
            logger.warning("Redis unavailable, skipping daily limit check")
            return {
                "current": 0,
                "limit": settings.MAX_QUERIES_PER_DAY,
                "remaining": settings.MAX_QUERIES_PER_DAY,
                "redis_available": False
            }
        
        key = DailyLimitService._get_daily_key(tenant_id)
        
        try:
            # Get current count
            current_count = cache_service._redis_client.get(key)
            current = int(current_count) if current_count else 0
            
            # Check if limit exceeded
            if current >= settings.MAX_QUERIES_PER_DAY:
                logger.warning(f"Daily limit exceeded for tenant {tenant_id}: {current}/{settings.MAX_QUERIES_PER_DAY}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Daily query limit exceeded",
                        "current": current,
                        "limit": settings.MAX_QUERIES_PER_DAY,
                        "message": f"You have reached your daily limit of {settings.MAX_QUERIES_PER_DAY} queries. Limit resets at midnight UTC."
                    }
                )
            
            # Increment counter
            new_count = cache_service._redis_client.incr(key)
            
            # Set expiry to end of day (if this is the first increment)
            if new_count == 1:
                # Calculate seconds until midnight UTC
                now = datetime.now(timezone.utc)
                tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0)
                tomorrow = tomorrow.replace(day=tomorrow.day + 1)
                seconds_until_midnight = int((tomorrow - now).total_seconds())
                cache_service._redis_client.expire(key, seconds_until_midnight)
            
            remaining = settings.MAX_QUERIES_PER_DAY - new_count
            
            logger.info(f"Query count for tenant {tenant_id}: {new_count}/{settings.MAX_QUERIES_PER_DAY} (remaining: {remaining})")
            
            return {
                "current": new_count,
                "limit": settings.MAX_QUERIES_PER_DAY,
                "remaining": max(0, remaining),
                "redis_available": True
            }
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log error but allow query (fail open)
            logger.error(f"Error checking daily limit for tenant {tenant_id}: {e}")
            return {
                "current": 0,
                "limit": settings.MAX_QUERIES_PER_DAY,
                "remaining": settings.MAX_QUERIES_PER_DAY,
                "redis_available": False,
                "error": str(e)
            }
    
    @staticmethod
    async def get_current_usage(tenant_id: UUID) -> dict:
        """Get current daily usage without incrementing"""
        if not cache_service.is_available:
            return {
                "current": 0,
                "limit": settings.MAX_QUERIES_PER_DAY,
                "remaining": settings.MAX_QUERIES_PER_DAY,
                "redis_available": False
            }
        
        key = DailyLimitService._get_daily_key(tenant_id)
        
        try:
            current_count = cache_service._redis_client.get(key)
            current = int(current_count) if current_count else 0
            remaining = max(0, settings.MAX_QUERIES_PER_DAY - current)
            
            return {
                "current": current,
                "limit": settings.MAX_QUERIES_PER_DAY,
                "remaining": remaining,
                "redis_available": True
            }
        except Exception as e:
            logger.error(f"Error getting daily usage for tenant {tenant_id}: {e}")
            return {
                "current": 0,
                "limit": settings.MAX_QUERIES_PER_DAY,
                "remaining": settings.MAX_QUERIES_PER_DAY,
                "redis_available": False,
                "error": str(e)
            }


# Singleton instance
daily_limit_service = DailyLimitService()
````

## File: backend/app/services/storage.py
````python
"""
Google Cloud Storage service using S3-compatible API with HMAC keys
"""
import boto3
from botocore.exceptions import ClientError
from app.config import settings


class StorageService:
    """Singleton-like storage service for GCS operations"""
    
    _client = None
    
    @classmethod
    def get_client(cls):
        """Get or create boto3 S3 client for GCS"""
        if cls._client is None:
            cls._client = boto3.client(
                's3',
                endpoint_url='https://storage.googleapis.com',
                aws_access_key_id=settings.GCS_ACCESS_KEY,
                aws_secret_access_key=settings.GCS_SECRET_KEY,
                region_name='auto'
            )
        return cls._client
    
    @classmethod
    def upload_file(cls, bucket_name: str, key: str, content: bytes, content_type: str = None) -> None:
        """Upload a file to GCS"""
        try:
            client = cls.get_client()
            client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=content,
                ContentType=content_type or 'application/octet-stream'
            )
        except ClientError as e:
            raise ValueError(f"Failed to upload to GCS: {str(e)}")
    
    @classmethod
    def download_file(cls, bucket_name: str, key: str) -> bytes:
        """Download a file from GCS"""
        try:
            client = cls.get_client()
            response = client.get_object(Bucket=bucket_name, Key=key)
            return response['Body'].read()
        except ClientError as e:
            raise ValueError(f"Failed to download from GCS: {str(e)}")
    
    @classmethod
    def delete_file(cls, bucket_name: str, key: str) -> None:
        """Delete a file from GCS"""
        try:
            client = cls.get_client()
            client.delete_object(Bucket=bucket_name, Key=key)
        except ClientError as e:
            raise ValueError(f"Failed to delete from GCS: {str(e)}")
````

## File: backend/app/main.py
````python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.config import settings
from app.api.v1 import routes
from app.observability.metrics import setup_metrics
from app.observability.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            integrations=[FastApiIntegration()],
            traces_sample_rate=0.1,
        )
    yield


app = FastAPI(
    title="Weaver API",
    description="AI-Powered Knowledge Bot Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_metrics(app)

app.include_router(routes.router, prefix="/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
````

## File: backend/tests/test_api.py
````python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_query_without_auth():
    response = client.post(
        "/v1/tenants/00000000-0000-0000-0000-000000000000/query",
        json={"query": "test"}
    )
    assert response.status_code == 401


def test_invalid_api_key():
    response = client.post(
        "/v1/tenants/00000000-0000-0000-0000-000000000000/query",
        json={"query": "test"},
        headers={"Authorization": "Bearer invalid_key"}
    )
    assert response.status_code == 401
````

## File: backend/tests/test_chunking.py
````python
from app.workers.tasks import chunk_text


def test_chunk_text():
    text = " ".join([f"word{i}" for i in range(1000)])
    
    chunks = chunk_text(text, chunk_size=100, overlap_pct=20)
    
    assert len(chunks) > 1
    assert all(isinstance(chunk, str) for chunk in chunks)
    
    first_chunk_words = chunks[0].split()
    second_chunk_words = chunks[1].split()
    
    assert len(first_chunk_words) == 100
    
    overlap_words = set(first_chunk_words[-20:]) & set(second_chunk_words[:20])
    assert len(overlap_words) > 0


def test_chunk_text_small():
    text = "This is a small text"
    
    chunks = chunk_text(text, chunk_size=100, overlap_pct=20)
    
    assert len(chunks) == 1
    assert chunks[0] == text
````

## File: backend/tests/test_embeddings.py
````python
import pytest
from app.services.embeddings import EmbeddingService


@pytest.mark.asyncio
async def test_embed_text():
    service = EmbeddingService()
    
    text = "This is a test document about password reset procedures."
    embedding = await service.embed_text(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == 1536
    assert all(isinstance(x, float) for x in embedding)


@pytest.mark.asyncio
async def test_embed_documents():
    service = EmbeddingService()
    
    texts = [
        "First document about authentication.",
        "Second document about authorization.",
    ]
    embeddings = await service.embed_documents(texts)
    
    assert len(embeddings) == 2
    assert all(len(emb) == 1536 for emb in embeddings)
````

## File: backend/alembic.ini
````
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = 

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
````

## File: backend/entrypoint.sh
````bash
#!/bin/bash
set -e

echo "🚀 Starting Weaver Backend..."

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "📊 Running database migrations with Alembic..."
    alembic upgrade head
    
    if [ $? -eq 0 ]; then
        echo "✅ Migrations applied successfully"
    else
        echo "❌ Migration failed!"
        exit 1
    fi
    
    echo "✅ Migrations complete!"
fi

echo "🌐 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
````

## File: backend/requirements.txt
````
fastapi==0.121.0
uvicorn[standard]==0.38.0
python-multipart==0.0.20
pydantic==2.12.4
pydantic-settings==2.11.0

langchain==1.0.4
langchain-google-genai==3.0.1
langchain-community==0.4.1

psycopg2-binary==2.9.11
asyncpg==0.30.0
pgvector==0.4.1
sqlalchemy==2.0.44
alembic==1.17.1

celery==5.5.2
redis==7.0.1

boto3==1.35.94
botocore==1.35.94

PyMuPDF==1.23.21
python-docx==1.2.0
html2text==2025.4.15

supabase==2.24.0

passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.5.0
argon2-cffi==25.1.0

prometheus-client==0.23.1
sentry-sdk[fastapi]==2.43.0

python-dotenv==1.2.1
````

## File: demo_docs/faq.txt
````
# Weaver Frequently Asked Questions (FAQ)

## General Questions

### What is Weaver?

Weaver is an AI-powered platform that transforms your documents into intelligent chatbots. Upload your PDFs, DOCX files, or other documents, and Weaver creates a bot that can answer questions based on that content using advanced RAG (Retrieval-Augmented Generation) technology.

### How is Weaver different from ChatGPT?

While ChatGPT is a general-purpose AI trained on internet data, Weaver creates bots trained specifically on YOUR documents. This means:
- Answers come from your content, not the internet
- No hallucinations or made-up information
- Every answer cites the source document
- You control what knowledge the bot has
- Perfect for business-specific information

### Do I need coding experience to use Weaver?

No! Weaver is designed for non-technical users. Our dashboard provides:
- Drag-and-drop document upload
- Visual bot configuration with AI-generated prompts
- Point-and-click API key management
- Built-in test interface

Developers can use our REST API for advanced integrations.

### What document formats are supported?

Weaver supports:
- PDF (.pdf)
- Microsoft Word (.docx)
- Plain text (.txt)
- HTML (.html)

More formats coming soon (PowerPoint, Excel, Markdown).

### Is there a free tier?

Yes! The free tier includes:
- 50 queries per day
- 10 documents maximum
- 100 MB storage
- Email support
- Full API access

## Getting Started

### How do I create my first bot?

1. Sign up at weaver.com using Google OAuth
2. Upload your first document (PDF, DOCX, TXT, or HTML)
3. Wait for processing (usually 1-3 minutes)
4. Generate an API key in the API Keys tab
5. Test your bot using the built-in test panel
6. Integrate using our REST API

### How long does document processing take?

Processing time depends on document size:
- Small documents (< 10 pages): 30 seconds - 1 minute
- Medium documents (10-50 pages): 1-3 minutes
- Large documents (50-100 pages): 3-5 minutes
- Very large documents (100+ pages): 5-10 minutes

You can upload multiple documents and they'll process in parallel.

### Can I customize my bot's personality?

Absolutely! Go to the "Bot Settings" tab and describe your business:
- Business name and industry
- What your business does
- Desired tone (Professional, Friendly, Technical, Casual, Formal)
- Primary goal for the bot
- Special instructions

Weaver's AI will generate an optimal system prompt in seconds. You can edit it or regenerate it as needed.

### How do I test my bot before deploying?

Use the built-in "Test Your Bot" panel in the API Keys tab:
1. Paste an API key
2. Enter a test question
3. Choose streaming or non-streaming mode
4. Click "Run Test"
5. See results instantly

You can also test the demo bot to see how Weaver works before uploading your own documents.

## Technical Questions

### What AI models does Weaver use?

Weaver uses Google's Gemini models:
- **gemini-2.5-flash-lite**: For generating answers (fast, cost-effective)
- **gemini-embedding-001**: For creating document embeddings (768 dimensions)

We may add support for other models (OpenAI, Anthropic) in the future.

### How does RAG work?

RAG (Retrieval-Augmented Generation) works in three steps:

1. **Indexing**: Your documents are split into chunks and converted to vector embeddings
2. **Retrieval**: When a question is asked, the most relevant chunks are found using semantic search
3. **Generation**: The AI generates an answer based on the retrieved context

This ensures answers are accurate and based on your actual documents.

### What's the average response time?

Typical query latency:
- **Cached queries**: < 100ms
- **Non-cached queries**: 1.5 - 3 seconds
  - Embedding generation: 50-100ms
  - Vector search: 100-200ms
  - LLM generation: 1-2 seconds

Streaming responses start appearing within 500ms.

### How accurate are the answers?

Accuracy depends on several factors:
- **Document quality**: Clear, well-written docs produce better results
- **Question specificity**: Specific questions get better answers than vague ones
- **Document coverage**: Bot can only answer based on uploaded content

Weaver provides confidence scores:
- **High**: Multiple relevant sources found (>0.7 similarity)
- **Medium**: Some relevant sources (0.5-0.7 similarity)
- **Low**: Few relevant sources (< 0.5 similarity)

### Is my data secure?

Yes! Weaver implements multiple security layers:
- All data encrypted at rest and in transit (TLS 1.3)
- Secure multi-tenant architecture (your data is isolated)
- API key authentication with rate limiting
- SOC 2 Type II compliant infrastructure
- GDPR compliant data processing
- Regular security audits

We never train models on your data or share it with third parties.

## Usage & Limits

### What are the rate limits?

Free tier limits:
- 60 API requests per minute per key
- 50 queries per day per tenant
- 10 documents maximum
- 100 MB total storage

Pro tier limits:
- 120 API requests per minute
- 1,000 queries per day
- Unlimited documents
- 10 GB storage

### What happens when I hit the daily query limit?

When you reach 50 queries in a day:
- Further queries return a 429 error
- Limit resets at midnight UTC
- You can upgrade to Pro for higher limits

The dashboard shows your current usage: "12/50 queries used today"

### Can I upload documents in bulk?

Yes! You can upload multiple documents at once:
- Drag and drop multiple files
- Click "Select Multiple Files"
- Up to 10 files at once (free tier)
- Processing happens in parallel

### How is storage calculated?

Storage is based on the original document size:
- A 5 MB PDF counts as 5 MB
- Processed data (embeddings, chunks) doesn't count toward storage
- Deleted documents free up storage immediately

### Can I delete documents?

Yes, you can delete documents from the dashboard:
1. Go to "Upload Documents" tab
2. Click the trash icon next to any document
3. Confirm deletion
4. Document is removed immediately
5. Storage is freed up

Note: This cannot be undone. The bot will no longer have access to that document's content.

## API & Integration

### How do I get an API key?

1. Log into your Weaver dashboard
2. Go to the "API Keys" tab
3. Click "Create New API Key"
4. Give it a name (e.g., "Production Key")
5. Copy the key immediately (it won't be shown again)
6. Use it in the Authorization header: `Bearer YOUR_API_KEY`

### Can I have multiple API keys?

Yes! Create as many API keys as needed:
- Separate keys for development/staging/production
- Keys for different applications
- Keys with different names for tracking

Each key has the same permissions and rate limits.

### How do I revoke a compromised API key?

1. Go to the "API Keys" tab
2. Find the compromised key
3. Click the trash icon
4. Confirm revocation
5. Key is immediately invalidated

Create a new key to replace it.

### What programming languages are supported?

Weaver's REST API works with any language that can make HTTP requests:
- JavaScript/TypeScript (examples provided)
- Python (examples provided)
- cURL (command-line examples)
- Ruby, Go, Java, PHP, etc. (use standard HTTP libraries)

Official SDKs coming soon for JavaScript, Python, and Go.

### Can I integrate Weaver into my mobile app?

Yes! Weaver's REST API works from:
- Web applications (React, Vue, Angular, etc.)
- Mobile apps (React Native, Flutter, Swift, Kotlin)
- Backend services (Node.js, Python, Go, etc.)
- Desktop applications (Electron, etc.)

Never expose your API key in client-side code. Use a backend proxy.

### Does Weaver support streaming responses?

Yes! Use the streaming endpoint for real-time responses:

```
GET /v1/tenants/{tenant_id}/query/stream?query=YOUR_QUESTION
Accept: text/event-stream
```

Responses arrive token-by-token via Server-Sent Events (SSE).

## Billing & Pricing

### How does the free tier work?

The free tier is completely free, forever:
- No credit card required
- 50 queries per day
- 10 documents
- 100 MB storage
- All features available

Perfect for testing and small projects.

### When should I upgrade to Pro?

Upgrade to Pro if you need:
- More than 50 queries per day
- More than 10 documents
- More than 100 MB storage
- Priority support
- Custom branding (coming soon)

### Is there an Enterprise plan?

Yes! Enterprise includes:
- Unlimited queries
- Unlimited documents
- Unlimited storage
- Dedicated support
- SLA guarantees
- On-premise deployment option
- Custom integrations

Contact sales@weaver.com for pricing.

### How is overage handled?

Free tier:
- Queries stop at 50/day limit
- Cannot upload documents beyond storage limit
- Upgrade to Pro to continue

Pro tier:
- Soft limits with overage charges
- $0.01 per additional query
- $0.10 per GB of additional storage

### Can I downgrade from Pro to Free?

Yes, but:
- Takes effect at the end of current billing period
- Documents beyond 10 must be deleted
- Storage beyond 100 MB must be freed
- Query limit drops to 50/day

## Troubleshooting

### Why is my document still processing?

Documents can take 1-10 minutes depending on size. If stuck for longer:
1. Check the document format is supported
2. Ensure the file isn't corrupted
3. Verify it's under the size limit (10 MB)
4. Refresh the page
5. Contact support if still stuck

### Why am I getting "low confidence" answers?

Low confidence means the bot couldn't find highly relevant information. Possible causes:
- Question is about content not in your documents
- Documents don't contain enough detail
- Question is too vague or broad
- Typos in the question

Solutions:
- Upload more comprehensive documentation
- Ask more specific questions
- Check the Analytics tab for low-confidence queries
- Refine your documents based on common questions

### Why am I getting 401 Unauthorized errors?

Common causes:
- API key is incorrect or expired
- API key was revoked
- Missing "Bearer" prefix in Authorization header
- Using session token instead of API key

Check your API key in the dashboard and ensure it's correctly formatted:
```
Authorization: Bearer sk_live_abc123...
```

### Why am I getting 429 Rate Limit errors?

You've exceeded either:
- **Minute limit**: 60 requests per minute per key (wait 1 minute)
- **Daily limit**: 50 queries per day (wait until midnight UTC or upgrade)

Check the error message for details.

### My bot isn't using my custom system prompt

Ensure you:
1. Generated a system prompt in "Bot Settings"
2. Clicked "Save & Activate Bot"
3. Waited for the save to complete
4. Refreshed your API client/cache

The prompt applies immediately to new queries.

## Advanced Features

### Can I use Weaver for multiple languages?

Currently, Weaver works best with English documents. Support for other languages coming soon:
- Spanish
- French
- German
- Japanese
- And more

### Can I fine-tune the bot's behavior?

Yes, through the system prompt in "Bot Settings":
- Define the bot's role and personality
- Specify tone and style
- Add disclaimers or policies
- Include special instructions

### Does Weaver support images or tables in documents?

Partial support:
- **Text in images**: Not yet (OCR coming soon)
- **Tables**: Text is extracted but formatting may be lost
- **Charts/Graphs**: Not yet (multimodal RAG coming soon)

Best results with text-heavy documents.

### Can I see what documents were used to answer a question?

Yes! Every response includes sources:
```json
"sources": [
  {
    "doc_id": "abc-123",
    "page": 5,
    "confidence": 0.92
  }
]
```

Use the doc_id to identify which document was used.

### Can I export my data?

Yes, contact support@weaver.com to request:
- Document export (original files)
- Query logs (CSV format)
- Analytics data

Enterprise plans include self-service export.

## Support & Community

### How do I get help?

Multiple support channels:
- **Documentation**: docs.weaver.com
- **Email**: support@weaver.com (24-48 hour response)
- **Community Forum**: community.weaver.com
- **Discord**: discord.gg/weaver
- **Status Page**: status.weaver.com

Pro users get priority support (4-12 hour response).

### Is there a community forum?

Yes! Join community.weaver.com to:
- Ask questions
- Share use cases
- Get integration help
- Vote on feature requests
- Connect with other users

### How do I request a new feature?

Three ways:
1. Submit feedback in the dashboard
2. Post in the community forum
3. Email feature-requests@weaver.com

We prioritize features based on user votes and business impact.

### Where can I report bugs?

Report bugs via:
- **Email**: bugs@weaver.com
- **Dashboard**: Click "Report Bug" in menu
- **Discord**: #bug-reports channel

Include steps to reproduce for faster resolution.

### Can I schedule a demo?

Yes! Contact sales@weaver.com to schedule:
- Platform walkthrough
- Custom integration consultation
- Enterprise features demo

## Future Features

### What's on the roadmap?

Coming in 2025:
- Multi-language support
- Image and table understanding
- Webhook integrations
- Slack and Discord bots
- Mobile SDKs
- Advanced analytics with A/B testing
- Custom domain support
- White-labeling
- Voice interaction
- Fine-tuning support

Vote on features at roadmap.weaver.com

### Will prices change?

Current pricing is locked for early users. We'll announce any changes with:
- 90 days notice
- Grandfather pricing for existing users
- Migration assistance

---

Still have questions? Email hello@weaver.com

Last Updated: November 2024 | Version 1.0
````

## File: demo_docs/integration_examples.txt
````
# Weaver API Integration Examples

## Getting Started

This guide provides practical examples for integrating Weaver's API into your applications. All examples use the REST API with API key authentication.

## Prerequisites

1. Weaver account with uploaded documents
2. Generated API key from the dashboard
3. Your tenant ID (found in dashboard URL)

## Base URL

```
Production: https://api.weaver.com
Development: http://localhost:8000
```

## Authentication

All API requests require an API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

## Example 1: Simple Query (cURL)

### Non-Streaming Query

```bash
curl -X POST https://api.weaver.com/v1/tenants/YOUR_TENANT_ID/query \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I reset my password?"
  }'
```

### Response

```json
{
  "answer": "To reset your password, follow these steps: 1) Click the 'Forgot Password' link on the login page, 2) Enter your email address, 3) Check your email for a reset link, 4) Click the link and create a new password.",
  "sources": [
    {
      "doc_id": "abc-123-def",
      "page": 5,
      "confidence": 0.92
    }
  ],
  "confidence": "high",
  "latency_ms": 1847,
  "daily_usage": {
    "current": 12,
    "limit": 50,
    "remaining": 38,
    "redis_available": true
  }
}
```

## Example 2: Streaming Query (cURL)

```bash
curl -N -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Accept: text/event-stream" \
  "https://api.weaver.com/v1/tenants/YOUR_TENANT_ID/query/stream?query=What+is+your+pricing"
```

### Streaming Response (SSE)

```
data: {"content": "Our"}
data: {"content": " pricing"}
data: {"content": " structure"}
data: {"content": " includes"}
data: {"content": " three"}
data: {"content": " tiers"}
data: {"content": "..."}
```

## Example 3: JavaScript/TypeScript Integration

### Simple Fetch

```javascript
async function queryBot(tenantId, apiKey, question) {
  const response = await fetch(
    `https://api.weaver.com/v1/tenants/${tenantId}/query`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: question }),
    }
  );

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  const data = await response.json();
  return data;
}

// Usage
const result = await queryBot(
  'your-tenant-id',
  'your-api-key',
  'How do I integrate the API?'
);

console.log('Answer:', result.answer);
console.log('Confidence:', result.confidence);
console.log('Sources:', result.sources);
```

### Streaming with EventSource

```javascript
function queryBotStreaming(tenantId, apiKey, question, onChunk, onComplete) {
  const query = encodeURIComponent(question);
  const url = `https://api.weaver.com/v1/tenants/${tenantId}/query/stream?query=${query}`;

  const eventSource = new EventSource(url, {
    headers: {
      'Authorization': `Bearer ${apiKey}`,
    },
  });

  let fullAnswer = '';

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    fullAnswer += data.content;
    onChunk(data.content);
  };

  eventSource.addEventListener('done', () => {
    eventSource.close();
    onComplete(fullAnswer);
  });

  eventSource.onerror = (error) => {
    console.error('Stream error:', error);
    eventSource.close();
  };

  return eventSource;
}

// Usage
const stream = queryBotStreaming(
  'your-tenant-id',
  'your-api-key',
  'Explain your API rate limits',
  (chunk) => console.log('Chunk:', chunk),
  (fullAnswer) => console.log('Complete:', fullAnswer)
);

// To stop streaming
// stream.close();
```

### React Component Example

```typescript
import { useState } from 'react';

interface QueryResult {
  answer: string;
  sources: Array<{ doc_id: string; page: number; confidence: number }>;
  confidence: string;
  latency_ms: number;
}

export function ChatWidget({ tenantId, apiKey }: Props) {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `https://api.weaver.com/v1/tenants/${tenantId}/query`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query }),
        }
      );
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Query failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-widget">
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question..."
      />
      <button onClick={handleQuery} disabled={loading}>
        {loading ? 'Querying...' : 'Ask'}
      </button>
      {result && (
        <div className="result">
          <p>{result.answer}</p>
          <small>Confidence: {result.confidence}</small>
        </div>
      )}
    </div>
  );
}
```

## Example 4: Python Integration

### Simple Query

```python
import requests
import json

def query_bot(tenant_id, api_key, question):
    url = f"https://api.weaver.com/v1/tenants/{tenant_id}/query"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"query": question}
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    return response.json()

# Usage
result = query_bot(
    tenant_id="your-tenant-id",
    api_key="your-api-key",
    question="How do I authenticate with the API?"
)

print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']}")
print(f"Latency: {result['latency_ms']}ms")
print(f"Daily usage: {result['daily_usage']['current']}/{result['daily_usage']['limit']}")
```

### Streaming Query

```python
import requests
import json

def query_bot_streaming(tenant_id, api_key, question):
    url = f"https://api.weaver.com/v1/tenants/{tenant_id}/query/stream"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "text/event-stream"
    }
    params = {"query": question}
    
    response = requests.get(url, headers=headers, params=params, stream=True)
    response.raise_for_status()
    
    full_answer = ""
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data = json.loads(line_str[6:])
                content = data.get('content', '')
                full_answer += content
                print(content, end='', flush=True)
    
    print()  # New line
    return full_answer

# Usage
answer = query_bot_streaming(
    tenant_id="your-tenant-id",
    api_key="your-api-key",
    question="What are your integration options?"
)
```

### Flask Integration

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

WEAVER_TENANT_ID = "your-tenant-id"
WEAVER_API_KEY = "your-api-key"

@app.route('/api/chat', methods=['POST'])
def chat():
    user_query = request.json.get('query')
    
    if not user_query:
        return jsonify({"error": "Query required"}), 400
    
    # Query Weaver bot
    response = requests.post(
        f"https://api.weaver.com/v1/tenants/{WEAVER_TENANT_ID}/query",
        headers={
            "Authorization": f"Bearer {WEAVER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={"query": user_query}
    )
    
    if response.status_code != 200:
        return jsonify({"error": "Bot query failed"}), 500
    
    result = response.json()
    
    return jsonify({
        "answer": result['answer'],
        "confidence": result['confidence'],
        "sources": result['sources']
    })

if __name__ == '__main__':
    app.run(debug=True)
```

## Example 5: Document Upload

```bash
curl -X POST https://api.weaver.com/v1/tenants/YOUR_TENANT_ID/docs:upload \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -F "file=@/path/to/document.pdf"
```

### Response

```json
{
  "doc_id": "abc-123-def",
  "filename": "document.pdf",
  "status": "processing",
  "upload_url": null
}
```

## Example 6: API Key Management

### Create API Key

```bash
curl -X POST https://api.weaver.com/v1/tenants/YOUR_TENANT_ID/api-keys \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Key",
    "rate_limit_rpm": 60
  }'
```

### Response

```json
{
  "key_id": "key-789-xyz",
  "key": "sk_live_abc123def456...",
  "name": "Production Key",
  "created_at": "2024-11-12T10:30:00Z"
}
```

### List API Keys

```bash
curl https://api.weaver.com/v1/tenants/YOUR_TENANT_ID/api-keys \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

### Revoke API Key

```bash
curl -X DELETE https://api.weaver.com/v1/tenants/YOUR_TENANT_ID/api-keys/key-789-xyz \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

## Example 7: Error Handling

### Rate Limit Exceeded

```json
{
  "detail": "Rate limit exceeded. Maximum 60 requests per minute."
}
```

### Daily Limit Exceeded

```json
{
  "detail": "Daily query limit exceeded (50 queries/day). Resets at midnight UTC."
}
```

### Missing API Key

```json
{
  "detail": "Missing API key"
}
```

### Invalid API Key

```json
{
  "detail": "Invalid API key"
}
```

### Robust Error Handling (JavaScript)

```javascript
async function queryBotWithErrorHandling(tenantId, apiKey, question) {
  try {
    const response = await fetch(
      `https://api.weaver.com/v1/tenants/${tenantId}/query`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: question }),
      }
    );

    if (response.status === 429) {
      throw new Error('Rate limit exceeded. Please wait and try again.');
    }

    if (response.status === 401) {
      throw new Error('Invalid API key. Please check your credentials.');
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Query failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Bot query error:', error);
    throw error;
  }
}
```

## Example 8: Webhook Integration (Future)

Coming soon: Webhooks for document processing completion, query events, and usage alerts.

```javascript
// Webhook endpoint example
app.post('/webhooks/weaver', (req, res) => {
  const event = req.body;
  
  switch (event.type) {
    case 'document.processed':
      console.log(`Document ${event.doc_id} processed successfully`);
      break;
    case 'query.completed':
      console.log(`Query answered with ${event.confidence} confidence`);
      break;
    case 'usage.threshold':
      console.log(`Usage at ${event.percentage}% of daily limit`);
      break;
  }
  
  res.sendStatus(200);
});
```

## Best Practices

### 1. Security
- Never expose API keys in client-side code
- Use environment variables for keys
- Rotate keys periodically
- Implement key-specific rate limits

### 2. Performance
- Cache responses for identical queries
- Use streaming for long responses
- Implement timeout handling
- Monitor latency metrics

### 3. User Experience
- Show loading indicators during queries
- Display confidence scores
- Provide source citations
- Handle errors gracefully

### 4. Monitoring
- Track query volume
- Monitor error rates
- Alert on daily limit approaching
- Log slow queries for optimization

## Rate Limits

- **Per API Key**: 60 requests per minute
- **Per Tenant**: 50 queries per day (configurable)
- **Document Upload**: 10 MB per file
- **Concurrent Requests**: 5 per API key

## Support

- API Documentation: https://api.weaver.com/docs
- Status Page: https://status.weaver.com
- Support Email: api-support@weaver.com
- Discord Community: https://discord.gg/weaver

## SDKs (Coming Soon)

Official SDKs are in development:
- JavaScript/TypeScript
- Python
- Go
- Ruby
- Java

---

Start building intelligent experiences with Weaver's API today!
Version 1.0 | Last Updated: November 2024
````

## File: demo_docs/rag_guide.txt
````
# Understanding RAG: Retrieval-Augmented Generation

## Introduction

RAG (Retrieval-Augmented Generation) is a powerful AI technique that combines the best of two worlds: information retrieval and natural language generation. This guide explains how RAG works and why it's the foundation of Weaver's intelligent bot platform.

## What is RAG?

RAG is an AI framework that enhances large language models (LLMs) by giving them access to external knowledge sources. Instead of relying solely on the model's training data, RAG retrieves relevant information from a knowledge base and uses it to generate accurate, contextual responses.

### The Problem RAG Solves

Traditional LLMs have several limitations:
- **Knowledge Cutoff**: They only know information up to their training date
- **Hallucinations**: They may generate plausible but incorrect information
- **No Source Citations**: Users can't verify where information came from
- **Static Knowledge**: They can't be updated with new information without retraining

RAG addresses all these issues by grounding responses in actual documents.

## How RAG Works: The Three-Phase Process

### Phase 1: Indexing (Offline)

This happens when you upload documents to Weaver:

1. **Document Ingestion**
   - Documents are uploaded (PDF, DOCX, TXT, HTML)
   - Text is extracted from various formats
   - Content is cleaned and preprocessed

2. **Text Chunking**
   - Documents are split into smaller, semantic chunks (500 tokens)
   - Overlap between chunks ensures context continuity (10% overlap)
   - Each chunk maintains metadata (document ID, page number)

3. **Embedding Generation**
   - Each text chunk is converted into a vector (numerical representation)
   - Weaver uses Google's gemini-embedding-001 model
   - Creates 768-dimensional vectors that capture semantic meaning

4. **Vector Storage**
   - Embeddings are stored in PostgreSQL with pgvector extension
   - HNSW (Hierarchical Navigable Small World) index for fast retrieval
   - Optimized for similarity search at scale

### Phase 2: Retrieval (Real-Time)

When a user asks a question:

1. **Query Embedding**
   - User's question is converted to a vector using the same embedding model
   - Ensures query and documents are in the same semantic space
   - Takes ~50-100ms to generate

2. **Similarity Search**
   - Query vector is compared against all document vectors
   - Uses cosine similarity to find most relevant chunks
   - HNSW index enables sub-second search across millions of vectors
   - Top K most similar chunks are retrieved (default K=3)

3. **Context Assembly**
   - Retrieved chunks are ranked by similarity score
   - Text from top chunks is assembled into context
   - Metadata (document name, page number) is preserved

### Phase 3: Generation (Real-Time)

Generating the final answer:

1. **Prompt Construction**
   - System prompt defines bot behavior
   - Retrieved context is injected into the prompt
   - User's question is included
   - Prompt instructs LLM to cite sources

2. **LLM Invocation**
   - Complete prompt sent to Google Gemini (gemini-2.5-flash-lite)
   - LLM generates answer based on provided context
   - Can stream response in real-time using SSE

3. **Response Assembly**
   - Generated answer is extracted
   - Source citations are attached
   - Confidence score calculated
   - Latency metrics recorded

## Key RAG Concepts

### Embeddings

Embeddings are dense vector representations of text that capture semantic meaning. Similar concepts have similar vectors, enabling semantic search.

**Example:**
- "How do I reset my password?" 
- "What's the process for password recovery?"

These questions have different words but similar embeddings, so RAG retrieves the same relevant documentation.

### Semantic Search vs. Keyword Search

**Keyword Search:**
- Matches exact words
- Query: "car repair" won't find "automobile maintenance"
- Fast but limited understanding

**Semantic Search (RAG):**
- Matches meaning
- Query: "car repair" finds "automobile maintenance", "vehicle servicing"
- Understands synonyms, context, intent

### Vector Similarity Metrics

Weaver uses cosine similarity to measure how "close" two vectors are:
- Score ranges from 0 (completely different) to 1 (identical)
- High scores (>0.7) indicate strong relevance
- Low scores (<0.5) suggest weak relevance

### Chunking Strategy

Why chunk documents?

1. **LLM Context Limits**: Models have token limits (e.g., 8,192 tokens)
2. **Precision**: Smaller chunks = more precise retrieval
3. **Performance**: Faster to search through smaller units
4. **Quality**: More relevant context = better answers

Weaver's chunking:
- 500 tokens per chunk (optimal for most use cases)
- 10% overlap between chunks (preserves context)
- Respects sentence boundaries (no mid-sentence cuts)

## RAG vs. Fine-Tuning

### RAG (Retrieval-Augmented Generation)
**Pros:**
- Instant knowledge updates (just upload new docs)
- Source attribution (always cite sources)
- Lower cost (no model training)
- Transparent (see what documents were used)
- Flexible (different knowledge bases per tenant)

**Cons:**
- Retrieval latency (1-3 seconds)
- Dependent on chunk quality
- Requires vector database infrastructure

### Fine-Tuning
**Pros:**
- Faster inference (no retrieval step)
- Can teach writing style and tone
- Smaller models possible

**Cons:**
- Expensive (requires GPU training)
- Time-consuming (days to weeks)
- Static knowledge (must retrain for updates)
- No source attribution
- Hallucination risk remains

**Weaver's Approach:** We use RAG because most businesses need dynamic, verifiable knowledge bases, not style adaptation.

## Advanced RAG Techniques in Weaver

### 1. HNSW Indexing
- Approximate nearest neighbor search
- Sub-linear search time
- Parameters: m=32, ef_construction=128
- Balances speed and accuracy

### 2. Caching
- Redis caches embeddings (1 hour TTL)
- Query results cached (5 minutes TTL)
- Reduces costs and latency for repeated queries

### 3. Confidence Scoring
- High confidence: Multiple relevant chunks, high similarity
- Medium confidence: Some relevant chunks
- Low confidence: No highly relevant chunks found

### 4. Streaming Responses
- Server-Sent Events (SSE) for real-time output
- Users see answers as they're generated
- Improves perceived latency

## RAG Best Practices

### For Better Results:

1. **Quality Documents**
   - Well-structured content
   - Clear headings and sections
   - Avoid scanned images without OCR
   - Update outdated information

2. **Specific Questions**
   - "How do I reset my password?" (Good)
   - "Tell me about passwords" (Too broad)

3. **Monitor Analytics**
   - Track low-confidence queries
   - Identify knowledge gaps
   - Add missing documentation

4. **Iterative Improvement**
   - Review unanswered questions
   - Refine document structure
   - Test with real user queries

### Common Pitfalls:

1. **Too Much Context**
   - Don't upload everything at once
   - Focus on relevant, high-quality docs
   - Remove duplicates

2. **Poor Document Quality**
   - Scanned PDFs without text layer
   - Inconsistent formatting
   - Outdated information

3. **Unrealistic Expectations**
   - RAG retrieves from your docs only
   - Can't infer information not present
   - Best for factual Q&A, not creative writing

## RAG Performance Metrics

### Weaver's RAG Performance:

- **Average Query Latency**: 1.5-3 seconds
- **Embedding Generation**: 50-100ms
- **Vector Search**: 100-200ms
- **LLM Generation**: 1-2 seconds
- **Cache Hit Rate**: 40-60% (typical)

### Optimization Strategies:

1. **Embedding Cache**: Reuse embeddings for identical queries
2. **Connection Pooling**: Reduce database overhead
3. **Batch Processing**: Process multiple documents efficiently
4. **Index Optimization**: Regular ANALYZE on vector indices

## RAG Use Cases

### Customer Support Automation
- Answer FAQs from help documentation
- Provide troubleshooting steps
- Reduce ticket volume by 30-50%

### Internal Knowledge Management
- Search across company wikis, policies, procedures
- Onboard new employees faster
- Reduce "where is that document?" questions

### Developer Documentation
- API reference search
- Code example lookup
- Integration guide assistance

### Compliance & Legal
- Policy interpretation
- Regulatory guidance
- Contract clause search

### Research & Education
- Literature review assistance
- Course material Q&A
- Study guide generation

## Future of RAG

### Emerging Trends:

1. **Hybrid Search**: Combining semantic and keyword search
2. **Multi-Modal RAG**: Including images, tables, charts
3. **Conversational RAG**: Multi-turn dialogues with context
4. **Agentic RAG**: AI agents that can navigate and reason over documents
5. **Personalized RAG**: User-specific retrieval based on history

### Weaver's Roadmap:

- Multi-language embedding support
- Advanced chunk strategies (recursive splitting)
- Query rewriting for better retrieval
- Feedback loops for continuous improvement

## Conclusion

RAG is the foundation of modern knowledge bots. By combining retrieval with generation, it delivers accurate, verifiable, and up-to-date answers from your documents. Weaver makes RAG accessible to everyone through a simple, powerful platform.

## Learn More

- Read "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al., 2020)
- Explore Weaver's API documentation for integration examples
- Join our community forum to share RAG tips and tricks

---

Understanding RAG is key to building effective knowledge bots.
Version 1.0 | Last Updated: November 2024
````

## File: demo_docs/weaver_overview.txt
````
# Weaver Platform Overview

## What is Weaver?

Weaver is an AI-powered knowledge bot platform that enables businesses to create and deploy intelligent customer-service bots trained on their own documents. Built on cutting-edge RAG (Retrieval-Augmented Generation) technology, Weaver transforms your documentation into conversational AI that can answer questions accurately and contextually.

## Key Features

### Document Ingestion
- Upload multiple document formats: PDF, DOCX, TXT, and HTML
- Automatic text extraction and preprocessing
- Intelligent document chunking for optimal retrieval
- Support for large document libraries

### RAG-Based Query Answering
- Semantic search using vector embeddings
- Context-aware responses based on your documents
- High accuracy with source citation
- Confidence scoring for every answer

### API-First Architecture
- RESTful API endpoints for integration
- API key authentication for secure access
- Rate limiting (60 requests per minute)
- Daily query limits (50 queries per day, configurable)
- Real-time streaming responses via Server-Sent Events (SSE)

### AI-Powered Bot Configuration
- No prompt engineering skills required
- Simple business information form
- AI generates optimal system prompts
- Customizable bot personality (Professional, Friendly, Technical, Casual, Formal)
- Edit and regenerate prompts as needed

### Performance & Scalability
- High-performance query engine (1.5-3s average latency)
- Redis caching for embeddings and query results
- Optimized HNSW vector search
- PostgreSQL with pgvector extension
- Horizontal scaling support

### Analytics Dashboard
- Query volume tracking
- Average latency monitoring
- Low-confidence query identification
- Top queries analysis
- Daily usage statistics

### Multi-Tenancy
- Secure data isolation per tenant
- One bot per tenant architecture
- Role-based access control (Owner, Admin, Member)
- Individual API keys per tenant

## Technology Stack

### Backend
- FastAPI (Python 3.12) - High-performance web framework
- Celery + Redis - Background task processing
- PostgreSQL + pgvector - Vector database with HNSW indexing
- SQLAlchemy 2.0 - Async ORM
- Alembic - Database migrations
- Google Gemini - LLM and embeddings (gemini-2.5-flash-lite, gemini-embedding-001)

### Frontend
- React 18 + Vite + TypeScript
- Zustand - State management
- TanStack Query (React Query) - Server state
- Tailwind CSS + shadcn/ui - Styling
- Recharts - Analytics visualization

### Storage & Auth
- Google Cloud Storage (GCS) - Document storage via HMAC keys
- Supabase OAuth - Google authentication
- JWT tokens for API authentication

## Use Cases

### Customer Support
Deploy a bot that answers common customer questions based on your help documentation, reducing support ticket volume and response times.

### Internal Knowledge Base
Enable employees to quickly find information across company wikis, policies, and procedures without manual searching.

### Product Documentation
Help developers and users understand your product features, API endpoints, and integration guides through conversational queries.

### Technical Documentation
Assist developers with API documentation, code examples, and troubleshooting guides in a natural language interface.

### Education & Training
Provide students or trainees with instant access to course materials, FAQs, and learning resources.

## Getting Started

1. **Sign Up** - Create an account using Google OAuth
2. **Upload Documents** - Add your PDFs, DOCX, TXT, or HTML files
3. **Configure Bot** - Describe your business to generate a custom system prompt
4. **Generate API Key** - Create keys for programmatic access
5. **Integrate** - Use our REST API to query your bot from any application
6. **Monitor** - Track usage and performance in the analytics dashboard

## Pricing Tiers (Future)

### Free Tier
- 50 queries per day
- 10 documents max
- 100 MB storage
- Email support

### Pro Tier
- 1,000 queries per day
- Unlimited documents
- 10 GB storage
- Priority support
- Custom branding

### Enterprise
- Unlimited queries
- Unlimited documents
- Unlimited storage
- Dedicated support
- On-premise deployment option
- SLA guarantees

## Security & Compliance

- End-to-end encryption for data at rest and in transit
- SOC 2 Type II compliant infrastructure
- GDPR compliant data processing
- Regular security audits
- Role-based access control (RBAC)
- API key rotation support
- Audit logging for all operations

## Support & Resources

- Documentation: https://docs.weaver.com
- API Reference: https://api.weaver.com/docs
- Community Forum: https://community.weaver.com
- Email Support: support@weaver.com
- Status Page: https://status.weaver.com

## Roadmap

### Q1 2025
- Multi-language support
- Advanced analytics with A/B testing
- Webhook integrations
- Slack and Discord bots

### Q2 2025
- Custom domain support
- White-labeling options
- Fine-tuning support for specialized domains
- Compliance certifications (HIPAA, SOC 2)

### Q3 2025
- Mobile SDKs (iOS and Android)
- Voice interaction support
- Advanced prompt templates
- Team collaboration features

## Contact

For sales inquiries: sales@weaver.com
For partnerships: partners@weaver.com
For general questions: hello@weaver.com

Follow us on Twitter: @WeaverAI
LinkedIn: linkedin.com/company/weaver-ai

---

Weaver - Transform your documents into intelligent conversations.
Version 1.0 | Last Updated: November 2024
````

## File: frontend/src/components/ui/sonner.tsx
````typescript
import { Toaster as Sonner } from "sonner"

type ToasterProps = React.ComponentProps<typeof Sonner>

const Toaster = ({ ...props }: ToasterProps) => {
  const theme = "light"

  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      className="toaster group"
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:bg-white group-[.toaster]:text-gray-950 group-[.toaster]:border-gray-200 group-[.toaster]:shadow-lg",
          description: "group-[.toast]:text-gray-500",
          actionButton:
            "group-[.toast]:bg-gray-900 group-[.toast]:text-gray-50",
          cancelButton:
            "group-[.toast]:bg-gray-100 group-[.toast]:text-gray-500",
        },
      }}
      {...props}
    />
  )
}

export { Toaster }
````

## File: frontend/src/hooks/useDebounce.ts
````typescript
import { useEffect, useState } from 'react'

export function useDebounce<T>(value: T, delay = 300): T {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const handler = window.setTimeout(() => setDebouncedValue(value), delay)
    return () => window.clearTimeout(handler)
  }, [value, delay])

  return debouncedValue
}
````

## File: frontend/src/lib/axios.ts
````typescript
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_URL,
})

export { API_URL }
````

## File: frontend/src/lib/gtag.ts
````typescript
// frontend/src/lib/gtag.ts

export const GA_MEASUREMENT_ID = 'G-PFNYJ5DXPF';

// Declare gtag function to avoid TypeScript errors
declare global {
  interface Window {
    gtag: (...args: any[]) => void;
  }
}

export const pageview = (url: string) => {
  if (typeof window.gtag === 'function') {
    window.gtag('config', GA_MEASUREMENT_ID, {
      page_path: url,
    });
  }
};
````

## File: frontend/src/lib/supabase.ts
````typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
````

## File: frontend/src/lib/utils.ts
````typescript
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatFileSize(bytes: number): string {
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString()
}
````

## File: frontend/src/vite-env.d.ts
````typescript
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_SUPABASE_URL: string
  readonly VITE_SUPABASE_ANON_KEY: string
  readonly VITE_SITE_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
````

## File: frontend/.eslintrc.cjs
````
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    '@typescript-eslint/no-explicit-any': 'off',
  },
}
````

## File: frontend/.gitignore
````
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# Environment variables
.env
.env.local
.env.production
````

## File: frontend/Dockerfile.dev
````
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
````

## File: frontend/nginx.conf
````
server {
    listen 3000;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;

    # SPA fallback - serve index.html for all routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
````

## File: frontend/postcss.config.js
````javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
````

## File: frontend/tailwind.config.js
````javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [],
}
````

## File: frontend/tsconfig.node.json
````json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
````

## File: infra/deploy/cloudrun.yaml
````yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: weaver-api
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: '1'
        autoscaling.knative.dev/maxScale: '10'
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
      - image: gcr.io/PROJECT_ID/weaver-api:latest
        ports:
        - name: http1
          containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: weaver-secrets
              key: database_url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: weaver-secrets
              key: redis_url
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: weaver-secrets
              key: google_api_key
        - name: SUPABASE_URL
          valueFrom:
            secretKeyRef:
              name: weaver-secrets
              key: supabase_url
        - name: SUPABASE_KEY
          valueFrom:
            secretKeyRef:
              name: weaver-secrets
              key: supabase_key
        - name: ENVIRONMENT
          value: production
        resources:
          limits:
            cpu: '2'
            memory: 2Gi
          requests:
            cpu: '1'
            memory: 1Gi
---
apiVersion: v1
kind: Service
metadata:
  name: weaver-worker
spec:
  selector:
    app: weaver-worker
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weaver-worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: weaver-worker
  template:
    metadata:
      labels:
        app: weaver-worker
    spec:
      containers:
      - name: worker
        image: gcr.io/PROJECT_ID/weaver-worker:latest
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: weaver-secrets
              key: database_url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: weaver-secrets
              key: redis_url
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: weaver-secrets
              key: google_api_key
        - name: ENVIRONMENT
          value: production
        resources:
          limits:
            cpu: '2'
            memory: 4Gi
          requests:
            cpu: '1'
            memory: 2Gi
````

## File: scripts/deploy.sh
````bash
#!/bin/bash

set -e

PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}

echo "🚀 Deploying Weaver to GCP"
echo "=========================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

echo "🔨 Building Docker images..."
docker build -t gcr.io/$PROJECT_ID/weaver-api:latest -f infra/docker/Dockerfile --target api .
docker build -t gcr.io/$PROJECT_ID/weaver-worker:latest -f infra/docker/Dockerfile --target worker .

echo ""
echo "📤 Pushing images to GCR..."
docker push gcr.io/$PROJECT_ID/weaver-api:latest
docker push gcr.io/$PROJECT_ID/weaver-worker:latest

echo ""
echo "🔐 Creating secrets (if not exists)..."
gcloud secrets create weaver-secrets --data-file=backend/.env --project=$PROJECT_ID || echo "Secrets already exist"

echo ""
echo "☁️  Deploying API to Cloud Run..."
gcloud run deploy weaver-api \
  --image gcr.io/$PROJECT_ID/weaver-api:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --project $PROJECT_ID

echo ""
echo "⚙️  Deploying workers..."
echo "Note: Workers should be deployed to GKE or Compute Engine"
echo "See infra/deploy/cloudrun.yaml for configuration"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Get the API URL:"
echo "  gcloud run services describe weaver-api --region $REGION --format 'value(status.url)'"
````

## File: scripts/setup.sh
````bash
#!/bin/bash

set -e

echo "🧩 Weaver Setup Script"
echo "======================"
echo ""

if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env from template..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your actual credentials"
fi

if [ ! -f frontend/.env.local ]; then
    echo "📝 Creating frontend/.env.local from template..."
    cp frontend/.env.example frontend/.env.local
    echo "⚠️  Please edit frontend/.env.local with your actual credentials"
fi

echo ""
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis

echo ""
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

echo ""
echo "📊 Running database migrations..."
docker-compose exec -T postgres psql -U weaver -d weaver < backend/app/db/models.sql

echo ""
echo "🐍 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

echo ""
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the services:"
echo "  1. Backend API:  cd backend && uvicorn app.main:app --reload"
echo "  2. Celery Worker: celery -A worker.celery.celery_app worker --loglevel=info"
echo "  3. Frontend:     cd frontend && npm run dev"
echo ""
echo "Visit http://localhost:3000 to access the dashboard"
````

## File: worker/health_server.py
````python
#!/usr/bin/env python3
"""
Lightweight HTTP health check server for Cloud Run.
Runs alongside Celery worker to respond to Cloud Run health probes.
"""
import os
from http.server import HTTPServer, BaseHTTPRequestHandler


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Respond to health check requests"""
        if self.path in ['/', '/health', '/healthz']:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress request logging to keep logs clean"""
        pass


def run_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f'✅ Health check server listening on port {port}')
    server.serve_forever()


if __name__ == '__main__':
    run_server()
````

## File: .alembic_commands.md
````markdown
# Alembic Quick Reference

## Common Commands

### Check Status
```bash
# Show current migration version
alembic current

# Show migration history
alembic history

# Show detailed history
alembic history --verbose
```

### Apply Migrations
```bash
# Apply all pending migrations
alembic upgrade head

# Apply next migration
alembic upgrade +1

# Apply to specific version
alembic upgrade <revision>
```

### Rollback Migrations
```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision>

# Rollback all migrations
alembic downgrade base
```

### Create Migrations
```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "description"

# Create empty migration
alembic revision -m "description"
```

### Preview SQL
```bash
# Show SQL without executing
alembic upgrade head --sql

# Show SQL for downgrade
alembic downgrade -1 --sql
```

### Troubleshooting
```bash
# Mark database as up-to-date without running migrations
alembic stamp head

# Mark as specific version
alembic stamp <revision>
```

## Docker Commands

When running in Docker:

```bash
# Check current version
docker-compose exec api alembic current

# Apply migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Show history
docker-compose exec api alembic history
```

## Workflow

### Making Model Changes

1. Edit `backend/app/db/models.py`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review generated file in `backend/alembic/versions/`
4. Apply migration: `alembic upgrade head`
5. Test your changes

### Production Deployment

1. **Backup database first!**
   ```bash
   pg_dump weaver > backup_$(date +%Y%m%d).sql
   ```

2. Apply migrations:
   ```bash
   alembic upgrade head
   ```

3. Verify:
   ```bash
   alembic current
   ```

4. If issues, rollback:
   ```bash
   alembic downgrade -1
   ```

## Tips

- Always review auto-generated migrations before applying
- Test migrations on a copy of production data first
- Keep migrations small and focused
- Never edit applied migrations - create a new one instead
- Use meaningful migration messages
- Backup before migrating production
````

## File: .env.example
````
DATABASE_URL=postgresql+asyncpg://weaver:weaver_dev@postgres:5432/weaver
REDIS_URL=redis://redis:6379/0

GOOGLE_API_KEY=your_google_gemini_api_key_here

GCS_BUCKET_NAME=weaver-docs
GCS_PROJECT_ID=your-gcp-project-id

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

SENTRY_DSN=


ENVIRONMENT=development


LOG_LEVEL=INFO


RATE_LIMIT_RPM=60

MAX_FILE_SIZE_MB=200
MAX_TENANT_STORAGE_GB=2


CHUNK_SIZE=800
CHUNK_OVERLAP_PCT=20
TOP_K_RESULTS=8
LLM_TEMPERATURE=0.2
````

## File: ARCHITECTURE.md
````markdown
# Weaver Architecture

## Overview

Weaver is a multi-tenant SaaS platform for creating AI-powered knowledge bots. The system follows a one-bot-per-tenant model with API key authentication.

## System Components

### Backend API (FastAPI)

- **Framework**: FastAPI (Python 3.12)
- **Authentication**: 
  - Dashboard: Supabase OAuth (Google)
  - Bot API: API Key (Argon2 hashed)
- **Rate Limiting**: Redis token bucket (60 rpm default)
- **Observability**: Prometheus metrics, Sentry, structured JSON logging

**Key Endpoints**:
- `POST /v1/tenants/{tenant_id}/query` - Query bot
- `GET /v1/tenants/{tenant_id}/query/stream` - SSE streaming
- `POST /v1/tenants/{tenant_id}/docs:upload` - Upload documents
- `POST /v1/tenants/{tenant_id}/api-keys` - Manage API keys
- `GET /v1/tenants/{tenant_id}/analytics/*` - Analytics

### Workers (Celery)

- **Queue**: Redis
- **Tasks**:
  - Document extraction (PDF, DOCX, TXT, HTML)
  - Text chunking (800 tokens, 20% overlap)
  - Embedding generation (Gemini embedding-001, 1536-dim)
  - Vector upsert to pgvector

### Database (PostgreSQL + pgvector)

**ORM**: SQLAlchemy 2.0 (async)
**Migrations**: Alembic (versioned, auto-generated)

**Schema**:
- `tenants` - Tenant metadata
- `users` - User accounts (linked to Supabase)
- `bots` - Bot config (1:1 with tenants)
- `docs` - Document metadata
- `doc_chunks` - Text chunks with embeddings (vector(1536))
- `api_keys` - Hashed API keys
- `bot_queries` - Query logs for analytics

**Indexes**:
- HNSW on `doc_chunks.embedding` for fast cosine similarity search (m=16, ef_construction=64)
- B-tree indexes on foreign keys and frequently queried columns

**Models**: All tables defined as SQLAlchemy ORM models in `app/db/models.py` with relationships

### Storage (Google Cloud Storage)

- Bucket structure: `gs://weaver/{tenant_id}/docs/{filename}`
- Stores original uploaded documents
- Used by workers for extraction

### LLM & Embeddings (Google Gemini via LangChain)

- **Embeddings**: `gemini-embedding-001` (1536 dimensions)
- **Chat**: `gemini-pro` (temperature 0.2)
- **Integration**: LangChain-Google-GenAI
  - `GoogleGenerativeAIEmbeddings` for embeddings
  - `ChatGoogleGenerativeAI` for chat completion

### Frontend (Next.js)

- **Framework**: Next.js 14 + React 18
- **Styling**: Tailwind CSS
- **Auth**: Supabase Auth Helpers
- **Features**:
  - Document upload
  - API key management
  - Analytics dashboard

## Data Flow

### Document Ingestion

```
User uploads file
    ↓
FastAPI receives file
    ↓
Upload to GCS (gs://weaver/{tenant_id}/docs/)
    ↓
Create doc record in DB (status: pending)
    ↓
Enqueue Celery task
    ↓
Worker downloads from GCS
    ↓
Extract text (PyMuPDF, python-docx, html2text)
    ↓
Chunk text (800 tokens, 20% overlap)
    ↓
Generate embeddings (Gemini via LangChain)
    ↓
Upsert to doc_chunks table
    ↓
Update doc status to completed
```

### Query Processing

```
Client sends query with API key
    ↓
Verify API key (hash check)
    ↓
Check rate limit (Redis)
    ↓
Embed query (Gemini via LangChain)
    ↓
Search similar chunks (pgvector cosine similarity, top-k=8)
    ↓
Build prompt with context
    ↓
Generate answer (Gemini via LangChain)
    ↓
Calculate confidence (based on similarity scores)
    ↓
Log query to bot_queries
    ↓
Return response with sources
```

## Security

### API Key Management

- Keys generated with `secrets.token_urlsafe(48)`
- Prefix: `wvr_`
- Hashed with Argon2id before storage
- Verification via constant-time comparison
- Revocable per key
- Rotatable without downtime

### Tenant Isolation

- All queries filtered by `tenant_id`
- Separate GCS namespaces
- Row-level security via application logic
- No cross-tenant data leakage

### Rate Limiting

- Redis sliding window (token bucket)
- Per API key limits (default 60 rpm)
- Configurable per key
- Returns 429 on exceed

## Scalability

### Horizontal Scaling

- **API**: Cloud Run auto-scales (1-10 instances)
- **Workers**: Multiple Celery workers (3+ recommended)
- **Database**: PostgreSQL with read replicas
- **Redis**: Redis Cluster for high availability

### Performance Optimizations

- HNSW index on embeddings (m=16, ef_construction=64) - better accuracy than IVFFlat
- Connection pooling (SQLAlchemy)
- Async I/O (FastAPI + asyncpg)
- Batch embedding generation
- Cached embeddings (no re-computation)

## Monitoring

### Metrics (Prometheus)

- `weaver_queries_total` - Query count by tenant/confidence
- `weaver_query_latency_seconds` - Query latency histogram
- `weaver_ingestion_total` - Ingestion job count by status
- `weaver_active_tenants` - Active tenant gauge
- `weaver_api_errors_total` - Error count by endpoint

### Logging

- Structured JSON logs
- Fields: `request_id`, `tenant_id`, `latency_ms`, `status`
- Centralized via GCP Logging

### Error Tracking

- Sentry integration
- Automatic error capture
- Performance monitoring (10% sample rate)

## Deployment

### Local Development

```bash
# Single command to start everything
./start.sh

# To stop
./stop.sh
```

The startup script automatically:
- Builds and starts all Docker containers
- Runs database migrations
- Waits for all services to be healthy
- Displays access URLs and logs

### Production (GCP)

- **API**: Cloud Run (managed, auto-scaling)
- **Workers**: Compute Engine or GKE
- **Database**: Cloud SQL (PostgreSQL with pgvector)
- **Redis**: Memorystore
- **Storage**: Cloud Storage
- **Secrets**: Secret Manager

## Future Enhancements

- Fine-tuning support
- Human-in-the-loop editor
- Multi-language support
- Advanced analytics (A/B testing)
- Third-party integrations (Slack, Zendesk)
- Usage-based billing
````

## File: BOT_SETTINGS_QUICK_START.md
````markdown
# Bot Settings - Quick Start Guide

## For End Users

### Configure Your Bot in 3 Steps

#### Step 1: Navigate to Bot Settings
1. Log into your Weaver dashboard
2. Click the **"Bot Settings"** tab
3. You'll see a simple form asking about your business

#### Step 2: Fill Out Your Business Information

**Required Fields:**
- **Business/Product Name** - e.g., "Acme Corp", "MyProduct"
- **Industry** - e.g., "SaaS", "E-commerce", "Healthcare"
- **What does your business do?** - 2-3 sentence description
- **Bot Personality** - Choose from dropdown:
  - Professional & Polished
  - Friendly & Conversational
  - Technical & Precise
  - Casual & Approachable
  - Formal & Academic
- **Primary Goal** - What should the bot help with?

**Optional:**
- **Special Instructions** - Any specific guidelines

#### Step 3: Generate and Save
1. Click **"Generate Bot Configuration"** (takes 1-2 seconds)
2. Review the generated prompt - you can edit it if needed
3. Click **"Save & Activate Bot"**
4. Done! Your bot now has a custom personality

### Example Scenarios

#### 🏢 SaaS Product Support
```
Business Name: CloudSync
Industry: SaaS
Description: We provide cloud file synchronization for businesses. 
  Our platform syncs files across devices in real-time with enterprise 
  security.
Tone: Professional & Polished
Goal: Answer customer questions about features, pricing, and integrations
```

#### 🛒 E-commerce Store
```
Business Name: Artisan Market
Industry: E-commerce
Description: Online marketplace for handcrafted goods. We connect 
  artisans with buyers worldwide, offering unique, handmade products.
Tone: Friendly & Conversational
Goal: Help customers find products and answer shipping/return questions
Special: Always mention our 30-day satisfaction guarantee
```

#### 💻 Technical Documentation
```
Business Name: DevTools API
Industry: Developer Tools
Description: RESTful API for payment processing. We offer simple 
  integration, comprehensive documentation, and 99.99% uptime SLA.
Tone: Technical & Precise
Goal: Provide accurate API documentation and code examples
Special: Always encourage checking API reference for latest endpoints
```

---

## For Developers

### API Endpoints

#### Generate System Prompt
```bash
POST /v1/tenants/{tenant_id}/bot/generate-prompt
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "business_name": "Acme Corp",
  "industry": "E-commerce",
  "description": "We sell premium widgets online with fast shipping",
  "tone": "friendly",
  "primary_goal": "Help customers find the right products",
  "special_instructions": "Always mention free shipping over $50"
}

# Response
{
  "system_prompt": "You are Acme Corp's friendly shopping assistant...",
  "business_info": { ... }
}
```

#### Update Bot Configuration
```bash
PUT /v1/tenants/{tenant_id}/bot
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "system_prompt": "Your custom prompt or generated prompt",
  "business_info": {
    "business_name": "...",
    "industry": "...",
    ...
  }
}

# Response
{
  "tenant_id": "...",
  "name": "Your Bot",
  "system_prompt": "...",
  "business_info": {...},
  "using_default_prompt": false,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### Revert to Default Prompt
```bash
PUT /v1/tenants/{tenant_id}/bot
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "system_prompt": ""
}
```

### Frontend Integration

```typescript
import { useGenerateSystemPrompt, useUpdateBotConfig } from '@/hooks/useBot'

function MyComponent() {
  const generateMutation = useGenerateSystemPrompt(tenantId)
  const updateMutation = useUpdateBotConfig(tenantId)
  
  const handleGenerate = async () => {
    const result = await generateMutation.mutateAsync({
      businessName: "Acme Corp",
      industry: "E-commerce",
      description: "...",
      tone: "friendly",
      primaryGoal: "Help customers",
      specialInstructions: "..."
    })
    console.log(result.system_prompt)
  }
  
  const handleSave = async (prompt: string) => {
    await updateMutation.mutateAsync({
      system_prompt: prompt,
      business_info: { ... }
    })
  }
}
```

### Database Schema

```sql
-- Stored in bots.config_json (JSONB)
{
  "system_prompt": "You are...",
  "business_info": {
    "business_name": "Acme Corp",
    "industry": "E-commerce",
    "description": "...",
    "tone": "friendly",
    "primary_goal": "...",
    "special_instructions": "..."
  }
}
```

### Testing the Feature

```bash
# Start dev environment
./start-dev.sh

# Backend tests
cd backend
pytest tests/test_prompt_generator.py -v

# Frontend tests
cd frontend
npm test -- BotSettingsTab

# Manual test in UI
# 1. Navigate to http://localhost:3000
# 2. Sign in
# 3. Go to "Bot Settings" tab
# 4. Fill form and generate
# 5. Save configuration
# 6. Go to "API Keys" tab -> "Test Your Bot"
# 7. Verify bot uses new personality
```

---

## Tips & Best Practices

### Writing Effective Descriptions
✅ **Good:**
> "We provide cloud-based project management software for remote teams. 
> Our platform includes task tracking, time management, and team collaboration 
> features."

❌ **Too Vague:**
> "We help businesses be more productive."

### Choosing the Right Tone

| If your business is... | Choose |
|------------------------|--------|
| B2B Enterprise SaaS | Professional |
| Consumer mobile app | Friendly |
| Developer tools/API | Technical |
| Lifestyle/social app | Casual |
| Legal/healthcare | Formal |

### Special Instructions Examples
- "Always include a disclaimer about not providing medical advice"
- "Mention our 24/7 support for urgent issues"
- "Use emojis occasionally 😊"
- "Link to docs.example.com for technical details"
- "Direct pricing questions to sales team"

### When to Regenerate
- Changing your target audience
- Launching new features
- Rebranding
- Feedback indicates wrong tone
- Low confidence queries on specific topics

---

## FAQ

**Q: Can I write my own prompt instead?**  
A: Yes! Just edit the generated prompt before saving, or write one from scratch in the text area.

**Q: How long does generation take?**  
A: Typically 1-2 seconds using Gemini's fast model.

**Q: Can I regenerate if I don't like the result?**  
A: Absolutely! Click "Regenerate" as many times as you want. Each generation will be slightly different.

**Q: Does changing the prompt affect existing conversations?**  
A: Yes, all new queries will use the updated prompt immediately. Past conversations are not changed.

**Q: Can I save multiple versions?**  
A: Currently, you can only have one active prompt per bot. The business_info is saved so you can regenerate later.

**Q: What if I want to use the default prompt again?**  
A: Save an empty string as the system_prompt - the bot will revert to using the default.

**Q: Is there a character limit?**  
A: The generated prompts are typically 2-4 paragraphs (~300-600 words). You can edit to make them longer or shorter.

---

## Support

Need help configuring your bot?
- 📧 Email: support@weaver.com
- 📖 Full docs: [BUSINESS_INFO_PROMPT_GENERATION.md](./BUSINESS_INFO_PROMPT_GENERATION.md)
- 💬 Chat: Available in dashboard

---

**Last Updated:** November 2024  
**Version:** 1.0
````

## File: DEMO_BOT_ADMIN_IMPLEMENTATION.md
````markdown
# Demo Bot Admin User Implementation

## Overview

Added support for creating an admin user in the demo bot migration using environment variables. The admin user is linked to the demo bot tenant and can upload/manage demo content.

## Changes Made

### 1. Migration Update
**File:** `backend/alembic/versions/004_create_demo_bot.py`

**What Changed:**
- Added `import os` for environment variable access
- Added admin profile creation logic (optional, based on env vars)
- Added UUID validation before insertion
- Added helpful console output messages
- Updated downgrade to remove admin profile

**Key Features:**
```python
# Reads environment variables
admin_uuid = os.getenv('DEMO_BOT_ADMIN_UUID')
admin_email = os.getenv('DEMO_BOT_ADMIN_EMAIL', 'admin@weaver.com')

# Validates UUID format
uuid.UUID(admin_uuid)

# Creates profile linked to demo tenant
INSERT INTO profiles (id, tenant_id, email, role, ...)
VALUES (admin_uuid, demo_tenant_id, admin_email, 'owner', ...)

# Provides clear feedback
print("✓ Created admin profile for {email} (UUID: {uuid})")
```

### 2. Environment Configuration
**Files:** `docker-compose.yml`, `env.template`

**Added Variables:**
```bash
DEMO_BOT_ADMIN_UUID=          # Supabase user UUID (leave empty to skip)
DEMO_BOT_ADMIN_EMAIL=admin@weaver.com  # Admin email (must match Supabase)
```

**Docker Compose:**
```yaml
api:
  environment:
    # ... existing vars ...
    - DEMO_BOT_ADMIN_UUID=${DEMO_BOT_ADMIN_UUID:-}
    - DEMO_BOT_ADMIN_EMAIL=${DEMO_BOT_ADMIN_EMAIL:-admin@weaver.com}
```

### 3. Documentation Updates

**Created:**
- `DEMO_BOT_ADMIN_SETUP.md` - Quick start guide (5-minute setup)

**Updated:**
- `DEMO_BOT_SETUP.md` - Added detailed admin setup steps
- `DEMO_BOT_IMPLEMENTATION.md` - Updated next steps section
- `README.md` - Added admin setup to demo bot section

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Supabase Dashboard                        │
│                                                             │
│  1. Create User                                             │
│     Email: admin@weaver.com                                 │
│     Password: [secure]                                      │
│     Auto Confirm: ✅                                         │
│     ↓                                                        │
│  2. Copy User UUID                                          │
│     a1b2c3d4-e5f6-7890-abcd-ef1234567890                   │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                    .env File                                │
│                                                             │
│  DEMO_BOT_ADMIN_UUID=a1b2c3d4-e5f6-7890-abcd-ef1234567890  │
│  DEMO_BOT_ADMIN_EMAIL=admin@weaver.com                     │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              Alembic Migration (004)                        │
│                                                             │
│  1. Create demo tenant                                      │
│  2. Create demo bot                                         │
│  3. IF DEMO_BOT_ADMIN_UUID set:                             │
│     - Validate UUID format                                  │
│     - Insert profile with:                                  │
│       • id = DEMO_BOT_ADMIN_UUID (from Supabase)           │
│       • tenant_id = demo_bot_id                            │
│       • email = DEMO_BOT_ADMIN_EMAIL                       │
│       • role = 'owner'                                      │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                    Database State                           │
│                                                             │
│  profiles table:                                            │
│  ┌──────────────┬─────────────────┬────────────┬────────┐  │
│  │      id      │      email      │ tenant_id  │  role  │  │
│  ├──────────────┼─────────────────┼────────────┼────────┤  │
│  │ a1b2c3d4-... │admin@weaver.com │ 00000000...│ owner  │  │
│  └──────────────┴─────────────────┴────────────┴────────┘  │
│                                                             │
│  Admin can now:                                             │
│  ✅ Login via Supabase auth                                 │
│  ✅ Access demo bot tenant dashboard                        │
│  ✅ Upload documents to demo bot                            │
│  ✅ Create API keys for demo bot                            │
└─────────────────────────────────────────────────────────────┘
```

### Key Constraints

1. **`profiles.id` MUST match Supabase `auth.users.id`**
   - Cannot create a profile without Supabase user
   - UUID must be copied from Supabase Dashboard

2. **Email must match**
   - `DEMO_BOT_ADMIN_EMAIL` must match Supabase user's email
   - Used for login and display

3. **Optional but recommended**
   - If variables not set, migration still succeeds
   - Admin can be created manually later

## Setup Workflow

### For Fresh Installation

1. **Create Supabase user** (Supabase Dashboard)
2. **Copy UUID** from user list
3. **Set environment variables** in `.env`
4. **Run `docker-compose up`** (migration runs automatically)
5. **Login as admin** and upload content

### For Existing Installation

1. **Create Supabase user** (Supabase Dashboard)
2. **Copy UUID** from user list
3. **Set environment variables** in `.env`
4. **Restart API**: `docker-compose restart api`
5. **Re-run migration**:
   ```bash
   docker-compose exec api alembic downgrade -1
   docker-compose exec api alembic upgrade head
   ```
6. **Login as admin** and upload content

### Without Environment Variables

Migration output:
```
ℹ DEMO_BOT_ADMIN_UUID not set. Skipping admin profile creation.
  To create an admin later:
  1. Create user in Supabase Dashboard
  2. Set DEMO_BOT_ADMIN_UUID and DEMO_BOT_ADMIN_EMAIL
  3. Re-run migration or manually insert profile
```

## Benefits

### 1. Flexible Setup
- ✅ Admin creation is optional
- ✅ Can be done during initial setup or later
- ✅ No code changes needed, just env vars

### 2. Secure by Default
- ✅ Requires Supabase user (proper authentication)
- ✅ UUID must exist in Supabase before profile creation
- ✅ Validates UUID format before insertion

### 3. Clear Feedback
- ✅ Migration prints success messages
- ✅ Warning if UUID format is invalid
- ✅ Instructions if variables not set

### 4. Idempotent
- ✅ Uses `ON CONFLICT DO NOTHING`
- ✅ Can re-run migration safely
- ✅ Downgrade removes admin profile

## Testing

### Verify Admin Creation

```bash
# Check if admin profile exists
docker-compose exec api psql $DATABASE_URL -c "
  SELECT 
    p.id,
    p.email,
    p.tenant_id,
    p.role,
    t.name as tenant_name
  FROM profiles p
  JOIN tenants t ON p.tenant_id = t.id
  WHERE p.email = 'admin@weaver.com';
"
```

Expected output:
```
              id              |       email        |             tenant_id              | role  |   tenant_name    
------------------------------+--------------------+------------------------------------+-------+------------------
 a1b2c3d4-e5f6-7890-abcd-... | admin@weaver.com   | 00000000-0000-0000-0000-000000000000 | owner | Weaver Demo Bot
```

### Test Admin Login

1. **Go to frontend**: `http://localhost:3000`
2. **Click "Sign in"**
3. **Use email/password** or Google OAuth
4. **Should land on dashboard** with demo bot tenant

### Test Document Upload

1. **Navigate to Upload tab**
2. **Upload a PDF**
3. **Should see "pending" → "processing" → "completed"**
4. **Document should appear in list**

## Troubleshooting

### Admin profile not created

**Symptoms:**
- Migration says "Skipping admin profile creation"
- Can't login as admin

**Solutions:**
1. Check `.env` file has `DEMO_BOT_ADMIN_UUID` set
2. Restart containers: `docker-compose restart api`
3. Re-run migration:
   ```bash
   docker-compose exec api alembic downgrade -1
   docker-compose exec api alembic upgrade head
   ```

### Invalid UUID format error

**Symptoms:**
- Migration prints "WARNING: Invalid DEMO_BOT_ADMIN_UUID format"

**Solutions:**
1. Verify UUID is in format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
2. Copy directly from Supabase Dashboard
3. Remove any quotes, spaces, or extra characters

### User not found when logging in

**Symptoms:**
- Can't login with admin credentials
- "User not found" error

**Solutions:**
1. Verify user exists in Supabase Dashboard
2. Check "Confirmed At" column has a timestamp
3. If not confirmed, manually confirm in Supabase Dashboard

### 403 Forbidden when uploading

**Symptoms:**
- Admin can login but can't upload documents

**Solutions:**
1. Verify `tenant_id` in profiles table is demo bot ID
2. Verify `role` is `owner` or `admin`
3. Check if admin user is in correct tenant

## Alternative: Manual Admin Creation

If migration approach doesn't work, create admin manually:

```sql
-- After creating user in Supabase
INSERT INTO profiles (id, tenant_id, email, role, created_at, updated_at)
VALUES (
    'YOUR_SUPABASE_USER_UUID',
    '00000000-0000-0000-0000-000000000000',
    'admin@weaver.com',
    'owner',
    NOW(),
    NOW()
)
ON CONFLICT (id) DO NOTHING;
```

Run via psql:
```bash
docker-compose exec api psql $DATABASE_URL -c "
  INSERT INTO profiles (id, tenant_id, email, role, created_at, updated_at)
  VALUES (
      'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
      '00000000-0000-0000-0000-000000000000',
      'admin@weaver.com',
      'owner',
      NOW(),
      NOW()
  )
  ON CONFLICT (id) DO NOTHING;
"
```

## Files Modified

- ✅ `backend/alembic/versions/004_create_demo_bot.py` - Added admin creation logic
- ✅ `docker-compose.yml` - Added environment variables
- ✅ `env.template` - Added admin config section
- ✅ `DEMO_BOT_SETUP.md` - Updated with admin setup steps
- ✅ `DEMO_BOT_IMPLEMENTATION.md` - Updated next steps
- ✅ `README.md` - Added admin setup to demo bot section
- ✅ `DEMO_BOT_ADMIN_SETUP.md` - NEW: Quick start guide

## Summary

✅ **Admin creation is now automated via migration**  
✅ **Uses environment variables for flexibility**  
✅ **Validates UUID format before insertion**  
✅ **Provides clear feedback during migration**  
✅ **Optional - migration succeeds without admin**  
✅ **Idempotent - safe to re-run**  
✅ **Secure - requires Supabase user first**  

The admin user is ready to upload demo content once the migration completes successfully! 🎉
````

## File: DEMO_BOT_ADMIN_SETUP.md
````markdown
# Demo Bot Admin Setup - Quick Reference

This guide shows you how to create an admin user for managing the demo bot content.

## Why Do You Need an Admin?

The demo bot needs documents to answer questions. To upload these documents, you need a user account that:
1. Exists in Supabase (for authentication)
2. Is linked to the demo bot tenant in your database
3. Has "owner" role permissions

## Setup Steps (5 Minutes)

### Step 1: Create User in Supabase Dashboard

1. **Open Supabase Dashboard**
   - Go to your Supabase project: `https://app.supabase.com/project/YOUR_PROJECT`

2. **Navigate to Authentication**
   - Click **"Authentication"** in the left sidebar
   - Click **"Users"** tab

3. **Add New User**
   - Click the **"Add user"** button
   - Fill in the form:
     ```
     Email: admin@weaver.com
     Password: [Choose a secure password]
     Auto Confirm User: ✅ (Enable this!)
     ```
   - Click **"Create user"**

4. **Copy the User UUID**
   - Find the new user in the list
   - Look for the **"ID"** column (UUID format)
   - Example: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
   - **Copy this UUID** - you'll need it in the next step

### Step 2: Configure Environment Variables

1. **Open your `.env` file** in the project root

2. **Add these lines** (or update if they exist):
   ```bash
   # Demo Bot Admin User
   DEMO_BOT_ADMIN_UUID=a1b2c3d4-e5f6-7890-abcd-ef1234567890  # Replace with your UUID
   DEMO_BOT_ADMIN_EMAIL=admin@weaver.com  # Must match Supabase email
   ```

3. **Save the file**

### Step 3: Run Migration

1. **Restart the API service** to pick up the new environment variables:
   ```bash
   docker-compose restart api
   ```

2. **Run the migration**:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

3. **Verify success** - you should see:
   ```
   ✓ Created admin profile for admin@weaver.com (UUID: a1b2c3d4-...)
   ```

   If you see this instead:
   ```
   ℹ DEMO_BOT_ADMIN_UUID not set. Skipping admin profile creation.
   ```
   Then the environment variables weren't loaded. Try:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Step 4: Login as Admin

1. **Open the frontend**:
   ```
   http://localhost:3000
   ```

2. **Click "Sign in with Google"** or use email/password login

3. **Enter admin credentials**:
   - Email: `admin@weaver.com`
   - Password: [the password you set in Supabase]

4. **You should land on the dashboard** with the demo bot tenant

### Step 5: Upload Demo Documents

1. **Go to the "Upload" tab**

2. **Upload 3-5 PDF documents** about:
   - What is Weaver? (Platform overview)
   - How RAG works (Technical explanation)
   - API documentation (Integration guide)
   - FAQ (Common questions)
   - Use cases (Example applications)

3. **Wait for processing** - documents will show "completed" status when ready

4. **Test the demo bot** in the API Keys tab

## Verification Checklist

- [ ] Admin user exists in Supabase Dashboard
- [ ] Admin UUID copied correctly
- [ ] `.env` file updated with UUID and email
- [ ] API service restarted
- [ ] Migration run successfully
- [ ] Success message: "Created admin profile for..."
- [ ] Can login as admin via frontend
- [ ] Dashboard shows demo bot tenant ID (`00000000-0000-0000-0000-000000000000`)
- [ ] Can upload documents successfully
- [ ] Documents show "completed" status
- [ ] Demo bot responds to queries

## Troubleshooting

### "User not found" when logging in

**Problem:** Can't login with admin credentials

**Solutions:**
1. Verify user exists in Supabase Dashboard → Authentication → Users
2. Check "Confirmed At" column - should have a timestamp (not blank)
3. If blank, click the user → "Send confirmation email" or manually confirm

### "Admin profile not created" in migration

**Problem:** Migration says "Skipping admin profile creation"

**Solutions:**
1. Check `.env` file has `DEMO_BOT_ADMIN_UUID` set
2. Verify UUID format is correct (no extra spaces, quotes, etc.)
3. Restart containers: `docker-compose down && docker-compose up -d`
4. Re-run migration: `docker-compose exec api alembic downgrade -1 && docker-compose exec api alembic upgrade head`

### "Tenant ID mismatch" when trying to upload

**Problem:** 403 Forbidden when uploading to demo bot tenant

**Solutions:**
1. Verify admin profile exists in database:
   ```bash
   docker-compose exec api psql $DATABASE_URL -c "
     SELECT id, email, tenant_id, role 
     FROM profiles 
     WHERE email = 'admin@weaver.com';
   "
   ```
2. Check that `tenant_id` is `00000000-0000-0000-0000-000000000000`
3. Check that `role` is `owner` or `admin`

### UUID format error in migration

**Problem:** Migration fails with "Invalid DEMO_BOT_ADMIN_UUID format"

**Solutions:**
1. Verify UUID is in correct format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
2. No extra quotes, spaces, or characters
3. Copy directly from Supabase Dashboard

## Database Verification

Check if the admin profile was created correctly:

```bash
# Check if profile exists
docker-compose exec api psql $DATABASE_URL -c "
  SELECT 
    p.id,
    p.email,
    p.tenant_id,
    p.role,
    t.name as tenant_name
  FROM profiles p
  JOIN tenants t ON p.tenant_id = t.id
  WHERE p.email = 'admin@weaver.com';
"
```

Expected output:
```
              id              |       email        |             tenant_id              | role  |   tenant_name    
------------------------------+--------------------+------------------------------------+-------+------------------
 a1b2c3d4-e5f6-7890-abcd-... | admin@weaver.com   | 00000000-0000-0000-0000-000000000000 | owner | Weaver Demo Bot
```

## Alternative: Manual Profile Creation

If the migration approach doesn't work, you can manually create the profile:

1. **Create user in Supabase** (as in Step 1)

2. **Manually insert profile**:
   ```sql
   INSERT INTO profiles (id, tenant_id, email, role, created_at, updated_at)
   VALUES (
       'YOUR_SUPABASE_USER_UUID',
       '00000000-0000-0000-0000-000000000000',
       'admin@weaver.com',
       'owner',
       NOW(),
       NOW()
   )
   ON CONFLICT (id) DO NOTHING;
   ```

3. **Run via psql**:
   ```bash
   docker-compose exec api psql $DATABASE_URL -c "
     INSERT INTO profiles (id, tenant_id, email, role, created_at, updated_at)
     VALUES (
         'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
         '00000000-0000-0000-0000-000000000000',
         'admin@weaver.com',
         'owner',
         NOW(),
         NOW()
     )
     ON CONFLICT (id) DO NOTHING;
   "
   ```

## Security Notes

- ✅ Admin can only upload to demo bot tenant
- ✅ Admin cannot access other users' data
- ✅ Admin role is for content management only
- ✅ Use a strong password for the admin account
- ⚠️ In production, use a non-obvious email (not `admin@...`)
- ⚠️ Consider creating multiple admin users with separate emails

## Next Steps After Setup

1. **Upload quality demo content** (3-5 well-written PDFs)
2. **Test queries** as a regular user to verify responses
3. **Monitor performance** in the Analytics tab
4. **Update content** periodically to keep it relevant
5. **Share the demo bot** with new users for onboarding

---

**Need Help?**
- See `DEMO_BOT_SETUP.md` for comprehensive documentation
- Check `DEMO_BOT_IMPLEMENTATION.md` for technical details
- Review `DEMO_BOT_TEST_PLAN.md` for testing checklist
````

## File: DEMO_BOT_IMPLEMENTATION.md
````markdown
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
````

## File: DEMO_BOT_SETUP.md
````markdown
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
````

## File: docker-compose.dev.yml
````yaml
# Development overrides for docker-compose.yml
# Usage: docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
      args:
        VITE_API_URL: ${API_URL:-http://localhost:8000}
        VITE_SUPABASE_URL: ${SUPABASE_URL}
        VITE_SUPABASE_ANON_KEY: ${SUPABASE_KEY}
        VITE_SITE_URL: ${SITE_URL:-http://localhost:3000}
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev
    environment:
      - NODE_ENV=development
      - VITE_API_URL=${API_URL:-http://localhost:8000}
      - VITE_SUPABASE_URL=${SUPABASE_URL}
      - VITE_SUPABASE_ANON_KEY=${SUPABASE_KEY}
      - VITE_SITE_URL=${SITE_URL:-http://localhost:3000}
````

## File: QUICK_REFERENCE.md
````markdown
# Quick Reference Card

## 🚀 Start the App

```bash
# Development (hot-reload)
./start-dev.sh

# Production
./start.sh

# Stop
./stop.sh
```

## 📁 Project Structure

```
frontend/src/
├── components/ui/       # Reusable UI (Button, Card, Tabs, Input)
├── components/dashboard/# Feature components (Upload, APIKeys, Analytics)
├── pages/              # Routes (Login, AuthCallback, Dashboard)
├── hooks/              # React Query hooks (useDocuments, useAPIKeys)
├── store/              # Zustand stores (authStore)
├── lib/                # Utils (supabase, axios, utils)
└── types/              # TypeScript types
```

## 🔧 Common Commands

```bash
# Install dependencies
cd frontend && npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🌐 Environment Variables

```bash
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_SITE_URL=http://localhost:3000
```

## 📦 Tech Stack

- **React 18** + **TypeScript**
- **Vite 5** (build tool)
- **React Router v6** (routing)
- **Zustand** (auth state)
- **TanStack Query** (server state)
- **Axios** (HTTP client)
- **Tailwind CSS** (styling)
- **shadcn/ui** (components)

## 🎣 Custom Hooks

```typescript
// Documents
import { useDocuments, useUploadDocument } from '@/hooks/useDocuments'
const { data: documents } = useDocuments(tenantId)
const uploadMutation = useUploadDocument(tenantId)

// API Keys
import { useAPIKeys, useCreateAPIKey, useRevokeAPIKey } from '@/hooks/useAPIKeys'
const { data: keys } = useAPIKeys(tenantId)
const createMutation = useCreateAPIKey(tenantId)
const revokeMutation = useRevokeAPIKey(tenantId)

// Auth
import { useAuthStore } from '@/store/authStore'
const { user, session, loading, signOut } = useAuthStore()
```

## 🎨 UI Components

```typescript
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'

<Button variant="destructive" size="lg">Delete</Button>
<Card><CardHeader><CardTitle>Title</CardTitle></CardHeader></Card>
```

## 🔐 Auth Flow

1. User clicks "Sign in with Google"
2. Redirected to Google OAuth
3. Callback to `/auth/callback`
4. Backend creates profile/tenant/bot
5. Redirected to `/dashboard`
6. Session persisted in Supabase

## 📤 Upload Flow

1. User selects file
2. `useUploadDocument` mutation
3. File uploaded to GCS
4. Celery worker processes document
5. Status polling (5s) via `useDocuments`
6. Status: pending → processing → completed

## 🔑 API Key Flow

1. User clicks "Create New API Key"
2. `useCreateAPIKey` mutation
3. Key displayed once (copy to clipboard)
4. Key stored in database (hashed)
5. User can revoke via `useRevokeAPIKey`

## 🧪 Testing Checklist

- [ ] OAuth login works
- [ ] Document upload works
- [ ] Status updates automatically
- [ ] API key creation works
- [ ] Copy to clipboard works
- [ ] API key revocation works
- [ ] Sign out works
- [ ] Hot-reload works (dev mode)

## 📚 Documentation

- `MIGRATION_COMPLETE.md` - Overview
- `MIGRATION_NOTES.md` - Technical details
- `FRONTEND_GUIDE.md` - Developer guide
- `TESTING_CHECKLIST.md` - Full testing guide

## 🐛 Debugging

```typescript
// React Query Devtools
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
<ReactQueryDevtools initialIsOpen={false} />

// Browser console
console.log('User:', useAuthStore.getState().user)
console.log('Session:', useAuthStore.getState().session)

// Docker logs
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f frontend
```

## 🔗 URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## 💡 Pro Tips

1. Use `./start-dev.sh` for development (instant hot-reload)
2. Check browser console for errors
3. Use React Query Devtools for debugging queries
4. Install Redux DevTools for Zustand state inspection
5. Use `cn()` utility for conditional Tailwind classes
6. Keep components small and focused
7. Extract logic into custom hooks
8. Always handle loading and error states

## 🆘 Common Issues

**Issue**: Hot-reload not working  
**Fix**: Ensure you're using `./start-dev.sh` and `docker-compose.dev.yml`

**Issue**: Environment variables not available  
**Fix**: Prefix with `VITE_` and rebuild

**Issue**: 404 on refresh  
**Fix**: Nginx config handles SPA routing (already configured)

**Issue**: Auth not persisting  
**Fix**: Check Supabase session in browser storage

**Issue**: Queries not refetching  
**Fix**: Check `queryKey` and `enabled` options in React Query

## 📞 Quick Links

- [Vite Docs](https://vitejs.dev/)
- [React Router](https://reactrouter.com/)
- [TanStack Query](https://tanstack.com/query/latest)
- [Zustand](https://docs.pmnd.rs/zustand/)
- [Tailwind CSS](https://tailwindcss.com/)
- [shadcn/ui](https://ui.shadcn.com/)
````

## File: QUICKSTART.md
````markdown
# Weaver Quick Start Guide

Get Weaver running locally in 5 minutes!

## Step 1: Prerequisites

Install the following:
- [Python 3.12+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Step 2: Get API Keys

### Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy it for later

### Supabase Setup
1. Go to [Supabase](https://supabase.com)
2. Create a new project
3. Go to Settings → API
4. Copy the URL and anon key
5. Go to Authentication → Providers
6. Enable Google OAuth
7. Configure OAuth callback: `http://localhost:3000/auth/callback`

### Google Cloud Storage (Optional for local dev)
1. Create a GCP project
2. Enable Cloud Storage API
3. Create a bucket named `weaver-docs`
4. Download service account credentials

## Step 3: Configure Environment

Create and edit `.env` file:

```bash
cd ~/makermode/weaver
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Google Gemini
GOOGLE_API_KEY=your_gemini_api_key_here

# Google Cloud Storage
GCS_BUCKET_NAME=weaver-docs
GCS_PROJECT_ID=your_gcp_project_id

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

## Step 4: Start Everything with One Command

```bash
./start.sh
```

That's it! The script will:
- ✅ Build all Docker images (API, Worker, Frontend)
- ✅ Start PostgreSQL with pgvector
- ✅ Start Redis
- ✅ Run Alembic migrations automatically (SQLAlchemy ORM)
- ✅ Start the API server
- ✅ Start Celery workers
- ✅ Start the frontend
- ✅ Wait for everything to be ready

The entire stack starts with a single command!

## Step 5: Access the App

1. Open http://localhost:3000
2. Click "Sign in with Google"
3. Complete OAuth flow
4. You'll be redirected to the dashboard

## Step 6: Test the System

### Upload a Document

1. Go to the "Upload Documents" tab
2. Select a PDF, DOCX, or TXT file (max 200MB)
3. Click "Upload"
4. Wait for processing (check Terminal 2 for worker logs)

### Create an API Key

1. Go to the "API Keys" tab
2. Click "Create New API Key"
3. Copy the key (it's only shown once!)

### Query Your Bot

Using curl:

```bash
curl -X POST http://localhost:8000/v1/tenants/YOUR_TENANT_ID/query \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?"}'
```

Or using the streaming endpoint:

```bash
curl -N http://localhost:8000/v1/tenants/YOUR_TENANT_ID/query/stream?query=Hello \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Stopping the Platform

To stop all services:

```bash
./stop.sh
```

To stop and remove all data (including database):

```bash
docker-compose down -v
```

## Troubleshooting

### "Connection refused" errors
- Make sure Docker is running
- Check service status: `docker-compose ps`
- View logs: `docker-compose logs -f`
- Restart if needed: `docker-compose restart`

### "Invalid API key" errors
- Check that you copied the full key including the `wvr_` prefix
- Verify the key hasn't been revoked in the dashboard

### Services not starting
- Check Docker Desktop is running
- View specific service logs: `docker-compose logs -f api` (or worker, frontend)
- Rebuild images: `docker-compose build --no-cache`

### Database migration errors
- Migrations run automatically on first API startup
- To manually run: `docker-compose exec api psql -h postgres -U weaver -d weaver -f /app/app/db/models.sql`

### Worker not processing jobs
- Check worker logs: `docker-compose logs -f worker`
- Verify Redis is running: `docker-compose ps redis`
- Restart worker: `docker-compose restart worker`

## Next Steps

- Read [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system
- Check [README.md](./README.md) for detailed API documentation
- Review [CONTRIBUTING.md](./CONTRIBUTING.md) if you want to contribute
- Deploy to production using [scripts/deploy.sh](./scripts/deploy.sh)

## Getting Help

- Check the logs in all 3 terminals
- Visit http://localhost:8000/docs for API documentation
- Open an issue on GitHub
- Review the code comments for implementation details

Happy building! 🚀
````

## File: START_HERE.md
````markdown
# 🚀 Start Here - Weaver Quick Setup

Welcome to Weaver! Get your AI knowledge bot platform running in **under 5 minutes**.

## Prerequisites

- Docker Desktop installed and running
- Google Gemini API key
- Supabase account (for OAuth)

## Setup Steps

### 1. Get Your API Keys

**Google Gemini**:
- Visit https://makersuite.google.com/app/apikey
- Create API key

**Supabase**:
- Go to https://supabase.com
- Create project
- Get URL and anon key from Settings → API
- Enable Google OAuth in Authentication → Providers

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit with your credentials
nano .env  # or use your favorite editor
```

Required variables:
```bash
GOOGLE_API_KEY=your_gemini_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret
```

### 3. Start Everything

```bash
./start.sh
```

That's it! The script will:
- ✅ Build all containers
- ✅ Start PostgreSQL + Redis
- ✅ Run migrations
- ✅ Start API + Workers + Frontend
- ✅ Wait for everything to be ready

### 4. Access Your Platform

- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/metrics

### 5. Stop Everything

```bash
./stop.sh
```

## What You Get

✅ **Complete RAG System**
- Upload documents (PDF, DOCX, TXT, HTML)
- Automatic text extraction and chunking
- Vector embeddings with Gemini
- Semantic search with HNSW index
- AI-powered answers with source citations

✅ **Production-Ready Features**
- Multi-tenant isolation
- API key management
- Rate limiting (60 rpm)
- OAuth authentication
- Analytics dashboard
- Streaming responses
- Prometheus metrics

✅ **Developer Experience**
- Single command startup
- Auto migrations
- Hot reload in dev mode
- Comprehensive logging
- Health checks

## Next Steps

1. **Sign in** at http://localhost:3000
2. **Upload a document** in the dashboard
3. **Create an API key** in the API Keys tab
4. **Query your bot**:

```bash
curl -X POST http://localhost:8000/v1/tenants/YOUR_TENANT_ID/query \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?"}'
```

## Documentation

- **QUICKSTART.md** - Detailed setup guide
- **README.md** - API documentation
- **ARCHITECTURE.md** - System design
- **CHANGELOG.md** - Version history
- **MIGRATION_GUIDE.md** - Upgrade guide

## Troubleshooting

**Services won't start?**
```bash
docker-compose ps  # Check status
docker-compose logs -f  # View logs
```

**Need to reset everything?**
```bash
docker-compose down -v  # Remove all data
./start.sh  # Start fresh
```

## Support

- Check logs: `docker-compose logs -f [service]`
- View service status: `docker-compose ps`
- Restart service: `docker-compose restart [service]`

## What's New in v1.1.0

🎯 **Single Command Startup** - No more juggling multiple terminals
📊 **HNSW Index** - Better accuracy and performance than IVFFlat
🐳 **Fully Dockerized** - Frontend included, everything containerized
⚙️ **Simplified Config** - One .env file for everything

---

**Ready to build amazing AI bots?** Run `./start.sh` and let's go! 🚀
````

## File: start.sh
````bash
#!/bin/bash

set -e

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                        🚀 Starting Weaver Platform 🚀                       ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  IMPORTANT: Please edit .env with your actual credentials:"
    echo "   - GOOGLE_API_KEY (required for Gemini)"
    echo "   - SUPABASE_URL and SUPABASE_KEY (required for OAuth)"
    echo "   - GCS_BUCKET_NAME and GCS_PROJECT_ID (required for storage)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

echo "🐳 Starting Docker Compose services..."
echo ""

# Build and start all services
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
echo ""

# Wait for API to be healthy
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "   Waiting for API... (attempt $attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ API failed to start. Check logs with: docker-compose logs api"
    exit 1
fi

# Wait for frontend
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "   Waiting for Frontend... (attempt $attempt/$max_attempts)"
    sleep 2
done

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                     ✅ Weaver is now running! ✅                             ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Access Points:"
echo "   • Dashboard:  http://localhost:3000"
echo "   • API:        http://localhost:8000"
echo "   • API Docs:   http://localhost:8000/docs"
echo "   • Metrics:    http://localhost:8000/metrics"
echo ""
echo "📊 Services Status:"
docker-compose ps
echo ""
echo "📝 Useful Commands:"
echo "   • View logs:        docker-compose logs -f"
echo "   • View API logs:    docker-compose logs -f api"
echo "   • View worker logs: docker-compose logs -f worker"
echo "   • Stop services:    docker-compose down"
echo "   • Restart:          docker-compose restart"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
````

## File: stop.sh
````bash
#!/bin/bash

echo "🛑 Stopping Weaver Platform..."
echo ""

docker-compose down

echo ""
echo "✅ All services stopped!"
echo ""
echo "To remove all data (including database):"
echo "  docker-compose down -v"
````

## File: .github/workflows/deploy-cloudrun-dockerhub.yml
````yaml
name: CI/CD - Build, Push, Deploy (Cloud Run via Docker Hub)

on:
  push:
    branches: [ "main" ]

env:
  API_IMAGE_NAME: weaver-api
  WORKER_IMAGE_NAME: weaver-worker
  FRONTEND_IMAGE_NAME: weaver-frontend

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # API image (FastAPI backend)
      - name: Build and push API image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: infra/docker/Dockerfile
          target: api
          push: true
          tags: |
            docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.API_IMAGE_NAME }}:latest
            docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.API_IMAGE_NAME }}:sha-${{ github.sha }}

      # Worker image (Celery worker)
      - name: Build and push Worker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: infra/docker/Dockerfile
          target: worker
          push: true
          tags: |
            docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.WORKER_IMAGE_NAME }}:latest
            docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.WORKER_IMAGE_NAME }}:sha-${{ github.sha }}

      # Frontend image (Vite + Nginx)
      - name: Build and push Frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          file: ./frontend/Dockerfile
          push: true
          tags: |
            docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.FRONTEND_IMAGE_NAME }}:latest
            docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.FRONTEND_IMAGE_NAME }}:sha-${{ github.sha }}
          build-args: |
            VITE_API_URL=${{ secrets.FRONTEND_VITE_API_URL }}
            VITE_SUPABASE_URL=${{ secrets.FRONTEND_VITE_SUPABASE_URL }}
            VITE_SUPABASE_ANON_KEY=${{ secrets.FRONTEND_VITE_SUPABASE_ANON_KEY }}
            VITE_SITE_URL=${{ secrets.FRONTEND_VITE_SITE_URL }}
          no-cache: true

  deploy-api:
    needs: build-and-push
    runs-on: ubuntu-latest
    permissions:
      contents: read

    steps:
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}

      - name: Set up gcloud SDK
        uses: google-github-actions/setup-gcloud@v2
        with:
          version: latest

      - name: Configure project
        run: gcloud config set project ${{ secrets.GCP_PROJECT_ID }}

      - name: Deploy API to Cloud Run
        run: |
          gcloud run deploy ${{ secrets.CLOUD_RUN_API_SERVICE }} \
            --image docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.API_IMAGE_NAME }}:sha-${{ github.sha }} \
            --region ${{ secrets.GCP_REGION }} \
            --platform managed \
            --allow-unauthenticated \
            --port 8000 \
            --cpu 1 \
            --memory 1Gi \
            --min-instances 1 \
            --max-instances 10

  deploy-worker:
    needs: build-and-push
    runs-on: ubuntu-latest
    permissions:
      contents: read

    steps:
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}

      - name: Set up gcloud SDK
        uses: google-github-actions/setup-gcloud@v2
        with:
          version: latest

      - name: Configure project
        run: gcloud config set project ${{ secrets.GCP_PROJECT_ID }}

      - name: Deploy Worker to Cloud Run
        run: |
          gcloud run deploy ${{ secrets.CLOUD_RUN_WORKER_SERVICE }} \
            --image docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.WORKER_IMAGE_NAME }}:sha-${{ github.sha }} \
            --region ${{ secrets.GCP_REGION }} \
            --platform managed \
            --no-allow-unauthenticated \
            --port 8080 \
            --cpu 1 \
            --memory 1Gi \
            --min-instances 1 \
            --max-instances 1 \
            --no-cpu-throttling

  deploy-frontend:
    needs: build-and-push
    runs-on: ubuntu-latest
    permissions:
      contents: read

    steps:
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}

      - name: Set up gcloud SDK
        uses: google-github-actions/setup-gcloud@v2
        with:
          version: latest

      - name: Configure project
        run: gcloud config set project ${{ secrets.GCP_PROJECT_ID }}

      - name: Deploy Frontend to Cloud Run
        run: |
          gcloud run deploy ${{ secrets.CLOUD_RUN_FRONTEND_SERVICE }} \
            --image docker.io/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.FRONTEND_IMAGE_NAME }}:sha-${{ github.sha }} \
            --region ${{ secrets.GCP_REGION }} \
            --platform managed \
            --allow-unauthenticated \
            --port 3000 \
            --cpu 1 \
            --memory 512Mi \
            --min-instances 0 \
            --max-instances 5
````

## File: backend/alembic/versions/001_initial_schema.py
````python
"""initial schema

Revision ID: 001
Revises: 
Create Date: 2025-11-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('plan_tier', sa.String(50), server_default='free'),
        sa.Column('storage_used_bytes', sa.BigInteger, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    
    # Create users table (will be renamed to profiles in migration 002)
    # id is Supabase auth.users.id (no default - provided by application)
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('role', sa.String(50), server_default='member'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_users_tenant_id', 'users', ['tenant_id'])
    op.create_index('idx_users_email', 'users', ['email'])
    
    # Create bots table
    op.create_table(
        'bots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('config_json', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('tenant_id', name='bots_tenant_id_unique'),
    )
    op.create_index('idx_bots_tenant_id', 'bots', ['tenant_id'])
    
    # Create docs table
    op.create_table(
        'docs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(500), nullable=False),
        sa.Column('gcs_path', sa.String(1000), nullable=False),
        sa.Column('size_bytes', sa.BigInteger, nullable=False),
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('error_message', sa.Text),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_docs_tenant_id', 'docs', ['tenant_id'])
    op.create_index('idx_docs_status', 'docs', ['status'])
    
    # Create doc_chunks table
    op.create_table(
        'doc_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('doc_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('embedding', Vector(1536)),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('page_num', sa.Integer),
        sa.Column('chunk_index', sa.Integer, nullable=False),
        sa.Column('chunk_metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['doc_id'], ['docs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_doc_chunks_doc_id', 'doc_chunks', ['doc_id'])
    op.create_index('idx_doc_chunks_tenant_id', 'doc_chunks', ['tenant_id'])
    op.execute("""
        CREATE INDEX idx_doc_chunks_embedding ON doc_chunks 
        USING hnsw (embedding vector_cosine_ops) 
        WITH (m = 16, ef_construction = 64)
    """)
    
    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255)),
        sa.Column('key_hash', sa.String(255), nullable=False),
        sa.Column('rate_limit_rpm', sa.Integer, server_default='60'),
        sa.Column('revoked', sa.Boolean, server_default='false'),
        sa.Column('last_used_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_api_keys_tenant_id', 'api_keys', ['tenant_id'])
    op.create_index('idx_api_keys_revoked', 'api_keys', ['revoked'])
    
    # Create bot_queries table
    op.create_table(
        'bot_queries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('api_key_id', postgresql.UUID(as_uuid=True)),
        sa.Column('query', sa.Text, nullable=False),
        sa.Column('answer', sa.Text, nullable=False),
        sa.Column('confidence', sa.String(50)),
        sa.Column('latency_ms', sa.Integer),
        sa.Column('sources', postgresql.JSONB, server_default='[]'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['api_key_id'], ['api_keys.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_bot_queries_tenant_id', 'bot_queries', ['tenant_id'])
    op.create_index('idx_bot_queries_api_key_id', 'bot_queries', ['api_key_id'])
    op.create_index('idx_bot_queries_created_at', 'bot_queries', ['created_at'])
    op.create_index('idx_bot_queries_confidence', 'bot_queries', ['confidence'])
    
    # Create triggers for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    for table in ['tenants', 'users', 'bots', 'docs', 'api_keys']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at 
            BEFORE UPDATE ON {table} 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
        """)
    
    # Create trigger for auto-creating bot on tenant creation
    op.execute("""
        CREATE OR REPLACE FUNCTION create_bot_for_tenant()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO bots (id, tenant_id, name, config_json)
            VALUES (NEW.id, NEW.id, NEW.name || ' Bot', '{}')
            ON CONFLICT (tenant_id) DO NOTHING;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    op.execute("""
        CREATE TRIGGER create_bot_on_tenant_insert 
        AFTER INSERT ON tenants 
        FOR EACH ROW EXECUTE FUNCTION create_bot_for_tenant()
    """)


def downgrade() -> None:
    op.drop_table('bot_queries')
    op.drop_table('api_keys')
    op.drop_table('doc_chunks')
    op.drop_table('docs')
    op.drop_table('bots')
    op.drop_table('users')
    op.drop_table('tenants')
    
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column CASCADE')
    op.execute('DROP FUNCTION IF EXISTS create_bot_for_tenant CASCADE')
````

## File: backend/app/services/cache.py
````python
"""
Centralized Redis cache service with connection pooling
"""
import hashlib
import json
import logging
from typing import Optional, Any
from redis import Redis
from redis.exceptions import RedisError

from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Singleton Redis cache service"""
    
    _instance = None
    _redis_client: Optional[Redis] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Redis connection pool"""
        try:
            # Create a single connection pool shared across all cache operations
            self._redis_client = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=False,  # Handle encoding/decoding manually for flexibility
                max_connections=100,  # Increased pool size for concurrent workloads
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            # Test connection
            self._redis_client.ping()
            logger.info("Redis cache service initialized successfully")
        except RedisError as e:
            logger.warning(f"Failed to connect to Redis: {e}. Cache will be disabled.")
            self._redis_client = None
        except Exception as e:
            logger.error(f"Unexpected error initializing Redis: {e}. Cache will be disabled.")
            self._redis_client = None
    
    @property
    def is_available(self) -> bool:
        """Check if Redis is available"""
        return self._redis_client is not None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.is_available:
            return None
        
        try:
            value = self._redis_client.get(key)
            if value:
                # Decode bytes to string and parse JSON
                return json.loads(value.decode('utf-8'))
            return None
        except RedisError as e:
            logger.warning(f"Cache GET error for key '{key}': {e}")
            return None
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Cache value decode error for key '{key}': {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in cache with TTL in seconds"""
        if not self.is_available:
            return False
        
        try:
            # Encode value as JSON bytes
            encoded_value = json.dumps(value).encode('utf-8')
            self._redis_client.setex(key, ttl, encoded_value)
            return True
        except RedisError as e:
            logger.warning(f"Cache SET error for key '{key}': {e}")
            return False
        except (TypeError, ValueError) as e:
            logger.warning(f"Cache value encode error for key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.is_available:
            return False
        
        try:
            self._redis_client.delete(key)
            return True
        except RedisError as e:
            logger.warning(f"Cache DELETE error for key '{key}': {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern. Returns number of keys deleted."""
        if not self.is_available:
            return 0
        
        try:
            keys = self._redis_client.keys(pattern)
            if keys:
                return self._redis_client.delete(*keys)
            return 0
        except RedisError as e:
            logger.warning(f"Cache CLEAR error for pattern '{pattern}': {e}")
            return 0
    
    @staticmethod
    def generate_key(prefix: str, *args) -> str:
        """Generate a consistent cache key from prefix and arguments"""
        # Concatenate all args and create hash
        key_parts = [str(arg) for arg in args]
        key_string = ":".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get_stats(self) -> dict:
        """Get Redis cache statistics"""
        if not self.is_available:
            return {"available": False}
        
        try:
            info = self._redis_client.info("stats")
            return {
                "available": True,
                "total_connections": info.get("total_connections_received", 0),
                "total_commands": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
            }
        except RedisError as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return {"available": False, "error": str(e)}
    
    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)


# Singleton instance
cache_service = CacheService()
````

## File: backend/app/services/ingestion.py
````python
from uuid import UUID
from fastapi import UploadFile

from app.config import settings
from app.db.repositories import DocumentRepository
from app.workers.tasks import process_document
from app.services.storage import StorageService


class IngestionService:
    def __init__(self):
        self.doc_repo = DocumentRepository()
    
    async def upload_document(
        self,
        tenant_id: UUID,
        file: UploadFile,
    ) -> dict:
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size:
            raise ValueError(f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit")
        
        # Upload to GCS using S3-compatible API
        gcs_path = f"{tenant_id}/docs/{file.filename}"
        
        StorageService.upload_file(
            bucket_name=settings.GCS_BUCKET_NAME,
            key=gcs_path,
            content=content,
            content_type=file.content_type
        )
        
        doc_id = await self.doc_repo.create_document(
            tenant_id=tenant_id,
            filename=file.filename,
            gcs_path=gcs_path,
            size_bytes=file_size,
        )

        try:
            process_document.delay(str(doc_id), str(tenant_id), gcs_path)
        except Exception as e:
            # If enqueueing to Celery fails, mark document as failed instead of leaving it pending
            await self.doc_repo.update_status(doc_id, "failed", f"Enqueue error: {e}")
            raise
        
        return {
            "doc_id": doc_id,
            "filename": file.filename,
            "status": "pending",
        }
````

## File: backend/app/services/llm.py
````python
from typing import List, AsyncIterator, Optional, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings


class LLMService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",  
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=settings.LLM_TEMPERATURE,
        )
        
        # Default system prompt for bots without custom prompt
        self.default_system_prompt = """You are a helpful AI assistant that answers questions based on the provided context.
If the context doesn't contain enough information to answer the question, say "I don't know based on the available information."
Always cite the source documents when providing answers."""
    
    def build_prompt(self, query: str, context_chunks: List[dict], bot_config: Optional[Dict] = None) -> List:
        # Use bot-specific system prompt if available, otherwise use default
        if bot_config and "system_prompt" in bot_config:
            system_prompt = bot_config["system_prompt"]
        else:
            system_prompt = self.default_system_prompt
        
        context_text = "\n\n".join([
            f"[Source {i+1} - Page {chunk.get('page_num', 'N/A')}]:\n{chunk['text']}"
            for i, chunk in enumerate(context_chunks)
        ])
        
        user_prompt = f"""Context:
{context_text}

Question: {query}

Answer:"""
        
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    
    async def generate_answer(self, query: str, context_chunks: List[dict], bot_config: Optional[Dict] = None) -> str:
        try:
            messages = self.build_prompt(query, context_chunks, bot_config)
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")
    
    async def generate_answer_stream(
        self,
        query: str,
        context_chunks: List[dict],
        bot_config: Optional[Dict] = None,
    ) -> AsyncIterator[str]:
        try:
            messages = self.build_prompt(query, context_chunks, bot_config)
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            raise Exception(f"LLM streaming failed: {str(e)}")
````

## File: backend/app/services/retrieval.py
````python
import time
import logging
from typing import List
from uuid import UUID

from app.services.embeddings import EmbeddingService
from app.db.repositories import ChunkRepository
from app.config import settings

logger = logging.getLogger(__name__)


class RetrievalService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.chunk_repo = ChunkRepository()
    
    async def retrieve_context(
        self,
        tenant_id: UUID,
        query: str,
        top_k: int = None,
    ) -> List[dict]:
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        # Time embedding generation
        t1 = time.time()
        query_embedding = await self.embedding_service.embed_text(query)
        embedding_ms = int((time.time() - t1) * 1000)
        
        # Time vector search
        t2 = time.time()
        chunks = await self.chunk_repo.search_similar(
            tenant_id=tenant_id,
            query_embedding=query_embedding,
            top_k=top_k,
        )
        vector_search_ms = int((time.time() - t2) * 1000)
        
        logger.info(f"Retrieval breakdown - embedding:{embedding_ms}ms | vector_search:{vector_search_ms}ms | top_k:{top_k}")
        
        return chunks
````

## File: frontend/app/dashboard/page.tsx
````typescript
'use client'

import { useEffect, useState } from 'react'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import { Upload, Key, BarChart3, LogOut } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL

export default function Dashboard() {
  const router = useRouter()
  const supabase = createClientComponentClient()
  const [user, setUser] = useState<any>(null)
  const [tenantId, setTenantId] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('upload')

  useEffect(() => {
    const getUser = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) {
        router.push('/')
        return
      }
      setUser(session.user)
      
      try {
        const response = await axios.get(`${API_URL}/v1/users/me`, {
          headers: { Authorization: `Bearer ${session.access_token}` }
        })
        setTenantId(response.data.tenant_id)
      } catch (error: any) {
        console.error('Error fetching user data:', error)
        // If user not found, try to complete signup
        if (error.response?.status === 404) {
          try {
            const signupResponse = await axios.post(
              `${API_URL}/v1/auth/complete-signup`,
              {},
              { headers: { Authorization: `Bearer ${session.access_token}` } }
            )
            setTenantId(signupResponse.data.tenant_id)
          } catch (signupError) {
            console.error('Error completing signup:', signupError)
          }
        }
      }
      
      setLoading(false)
    }
    getUser()
  }, [router, supabase])

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    router.push('/')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-2xl font-bold">Weaver</h1>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">{user?.email}</span>
              <button
                onClick={handleSignOut}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
              >
                <LogOut size={20} />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-4 mb-8">
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              activeTab === 'upload'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Upload size={20} />
            Upload Documents
          </button>
          <button
            onClick={() => setActiveTab('keys')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              activeTab === 'keys'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Key size={20} />
            API Keys
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              activeTab === 'analytics'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            <BarChart3 size={20} />
            Analytics
          </button>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          {activeTab === 'upload' && <UploadTab tenantId={tenantId} />}
          {activeTab === 'keys' && <APIKeysTab tenantId={tenantId} />}
          {activeTab === 'analytics' && <AnalyticsTab tenantId={tenantId} />}
        </div>
      </div>
    </div>
  )
}

function UploadTab({ tenantId }: { tenantId: string }) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const supabase = createClientComponentClient()

  // Load documents on mount and setup polling
  useEffect(() => {
    if (tenantId) {
      loadDocuments()
      // Poll for document status updates every 5 seconds
      const interval = setInterval(loadDocuments, 5000)
      return () => clearInterval(interval)
    }
  }, [tenantId])

  const loadDocuments = async () => {
    if (!tenantId) return
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const response = await axios.get(
        `${API_URL}/v1/tenants/${tenantId}/docs`,
        {
          headers: { Authorization: `Bearer ${session?.access_token}` }
        }
      )
      setDocuments(response.data.documents)
    } catch (error) {
      console.error('Error loading documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async () => {
    if (!file) return
    if (!tenantId) {
      setMessage('Workspace not ready yet. Please wait...')
      return
    }

    setUploading(true)
    setMessage('')

    try {
      const { data: { session } } = await supabase.auth.getSession()
      const formData = new FormData()
      formData.append('file', file)

      await axios.post(
        `${API_URL}/v1/tenants/${tenantId}/docs:upload`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${session?.access_token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      setMessage('Document uploaded successfully! Processing in background...')
      setFile(null)
      // Clear file input
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement
      if (fileInput) fileInput.value = ''
      // Reload documents immediately
      loadDocuments()
    } catch (error: any) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setUploading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    }
    return badges[status as keyof typeof badges] || 'bg-gray-100 text-gray-800'
  }

  const getStatusIcon = (status: string) => {
    if (status === 'pending' || status === 'processing') {
      return (
        <svg className="animate-spin h-4 w-4 inline mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )
    }
    if (status === 'completed') {
      return <span className="mr-1">✓</span>
    }
    if (status === 'failed') {
      return <span className="mr-1">✗</span>
    }
    return null
  }

  const formatFileSize = (bytes: number) => {
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  if (!tenantId) {
    return (
      <div>
        <h2 className="text-2xl font-semibold mb-4">Upload Documents</h2>
        <p className="text-gray-600">Loading your workspace...</p>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Upload Documents</h2>
      <p className="text-gray-600 mb-6">
        Upload PDF, DOCX, TXT, or HTML files to train your bot (max 200MB)
      </p>
      
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-8">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          accept=".pdf,.docx,.doc,.txt,.html,.htm"
          className="mb-4"
        />
        
        {file && (
          <div className="mb-4">
            <p className="text-sm text-gray-600">Selected: {file.name}</p>
            <p className="text-xs text-gray-500">
              {(file.size / (1024 * 1024)).toFixed(2)} MB
            </p>
          </div>
        )}
        
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-2 px-6 rounded-lg"
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </div>
      
      {message && (
        <div className={`mb-6 p-4 rounded-lg ${
          message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
        }`}>
          {message}
        </div>
      )}

      {/* Documents List */}
      <div>
        <h3 className="text-xl font-semibold mb-4">Your Documents</h3>
        
        {loading ? (
          <p className="text-gray-600">Loading documents...</p>
        ) : documents.length === 0 ? (
          <p className="text-gray-600">No documents uploaded yet. Upload your first document above!</p>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <div key={doc.id} className="border rounded-lg p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h4 className="font-medium text-gray-900">{doc.filename}</h4>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(doc.status)}`}>
                        {getStatusIcon(doc.status)}
                        {doc.status}
                      </span>
                    </div>
                    <div className="mt-1 flex gap-4 text-sm text-gray-600">
                      <span>{formatFileSize(doc.size_bytes)}</span>
                      <span>Uploaded: {formatDate(doc.created_at)}</span>
                    </div>
                    {doc.error_message && (
                      <p className="mt-2 text-sm text-red-600">Error: {doc.error_message}</p>
                    )}
                    {doc.status === 'completed' && (
                      <p className="mt-2 text-sm text-green-600">
                        ✓ Ready for querying! Your bot can now answer questions about this document.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function APIKeysTab({ tenantId }: { tenantId: string }) {
  const [keys, setKeys] = useState<any[]>([])
  const [newKey, setNewKey] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [copied, setCopied] = useState(false)
  const supabase = createClientComponentClient()

  useEffect(() => {
    if (tenantId) {
      loadKeys()
    }
  }, [tenantId])

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const loadKeys = async () => {
    if (!tenantId) return
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const response = await axios.get(
        `${API_URL}/v1/tenants/${tenantId}/api-keys`,
        {
          headers: { Authorization: `Bearer ${session?.access_token}` },
        }
      )
      setKeys(response.data.keys)
    } catch (error) {
      console.error('Error loading keys:', error)
    } finally {
      setLoading(false)
    }
  }

  const createKey = async () => {
    if (!tenantId) return
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const response = await axios.post(
        `${API_URL}/v1/tenants/${tenantId}/api-keys`,
        { name: `Key ${new Date().toISOString()}` },
        {
          headers: { Authorization: `Bearer ${session?.access_token}` },
        }
      )
      setNewKey(response.data.key)
      loadKeys()
    } catch (error) {
      console.error('Error creating key:', error)
    }
  }

  const revokeKey = async (keyId: string) => {
    if (!tenantId) return
    try {
      const { data: { session } } = await supabase.auth.getSession()
      await axios.delete(
        `${API_URL}/v1/tenants/${tenantId}/api-keys/${keyId}`,
        {
          headers: { Authorization: `Bearer ${session?.access_token}` },
        }
      )
      loadKeys()
    } catch (error) {
      console.error('Error revoking key:', error)
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">API Keys</h2>
      
      {/* API Endpoint Information */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="font-semibold mb-2 text-blue-900">Bot API Endpoint</h3>
        <p className="text-sm text-gray-700 mb-2">Use this endpoint to query your bot:</p>
        <code className="block p-2 bg-white rounded font-mono text-sm mb-3">
          POST {API_URL}/v1/tenants/{tenantId}/query
        </code>
        <details className="text-sm">
          <summary className="cursor-pointer text-blue-700 hover:text-blue-900 font-medium mb-2">
            Show example code
          </summary>
          <div className="mt-2 p-3 bg-white rounded">
            <pre className="text-xs overflow-x-auto">
{`curl -X POST ${API_URL}/v1/tenants/${tenantId}/query \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "What is your product about?"}'`}
            </pre>
          </div>
        </details>
      </div>
      
      <button
        onClick={createKey}
        className="mb-6 bg-blue-900 hover:bg-blue-950 text-white font-semibold py-2 px-6 rounded-lg"
      >
        Create New API Key
      </button>
      
      {newKey && (
        <div className="mb-6 p-4 bg-yellow-100 border border-yellow-300 rounded-lg">
          <p className="font-semibold mb-2">New API Key (save this, it won't be shown again):</p>
          <div className="flex items-center gap-2">
            <code className="flex-1 p-2 bg-white rounded font-mono text-sm">{newKey}</code>
            <button
              onClick={() => copyToClipboard(newKey)}
              className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
              title="Copy to clipboard"
            >
              {copied ? (
                <span className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Copied!
                </span>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              )}
            </button>
          </div>
          <button
            onClick={() => setNewKey(null)}
            className="mt-2 text-sm text-gray-600 hover:text-gray-900"
          >
            Dismiss
          </button>
        </div>
      )}
      
      <div className="space-y-4">
        {keys.map((key) => (
          <div key={key.id} className="flex items-center justify-between p-4 border rounded-lg">
            <div>
              <p className="font-medium">{key.name || 'Unnamed Key'}</p>
              <p className="text-sm text-gray-600">
                Created: {new Date(key.created_at).toLocaleDateString()}
              </p>
              {key.last_used_at && (
                <p className="text-sm text-gray-600">
                  Last used: {new Date(key.last_used_at).toLocaleDateString()}
                </p>
              )}
              <p className="text-sm text-gray-600">
                Rate limit: {key.rate_limit_rpm} rpm
              </p>
            </div>
            <button
              onClick={() => revokeKey(key.id)}
              disabled={key.revoked}
              className={`px-4 py-2 rounded-lg ${
                key.revoked
                  ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                  : 'bg-red-600 hover:bg-red-700 text-white'
              }`}
            >
              {key.revoked ? 'Revoked' : 'Revoke'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

function AnalyticsTab({ tenantId }: { tenantId: string }) {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Analytics</h2>
      <p className="text-gray-600">
        Analytics dashboard coming soon. This will show query volume, latency, top queries, and more.
      </p>
    </div>
  )
}
````

## File: frontend/src/components/dashboard/AnalyticsTab.new.tsx
````typescript
import { useState } from 'react'
import { useBotConfig } from '@/hooks/useBot'
import { useQueryStats, useTopQueries, useUnansweredQueries } from '@/hooks/useAnalytics'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts'
import { BarChart3, TrendingUp, Clock, AlertCircle } from 'lucide-react'
import type { DailyStat, TopQuery, UnansweredQuery } from '@/types'

interface AnalyticsTabProps {
  tenantId: string
}

export default function AnalyticsTab({ tenantId }: AnalyticsTabProps) {
  const [timeRange, setTimeRange] = useState<'7' | '30' | '90'>('30')
  
  const { data: botConfig, isLoading: botLoading } = useBotConfig(tenantId)
  const { data: stats, isLoading: statsLoading } = useQueryStats(tenantId, timeRange)
  const { data: topQueries, isLoading: topLoading } = useTopQueries(tenantId)
  const { data: unanswered, isLoading: unansweredLoading } = useUnansweredQueries(tenantId)

  const isLoading = botLoading || statsLoading

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-64 mb-2" />
          <Skeleton className="h-4 w-48" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  const totalQueries =
    stats?.daily_stats?.reduce((sum: number, day: DailyStat) => sum + day.total_queries, 0) || 0

  const avgLatency = stats?.daily_stats?.length
    ? Math.round(
        stats.daily_stats.reduce(
          (sum: number, day: DailyStat) => sum + day.avg_latency_ms,
          0
        ) / stats.daily_stats.length
      )
    : 0

  const lowConfidenceCount =
    stats?.daily_stats?.reduce(
      (sum: number, day: DailyStat) => sum + day.low_confidence_count,
      0
    ) || 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold mb-2">Analytics</h2>
          {botConfig && (
            <p className="text-gray-600">
              Bot: <span className="font-medium">{botConfig.name}</span>
            </p>
          )}
        </div>
        <div className="w-48">
          <Select value={timeRange} onValueChange={(value: any) => setTimeRange(value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-6 bg-white border rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Total Queries</h3>
            <BarChart3 className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{totalQueries.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-1">Last {timeRange} days</p>
        </div>

        <div className="p-6 bg-white border rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Avg Latency</h3>
            <Clock className="w-5 h-5 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{avgLatency}ms</p>
          <p className="text-xs text-gray-500 mt-1">Response time</p>
        </div>

        <div className="p-6 bg-white border rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Low Confidence</h3>
            <AlertCircle className="w-5 h-5 text-yellow-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{lowConfidenceCount}</p>
          <p className="text-xs text-gray-500 mt-1">
            {totalQueries > 0 ? `${Math.round((lowConfidenceCount / totalQueries) * 100)}%` : '0%'} of
            total
          </p>
        </div>
      </div>

      {/* Query Volume Chart */}
      {stats?.daily_stats && stats.daily_stats.length > 0 && (
        <div className="p-6 bg-white border rounded-lg">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Query Volume
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={stats.daily_stats}>
              <defs>
                <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '6px' }}
                labelFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <Area
                type="monotone"
                dataKey="total_queries"
                stroke="#6366F1"
                strokeWidth={2}
                fill="url(#colorQueries)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Top Queries */}
      <div className="p-6 bg-white border rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Top Queries</h3>
        {topLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-12" />
            ))}
          </div>
        ) : topQueries && topQueries.length > 0 ? (
          <div className="space-y-2">
            {topQueries.map((item: TopQuery, index: number) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <p className="text-sm text-gray-700 flex-1">{item.query}</p>
                <span className="ml-4 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                  {item.count} {item.count === 1 ? 'time' : 'times'}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No queries yet</p>
        )}
      </div>

      {/* Unanswered/Low Confidence Queries */}
      <div className="p-6 bg-white border rounded-lg">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-yellow-600" />
          Low Confidence Queries
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          These queries received low-confidence answers. Consider adding more relevant documents.
        </p>
        {unansweredLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-12" />
            ))}
          </div>
        ) : unanswered && unanswered.length > 0 ? (
          <div className="space-y-2">
            {unanswered.map((item: UnansweredQuery, index: number) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border border-yellow-200"
              >
                <p className="text-sm text-gray-700 flex-1">{item.query}</p>
                <span className="ml-4 text-xs text-gray-500">
                  {new Date(item.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">
            No low-confidence queries — great job! 🎉
          </p>
        )}
      </div>
    </div>
  )
}
````

## File: frontend/src/components/dashboard/BotSettingsTab.tsx
````typescript
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Loader2, Sparkles, Info, CheckCircle2 } from 'lucide-react'
import { useBotConfig, useGenerateSystemPrompt, useUpdateBotConfig } from '@/hooks/useBot'
import { toast } from 'sonner'

interface BotSettingsTabProps {
  tenantId: string
}

export default function BotSettingsTab({ tenantId }: BotSettingsTabProps) {
  const [businessInfo, setBusinessInfo] = useState({
    businessName: '',
    industry: '',
    description: '',
    tone: 'professional',
    primaryGoal: '',
    specialInstructions: '',
  })
  
  const [generatedPrompt, setGeneratedPrompt] = useState('')
  const [showPrompt, setShowPrompt] = useState(false)
  
  const { data: botConfig, isLoading: isLoadingConfig } = useBotConfig(tenantId)
  const generateMutation = useGenerateSystemPrompt(tenantId)
  const updateMutation = useUpdateBotConfig(tenantId)
  
  // Load existing configuration if available
  useEffect(() => {
    if (botConfig?.config?.system_prompt) {
      setGeneratedPrompt(botConfig.config.system_prompt)
      setShowPrompt(true)
    }
    if (botConfig?.config?.business_info) {
      const info = botConfig.config.business_info
      setBusinessInfo({
        businessName: info.business_name || '',
        industry: info.industry || '',
        description: info.description || '',
        tone: info.tone || 'professional',
        primaryGoal: info.primary_goal || '',
        specialInstructions: info.special_instructions || '',
      })
    }
  }, [botConfig])
  
  const isFormValid = 
    businessInfo.businessName.trim() &&
    businessInfo.industry.trim() &&
    businessInfo.description.trim() &&
    businessInfo.primaryGoal.trim()
  
  const handleGenerate = async () => {
    try {
      const result = await generateMutation.mutateAsync({
        businessName: businessInfo.businessName,
        industry: businessInfo.industry,
        description: businessInfo.description,
        tone: businessInfo.tone,
        primaryGoal: businessInfo.primaryGoal,
        specialInstructions: businessInfo.specialInstructions || undefined,
      })
      setGeneratedPrompt(result.system_prompt)
      setShowPrompt(true)
      toast.success('System prompt generated successfully!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to generate prompt')
    }
  }
  
  const handleSave = async () => {
    try {
      await updateMutation.mutateAsync({
        system_prompt: generatedPrompt,
        business_info: businessInfo,
      })
      toast.success('Bot configuration saved successfully!')
      // Don't clear the form - keep the saved configuration visible
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to save configuration')
    }
  }
  
  if (isLoadingConfig) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  const hasExistingConfig = botConfig?.config?.system_prompt

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold mb-2">Configure Your Bot</h2>
        <p className="text-gray-600">
          Tell us about your business and we'll create the perfect bot personality
        </p>
      </div>

      {/* Current Configuration Status */}
      {hasExistingConfig && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-medium text-blue-900">Active Configuration</p>
                <p className="text-sm text-blue-700 mt-1">
                  Your bot currently has a custom system prompt. You can view it below or generate a new one.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-600" />
            Business Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Business Name */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Business/Product Name *
            </label>
            <Input
              placeholder="e.g., Acme Corp, MyProduct"
              value={businessInfo.businessName}
              onChange={(e) => setBusinessInfo({...businessInfo, businessName: e.target.value})}
            />
          </div>

          {/* Industry */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Industry *
            </label>
            <Input
              placeholder="e.g., SaaS, E-commerce, Healthcare, Legal"
              value={businessInfo.industry}
              onChange={(e) => setBusinessInfo({...businessInfo, industry: e.target.value})}
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium mb-2">
              What does your business do? *
            </label>
            <textarea
              className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={4}
              placeholder="Describe your business, products, or services in 2-3 sentences..."
              value={businessInfo.description}
              onChange={(e) => setBusinessInfo({...businessInfo, description: e.target.value})}
            />
          </div>

          {/* Tone Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Bot Personality *
            </label>
            <select
              className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={businessInfo.tone}
              onChange={(e) => setBusinessInfo({...businessInfo, tone: e.target.value})}
            >
              <option value="professional">Professional & Polished</option>
              <option value="friendly">Friendly & Conversational</option>
              <option value="technical">Technical & Precise</option>
              <option value="casual">Casual & Approachable</option>
              <option value="formal">Formal & Academic</option>
            </select>
          </div>

          {/* Primary Goal */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Primary Goal *
            </label>
            <Input
              placeholder="e.g., Answer customer support questions, Explain product features, Help with onboarding"
              value={businessInfo.primaryGoal}
              onChange={(e) => setBusinessInfo({...businessInfo, primaryGoal: e.target.value})}
            />
          </div>

          {/* Special Instructions (Optional) */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Special Instructions (Optional)
            </label>
            <textarea
              className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={3}
              placeholder="Any specific guidelines? e.g., 'Always include a disclaimer', 'Mention our 24/7 support', 'Use emojis'"
              value={businessInfo.specialInstructions}
              onChange={(e) => setBusinessInfo({...businessInfo, specialInstructions: e.target.value})}
            />
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-900">
              <p className="font-medium mb-1">How it works</p>
              <p>We'll generate an optimal system prompt based on your business information. You can review and edit it before saving.</p>
            </div>
          </div>

          {/* Generate Button */}
          <Button
            onClick={handleGenerate}
            disabled={!isFormValid || generateMutation.isPending}
            className="w-full"
            size="lg"
          >
            {generateMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating Your Bot's Personality...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Bot Configuration
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Generated Prompt Preview */}
      {showPrompt && generatedPrompt && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="text-green-900 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5" />
              System Prompt Generated
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2 text-green-900">
                Preview (You can edit if needed)
              </label>
              <textarea
                className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 font-mono text-sm bg-white"
                rows={10}
                value={generatedPrompt}
                onChange={(e) => setGeneratedPrompt(e.target.value)}
              />
            </div>

            <div className="flex gap-3">
              <Button 
                onClick={handleSave} 
                disabled={updateMutation.isPending}
                className="bg-green-600 hover:bg-green-700"
              >
                {updateMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save & Activate Bot'
                )}
              </Button>
              
              <Button 
                variant="outline" 
                onClick={handleGenerate} 
                disabled={generateMutation.isPending || !isFormValid}
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Regenerate
              </Button>
              
              <Button 
                variant="ghost" 
                onClick={() => setShowPrompt(false)}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Examples Section */}
      {!showPrompt && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Example Use Cases</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="border-l-4 border-blue-500 pl-4">
              <p className="font-medium">SaaS Product Support</p>
              <p className="text-gray-600 mt-1">
                <strong>Tone:</strong> Professional & Polished<br />
                <strong>Goal:</strong> Answer customer questions about features, pricing, and integrations
              </p>
            </div>
            
            <div className="border-l-4 border-purple-500 pl-4">
              <p className="font-medium">E-commerce Store</p>
              <p className="text-gray-600 mt-1">
                <strong>Tone:</strong> Friendly & Conversational<br />
                <strong>Goal:</strong> Help customers find products and answer shipping/return questions
              </p>
            </div>
            
            <div className="border-l-4 border-green-500 pl-4">
              <p className="font-medium">Technical Documentation</p>
              <p className="text-gray-600 mt-1">
                <strong>Tone:</strong> Technical & Precise<br />
                <strong>Goal:</strong> Provide accurate API documentation and code examples
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
````

## File: frontend/src/main.tsx
````typescript
import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'

const rootElement = document.getElementById('root')

if (rootElement) {
  createRoot(rootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  )
}
````

## File: frontend/Dockerfile
````
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Debug: List copied files
RUN ls -la src/lib/ || echo "src/lib does not exist"

# Build args for environment variables
ARG VITE_API_URL
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ARG VITE_SITE_URL

# Set environment variables for build
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY
ENV VITE_SITE_URL=$VITE_SITE_URL

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
````

## File: frontend/index.html
````html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Weaver - AI Knowledge Bot Platform</title>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-PFNYJ5DXPF"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-PFNYJ5DXPF');
    </script>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
````

## File: frontend/vite.config.ts
````typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
    extensions: ['.ts', '.tsx', '.js', '.jsx', '.json'],
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    watch: {
      usePolling: true,
    },
  },
})
````

## File: infra/docker/Dockerfile
````
FROM python:3.12-slim as base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    redis-tools \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base as api

COPY backend/app /app/app
COPY backend/alembic.ini /app/alembic.ini
COPY backend/alembic /app/alembic
COPY backend/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

FROM base as worker

COPY backend/app /app/app
COPY worker /app/worker
COPY worker/entrypoint.sh /app/entrypoint.sh
COPY worker/health_server.py /app/health_server.py

RUN chmod +x /app/entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]
````

## File: worker/celery.py
````python
from celery import Celery
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from app.config import settings


def _ensure_rediss_ssl_params(url: str) -> str:
  """
  Celery's Redis backend requires rediss:// URLs to specify ssl_cert_reqs.
  Upstash uses TLS with CA verification, so we set ssl_cert_reqs=required if missing.
  """
  if not url.startswith("rediss://"):
    return url

  parsed = urlparse(url)
  query = dict(parse_qsl(parsed.query))

  if "ssl_cert_reqs" not in query:
    # Use 'required' to validate server certs (recommended for Upstash)
    query["ssl_cert_reqs"] = "required"

  new_query = urlencode(query)
  return urlunparse(parsed._replace(query=new_query))


redis_url = _ensure_rediss_ssl_params(settings.REDIS_URL)

celery_app = Celery(
    "weaver",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)

celery_app.autodiscover_tasks(["app.workers"])
````

## File: .gitignore
````
.env
.env.local
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
backend/lib/
worker/lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

.pytest_cache/
.coverage
htmlcov/

node_modules/
.next/
out/
.DS_Store
*.pem

.vscode/
.idea/
*.swp
*.swo
````

## File: README.md
````markdown
# Weaver - AI-Powered Knowledge Bot Platform

Weaver enables businesses to create and deploy AI customer-service bots trained on their own documents.

## Architecture

- **Backend**: FastAPI (Python 3.12)
- **Workers**: Celery + Redis
- **Database**: PostgreSQL + pgvector (HNSW index)
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Storage**: Google Cloud Storage (HMAC keys)
- **LLM**: Google Gemini (via LangChain)
- **Auth**: Supabase OAuth
- **Frontend**: React 18 + Vite + TypeScript
- **State Management**: Zustand + TanStack Query
- **Styling**: Tailwind CSS + shadcn/ui

## Features

- One bot per tenant architecture
- **AI-powered bot configuration** - Generate system prompts from simple business info (no prompt engineering needed)
- **Shared demo bot** for instant user onboarding (no document upload required)
- API key authentication
- Document ingestion (PDF, DOCX, TXT, HTML)
- RAG-based query answering
- Rate limiting (60 rpm per key)
- **Daily query limits** (50 queries/day, configurable)
- Real-time streaming responses
- Analytics dashboard
- **High-performance query engine (1.5-3s average latency)**
- **Redis caching for embeddings and queries**
- **Optimized HNSW vector search**

## Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL with pgvector
- Redis
- Google Cloud account
- Supabase account

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/weaver
REDIS_URL=redis://localhost:6379/0
GOOGLE_API_KEY=your_gemini_api_key
GCS_BUCKET_NAME=weaver-docs
GCS_PROJECT_ID=your_gcp_project
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

### Local Development

1. **Copy and configure environment variables**:

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

2. **Start everything with a single command**:

```bash
./start.sh
```

That's it! The script will:
- Build all Docker images
- Start PostgreSQL, Redis, API, Worker, and Frontend
- Run Alembic migrations automatically
- Wait for all services to be ready

Visit http://localhost:3000

**Note**: Migrations are now managed by Alembic (not raw SQL). See `SQLALCHEMY_MIGRATION.md` for details.

3. **To stop everything**:

```bash
./stop.sh
```

## API Endpoints

### Query Bot

```bash
POST /v1/tenants/{tenant_id}/query
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
  "query": "How do I reset my password?"
}
```

### Stream Query

```bash
GET /v1/tenants/{tenant_id}/query/stream?query=<query>
Authorization: Bearer <API_KEY>
```

### Upload Document

```bash
POST /v1/tenants/{tenant_id}/docs:upload
Authorization: Bearer <SESSION_TOKEN>
Content-Type: multipart/form-data

file: <file>
```

### Manage API Keys

```bash
# Create
POST /v1/tenants/{tenant_id}/api-keys
Authorization: Bearer <SESSION_TOKEN>

# List
GET /v1/tenants/{tenant_id}/api-keys
Authorization: Bearer <SESSION_TOKEN>

# Revoke
DELETE /v1/tenants/{tenant_id}/api-keys/{key_id}
Authorization: Bearer <SESSION_TOKEN>
```

### Configure Bot Personality

```bash
# Generate system prompt from business info (AI-powered)
POST /v1/tenants/{tenant_id}/bot/generate-prompt
Authorization: Bearer <SESSION_TOKEN>
Content-Type: application/json

{
  "business_name": "Acme Corp",
  "industry": "E-commerce",
  "description": "We sell premium widgets online",
  "tone": "friendly",
  "primary_goal": "Help customers find products",
  "special_instructions": "Always mention free shipping over $50"
}

# Update bot configuration
PUT /v1/tenants/{tenant_id}/bot
Authorization: Bearer <SESSION_TOKEN>
Content-Type: application/json

{
  "system_prompt": "You are Acme Corp's AI assistant...",
  "business_info": { ... }
}
```

**See also:**
- `BOT_SETTINGS_QUICK_START.md` - User guide
- `BUSINESS_INFO_PROMPT_GENERATION.md` - Technical details

## Deployment

### Build Docker Images

```bash
docker build -t gcr.io/PROJECT_ID/weaver-api:latest -f infra/docker/Dockerfile --target api .
docker build -t gcr.io/PROJECT_ID/weaver-worker:latest -f infra/docker/Dockerfile --target worker .
```

### Push to GCR

```bash
docker push gcr.io/PROJECT_ID/weaver-api:latest
docker push gcr.io/PROJECT_ID/weaver-worker:latest
```

### Deploy to Cloud Run

```bash
gcloud run services replace infra/deploy/cloudrun.yaml
```

## Database Migrations

Weaver uses **Alembic** for database migrations:

```bash
# Check current migration version
alembic current

# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "description"

# Rollback one migration
alembic downgrade -1
```

See `SQLALCHEMY_MIGRATION.md` for complete guide.

## Testing

```bash
cd backend
pytest tests/
```

## Monitoring

- Prometheus metrics: `/metrics`
- Health check: `/health`
- Sentry for error tracking
- Performance logs: `docker logs weaver-api-1 | grep "Query performance"`
- Cache metrics: `docker exec -it weaver-redis-1 redis-cli INFO stats`

## Performance

Weaver is optimized for production use with:
- **1.5-3s average query latency** (down from 10.9s)
- **<100ms for cached queries**
- **40-60% cost reduction** on LLM/embedding API calls
- **Redis caching** for embeddings and full query results
- **Optimized HNSW index** for fast vector search
- **Efficient connection pooling** and database indexes

For details, see:
- `PERFORMANCE_OPTIMIZATIONS.md` - Technical documentation
- `APPLY_PERFORMANCE_FIXES.md` - Quick start guide
- `PERFORMANCE_CHANGES_SUMMARY.md` - Changes overview

## Demo Bot

Weaver includes a **shared demo bot** that allows new users to test the platform immediately without uploading documents.

### Key Features
- ✅ All users can query the demo bot using their own API keys
- ✅ Queries count toward the user's personal daily limit (50/day)
- ✅ No setup required - works right after signup
- ✅ Helps users understand RAG capabilities before uploading own docs
- ✅ Seamless switch between demo bot and own bot

### Setup
1. Create admin user in Supabase Dashboard
2. Set `DEMO_BOT_ADMIN_UUID` and `DEMO_BOT_ADMIN_EMAIL` in `.env`
3. Run migrations: `docker-compose exec api alembic upgrade head`
4. Login as admin and upload demo content (PDFs about Weaver, RAG, API docs)
5. Users can now select "Demo Bot" in the API Keys tab

For complete setup instructions, see:
- `DEMO_BOT_ADMIN_SETUP.md` - Quick start (5 minutes)
- `DEMO_BOT_SETUP.md` - Comprehensive guide
- `DEMO_BOT_IMPLEMENTATION.md` - Technical overview

## License

Proprietary
````

## File: start-dev.sh
````bash
#!/bin/bash
set -e

echo "🚀 Starting Weaver in DEVELOPMENT mode..."
echo "   - Backend: Hot-reload enabled (volume mounted)"
echo "   - Worker: Hot-reload enabled (volume mounted)"
echo "   - Frontend: Hot-reload enabled (Vite dev server)"
echo ""

# Start services with dev override
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

echo ""
echo "✅ Development environment started!"
echo "   - Frontend: http://localhost:3000"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
````

## File: backend/app/api/v1/routes.py
````python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from uuid import UUID

from app.api.v1.schemas import (
    QueryRequest,
    QueryResponse,
    APIKeyCreate,
    APIKeyResponse,
    APIKeyListResponse,
    DocumentUploadResponse,
    DocumentListResponse,
    BotConfigResponse,
    SignupResponse,
    UserMeResponse,
    BusinessInfoRequest,
    GeneratedPromptResponse,
    BotConfigUpdate,
    BotSettingsResponse,
)
from app.auth.api_key import verify_api_key
from app.auth.types import APIKeyData
from app.auth.oauth import get_current_user, verify_supabase_token, require_admin_or_owner, User
from app.services.query import QueryService
from app.services.ingestion import IngestionService
from app.db.repositories import (
    APIKeyRepository,
    DocumentRepository,
    BotRepository,
    TenantRepository,
    ProfileRepository,
)
from app.middleware.rate_limit import check_rate_limit
from app.services.cache import cache_service
from app.services.rate_limit import daily_limit_service
from app.config import settings
from app.api.v1 import analytics


router = APIRouter()
router.include_router(analytics.router, tags=["analytics"])


@router.post("/auth/complete-signup", response_model=SignupResponse)
async def complete_signup(auth_data: dict = Depends(verify_supabase_token)):
    """
    Complete signup after OAuth - creates tenant, user profile, and bot if first time
    Called by frontend after successful Supabase OAuth
    """
    profile_repo = ProfileRepository()
    tenant_repo = TenantRepository()
    
    user_id = auth_data["id"]
    email = auth_data["email"]
    
    # Check if user profile already exists
    existing_profile = await profile_repo.get_by_id(user_id)
    
    if existing_profile:
        # User already exists, return existing data
        return SignupResponse(
            tenant_id=existing_profile["tenant_id"],
            user_id=existing_profile["id"],
            email=existing_profile["email"],
            role=existing_profile["role"],
            is_new_user=False,
            message="Welcome back!"
        )
    
    # New user - create tenant, user profile, and bot
    # Extract tenant name from email (before @)
    tenant_name = email.split('@')[0].capitalize()
    
    # Create tenant (this will auto-create bot via trigger)
    tenant_id = await tenant_repo.create(name=f"{tenant_name}'s Workspace")
    
    # Create user profile in our database
    await profile_repo.create(
        user_id=user_id,
        tenant_id=tenant_id,
        email=email,
        role="owner"
    )
    
    return SignupResponse(
        tenant_id=tenant_id,
        user_id=user_id,
        email=email,
        role="owner",
        is_new_user=True,
        message="Account created successfully!"
    )


@router.get("/users/me", response_model=UserMeResponse)
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserMeResponse(
        user_id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        role=user.role
    )


@router.post("/tenants/{tenant_id}/query", response_model=QueryResponse)
async def query_bot(
    tenant_id: UUID,
    request: QueryRequest,
    api_key_data: APIKeyData = Depends(verify_api_key),
):
    # Allow access to demo bot OR user's own tenant
    demo_bot_id = UUID(settings.DEMO_BOT_TENANT_ID) if settings.DEMO_BOT_ENABLED else None
    
    if tenant_id != api_key_data.tenant_id:
        # Check if querying demo bot
        if not (demo_bot_id and tenant_id == demo_bot_id):
            raise HTTPException(status_code=403, detail="Access denied. You can only query your own bot or the demo bot.")
    
    # Check rate limit (per minute)
    await check_rate_limit(api_key_data)
    
    # Check daily query limit - ALWAYS use user's tenant_id (not demo bot's)
    limit_info = await daily_limit_service.check_and_increment(api_key_data.tenant_id)
    
    query_service = QueryService()
    result = await query_service.query(
        tenant_id=tenant_id,  # Can be demo bot or user's own bot
        query=request.query,
        api_key_id=api_key_data.key_id,
    )
    
    # Add limit info to response
    result.daily_usage = limit_info
    
    return result


@router.get("/tenants/{tenant_id}/query/stream")
async def query_bot_stream(
    tenant_id: UUID,
    query: str,
    api_key_data: APIKeyData = Depends(verify_api_key),
):
    # Allow access to demo bot OR user's own tenant
    demo_bot_id = UUID(settings.DEMO_BOT_TENANT_ID) if settings.DEMO_BOT_ENABLED else None
    
    if tenant_id != api_key_data.tenant_id:
        # Check if querying demo bot
        if not (demo_bot_id and tenant_id == demo_bot_id):
            raise HTTPException(status_code=403, detail="Access denied. You can only query your own bot or the demo bot.")
    
    # Check rate limit (per minute)
    await check_rate_limit(api_key_data)
    
    # Check daily query limit - ALWAYS use user's tenant_id (not demo bot's)
    await daily_limit_service.check_and_increment(api_key_data.tenant_id)
    
    query_service = QueryService()
    stream = query_service.query_stream(
        tenant_id=tenant_id,  # Can be demo bot or user's own bot
        query=query,
        api_key_id=api_key_data.key_id,
    )
    
    return StreamingResponse(stream, media_type="text/event-stream")


@router.post("/tenants/{tenant_id}/docs:upload", response_model=DocumentUploadResponse)
async def upload_document(
    tenant_id: UUID,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    ingestion_service = IngestionService()
    result = await ingestion_service.upload_document(
        tenant_id=tenant_id,
        file=file,
    )
    
    return result


@router.get("/tenants/{tenant_id}/docs", response_model=DocumentListResponse)
async def list_documents(
    tenant_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, description="Filter by document status"),
    user: User = Depends(get_current_user),
):
    """List all documents for a tenant"""
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    doc_repo = DocumentRepository()
    repo_data = await doc_repo.list_by_tenant(
        tenant_id,
        limit=limit,
        offset=offset,
        status=status,
    )

    return DocumentListResponse(
        documents=repo_data['documents'],
        total=repo_data['total'],
        limit=repo_data['limit'],
        offset=repo_data['offset'],
        status_filter=repo_data['status_filter']
    )


@router.get("/tenants/{tenant_id}/bot", response_model=BotConfigResponse)
async def get_bot_config(
    tenant_id: UUID,
    user: User = Depends(get_current_user),
):
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    bot_repo = BotRepository()
    bot = await bot_repo.get_by_tenant_id(tenant_id)
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    return bot


@router.post("/tenants/{tenant_id}/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    tenant_id: UUID,
    request: APIKeyCreate,
    user: User = Depends(get_current_user),
):
    require_admin_or_owner(user, tenant_id)
    
    api_key_repo = APIKeyRepository()
    result = await api_key_repo.create_key(
        tenant_id=tenant_id,
        name=request.name,
        rate_limit_rpm=request.rate_limit_rpm,
    )
    
    return result


@router.get("/tenants/{tenant_id}/api-keys", response_model=APIKeyListResponse)
async def list_api_keys(
    tenant_id: UUID,
    user: User = Depends(get_current_user),
):
    require_admin_or_owner(user, tenant_id)
    
    api_key_repo = APIKeyRepository()
    keys = await api_key_repo.list_keys(tenant_id)
    
    return {"keys": keys}


@router.delete("/tenants/{tenant_id}/api-keys/{key_id}")
async def revoke_api_key(
    tenant_id: UUID,
    key_id: UUID,
    user: User = Depends(get_current_user),
):
    require_admin_or_owner(user, tenant_id)
    
    api_key_repo = APIKeyRepository()
    await api_key_repo.revoke_key(tenant_id, key_id)
    
    return {"status": "revoked"}


@router.get("/cache/stats")
async def get_cache_stats(user: User = Depends(get_current_user)):
    """
    Get cache statistics (admin/monitoring endpoint)
    """
    stats = cache_service.get_stats()
    return stats


@router.get("/tenants/{tenant_id}/usage/daily")
async def get_daily_usage(
    tenant_id: UUID,
    user: User = Depends(get_current_user),
):
    """
    Get current daily query usage for a tenant
    """
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    
    usage = await daily_limit_service.get_current_usage(tenant_id)
    return usage


@router.post("/tenants/{tenant_id}/bot/generate-prompt", response_model=GeneratedPromptResponse)
async def generate_system_prompt(
    tenant_id: UUID,
    request: BusinessInfoRequest,
    user: User = Depends(get_current_user),
):
    """
    Generate optimal system prompt from business information using LLM
    """
    require_admin_or_owner(user, tenant_id)
    
    from app.services.prompt_generator import PromptGeneratorService
    
    generator = PromptGeneratorService()
    system_prompt = await generator.generate_from_business_info(
        business_name=request.business_name,
        industry=request.industry,
        description=request.description,
        tone=request.tone,
        primary_goal=request.primary_goal,
        special_instructions=request.special_instructions,
    )
    
    return GeneratedPromptResponse(
        system_prompt=system_prompt,
        business_info=request.dict(),
    )


@router.put("/tenants/{tenant_id}/bot", response_model=BotSettingsResponse)
async def update_bot_config(
    tenant_id: UUID,
    request: BotConfigUpdate,
    user: User = Depends(get_current_user),
):
    """
    Update bot configuration (system prompt, business info, etc.)
    """
    require_admin_or_owner(user, tenant_id)
    
    bot_repo = BotRepository()
    
    # Get existing bot
    bot = await bot_repo.get_by_tenant(tenant_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Update config_json
    current_config = bot.get("config", {})
    
    # Update system_prompt if provided
    if request.system_prompt is not None:
        if request.system_prompt.strip():
            current_config["system_prompt"] = request.system_prompt.strip()
        else:
            # Empty string = remove custom prompt, use default
            current_config.pop("system_prompt", None)
    
    # Update business_info if provided
    if request.business_info is not None:
        current_config["business_info"] = request.business_info
    
    # Update bot in database
    await bot_repo.update_config(tenant_id, current_config)
    
    # Return updated config
    updated_bot = await bot_repo.get_by_tenant(tenant_id)
    return BotSettingsResponse(
        tenant_id=str(tenant_id),
        name=updated_bot["name"],
        system_prompt=updated_bot["config"].get("system_prompt"),
        business_info=updated_bot["config"].get("business_info"),
        using_default_prompt=("system_prompt" not in updated_bot["config"]),
        created_at=updated_bot["created_at"].isoformat(),
        updated_at=updated_bot["updated_at"].isoformat(),
    )
````

## File: backend/app/services/embeddings.py
````python
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings
from app.services.cache import cache_service


class EmbeddingService:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=settings.GOOGLE_API_KEY,
            task_type="retrieval_document",
        )
        self.cache_ttl = 3600  # 1 hour cache
    
    async def embed_text(self, text: str) -> List[float]:
        try:
            # Try cache first
            cache_key = cache_service.generate_key("emb", text.lower().strip())
            cached = cache_service.get(cache_key)
            if cached:
                return cached
            
            # Generate embedding
            embedding = await self.embeddings.aembed_query(
                text,
                output_dimensionality=1536
            )
            
            # Cache for future use
            cache_service.set(cache_key, embedding, self.cache_ttl)
            
            return embedding
        except Exception as e:
            raise Exception(f"Embedding generation failed: {str(e)}")
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            # Check cache for each text first
            cached_embeddings = []
            uncached_texts = []
            uncached_indices = []
            
            for i, text in enumerate(texts):
                cache_key = cache_service.generate_key("emb", text.lower().strip())
                cached = cache_service.get(cache_key)
                if cached:
                    cached_embeddings.append((i, cached))
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
            
            # Generate embeddings only for uncached texts
            if uncached_texts:
                new_embeddings = await self.embeddings.aembed_documents(
                    uncached_texts,
                    output_dimensionality=1536
                )
                
                # Cache new embeddings
                for text, embedding in zip(uncached_texts, new_embeddings):
                    cache_key = cache_service.generate_key("emb", text.lower().strip())
                    cache_service.set(cache_key, embedding, self.cache_ttl)
                
                # Merge cached and new embeddings in correct order
                result = [None] * len(texts)
                for i, emb in cached_embeddings:
                    result[i] = emb
                for i, emb in zip(uncached_indices, new_embeddings):
                    result[i] = emb
                
                return result
            
            # All cached - reconstruct in order
            result = [None] * len(texts)
            for i, emb in cached_embeddings:
                result[i] = emb
            return result
            
        except Exception as e:
            raise Exception(f"Batch embedding generation failed: {str(e)}")
````

## File: backend/app/workers/db.py
````python
"""
Worker-specific database connection configuration.

Workers use Transaction Mode (port 6543) for higher connection limits,
while the API uses Session Mode (port 5432) for prepared statements.

IMPORTANT: Workers use NullPool to avoid connection pool persistence issues
with asyncio.run() creating fresh event loops per task.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.config import settings


def _assert_worker_uses_transaction_mode() -> None:
    url = settings.worker_db_url
    if ":6543/" not in url:
        raise RuntimeError(f"Worker DB URL is not using Transaction Mode port 6543: {url}")


_assert_worker_uses_transaction_mode()
worker_db_url = settings.worker_db_url


# Worker engine configured for Transaction Mode (pgbouncer)
# - Uses WORKER_DATABASE_URL (port 6543)
# - Disables prepared statements (required for pgbouncer transaction mode)
# - Uses NullPool to prevent connection reuse across different event loops
#   (each asyncio.run() creates a new loop, so pooled connections become invalid)
worker_engine = create_async_engine(
    worker_db_url,
    echo=False,
    poolclass=NullPool,  # No connection pooling - create fresh connections per task
    execution_options={
        "compiled_cache": None,  # Disable SQLAlchemy's compiled statement cache
    },
    connect_args={
        "server_settings": {
            "jit": "off",
        },
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "prepared_statement_name_func": lambda: None,
    },
)

WorkerAsyncSessionLocal = sessionmaker(
    worker_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
````

## File: backend/app/config.py
````python
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API uses Session Mode (port 5432) - prepared statements enabled
    DATABASE_URL: str
    # Workers use Transaction Mode (port 6543) - high connection limit
    WORKER_DATABASE_URL: Optional[str] = None
    REDIS_URL: str
    
    GOOGLE_API_KEY: str
    GCS_BUCKET_NAME: str
    GCS_ACCESS_KEY: str  # HMAC Access Key
    GCS_SECRET_KEY: str  # HMAC Secret
    
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    
    SENTRY_DSN: Optional[str] = None
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    RATE_LIMIT_RPM: int = 60
    MAX_FILE_SIZE_MB: int = 200
    MAX_TENANT_STORAGE_GB: int = 2
    MAX_QUERIES_PER_DAY: int = 50  # Daily query limit per bot
    
    CHUNK_SIZE: int = 500  # Reduced from 800 for faster LLM processing
    CHUNK_OVERLAP_PCT: int = 10  # Reduced from 20
    TOP_K_RESULTS: int = 3  # Reduced from 8 for faster retrieval
    LLM_TEMPERATURE: float = 0.2
    
    # Demo Bot Configuration
    DEMO_BOT_TENANT_ID: str = "00000000-0000-0000-0000-000000000000"
    DEMO_BOT_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def worker_db_url(self) -> str:
        """Get worker database URL, fallback to main DATABASE_URL if not set."""
        return self.WORKER_DATABASE_URL or self.DATABASE_URL


settings = Settings()
````

## File: frontend/src/pages/Dashboard.tsx
````typescript
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { LogOut, Upload as UploadIcon, Key, BarChart3, Settings } from 'lucide-react'
import UploadTab from '@/components/dashboard/UploadTab'
import APIKeysTab from '@/components/dashboard/APIKeysTab'
import AnalyticsTab from '@/components/dashboard/AnalyticsTab'
import BotSettingsTab from '@/components/dashboard/BotSettingsTab'

export default function Dashboard() {
  const navigate = useNavigate()
  const { session, user, loading, signOut } = useAuthStore()
  const [activeTab, setActiveTab] = useState('upload')

  useEffect(() => {
    if (!session && !loading) {
      navigate('/')
    }
  }, [session, loading, navigate])

  const handleSignOut = async () => {
    await signOut()
    navigate('/')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Setting up your workspace...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-2xl font-bold text-blue-900 bg-clip-text">
              Weaver
            </h1>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">{user.email}</span>
              <Button
                onClick={handleSignOut}
                variant="ghost"
                size="sm"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-8">
            <TabsTrigger value="upload">
              <UploadIcon className="w-4 h-4 mr-2" />
              Upload Documents
            </TabsTrigger>
            <TabsTrigger value="keys">
              <Key className="w-4 h-4 mr-2" />
              API Keys
            </TabsTrigger>
            <TabsTrigger value="settings">
              <Settings className="w-4 h-4 mr-2" />
              Bot Settings
            </TabsTrigger>
            <TabsTrigger value="analytics">
              <BarChart3 className="w-4 h-4 mr-2" />
              Analytics
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload">
            <Card>
              <CardContent className="pt-6">
                <UploadTab tenantId={user.tenant_id} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="keys">
            <Card>
              <CardContent className="pt-6">
                <APIKeysTab tenantId={user.tenant_id} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings">
            <Card>
              <CardContent className="pt-6">
                <BotSettingsTab tenantId={user.tenant_id} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics">
            <Card>
              <CardContent className="pt-6">
                <AnalyticsTab tenantId={user.tenant_id} />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
````

## File: frontend/src/types/index.ts
````typescript
export interface User {
  id: string
  email: string
  tenant_id: string
  role: string
}

export interface Document {
  id: string
  filename: string
  size_bytes: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error_message?: string
  created_at: string
  updated_at: string
}

export interface DocumentListResponse {
  documents: Document[]
  total: number
  limit: number
  offset: number
  status_filter?: string | null
}

export interface APIKey {
  id: string
  name: string
  created_at: string
  last_used_at?: string
  rate_limit_rpm: number
  revoked: boolean
}

export interface CreateAPIKeyResponse {
  key: string
  id: string
}

export interface BotConfig {
  id: string
  tenant_id: string
  name: string
  config: Record<string, any>
  created_at: string
}

export interface DailyStat {
  date: string
  total_queries: number
  avg_latency_ms: number
  low_confidence_count: number
}

export interface QueryStatsResponse {
  daily_stats: DailyStat[]
}

export interface TopQuery {
  query: string
  count: number
}

export interface UnansweredQuery {
  query: string
  created_at: string
}
````

## File: frontend/src/App.tsx
````typescript
import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useAuthStore } from '@/store/authStore'
import { Toaster } from '@/components/ui/sonner'
import Login from '@/pages/Login'
import AuthCallback from '@/pages/AuthCallback'
import Dashboard from '@/pages/Dashboard'
import { pageview } from '@/lib/gtag'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { session, loading } = useAuthStore()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    )
  }

  if (!session) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

function AppRoutes() {
  const initialize = useAuthStore((state) => state.initialize)
  const location = useLocation()

  useEffect(() => {
    initialize()
  }, [initialize])

  useEffect(() => {
    pageview(location.pathname)
  }, [location])

  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
        <Toaster richColors position="top-right" />
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
````

## File: frontend/src/index.css
````css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 23%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 224.3 76.3% 48%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}

@layer utilities {
  .animate-gradient {
    background-size: 200% auto;
    animation: gradient 3s linear infinite;
  }
  
  @keyframes gradient {
    0% {
      background-position: 0% center;
    }
    100% {
      background-position: 200% center;
    }
  }
  
  .animate-fade-in {
    animation: fadeIn 0.8s ease-out;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .delay-1000 {
    animation-delay: 1s;
  }
}
````

## File: env.template
````
# Database Configuration (Cloud PostgreSQL with pgvector)
# API uses Session Mode (port 5432) - supports prepared statements
DATABASE_URL=postgresql+asyncpg://user:password@your-db-host:5432/dbname

# Worker Database URL (Optional) - Transaction Mode for high concurrency
# Use port 6543 for Supabase Transaction Mode (higher connection limits)
# If not set, workers will use DATABASE_URL
WORKER_DATABASE_URL=postgresql+asyncpg://user:password@your-db-host:6543/dbname

# Redis Configuration (Upstash Redis URL for both development and production)
# Example: rediss://:<password>@<host>:<port>
REDIS_URL=rediss://:<password>@your-upstash-endpoint:port

# Google Cloud Configuration
GOOGLE_API_KEY=your_google_api_key_here
GCS_BUCKET_NAME=your-gcs-bucket-name
# GCS HMAC Keys (from Cloud Console → Storage → Settings → Interoperability)
GCS_ACCESS_KEY=GOOG1E...  # Your HMAC Access Key
GCS_SECRET_KEY=your_hmac_secret  # Your HMAC Secret

# Supabase Configuration (for OAuth authentication)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
MAX_QUERIES_PER_DAY=50  # Daily query limit per bot (free tier)

# Demo Bot Configuration
DEMO_BOT_TENANT_ID=00000000-0000-0000-0000-000000000000
DEMO_BOT_ENABLED=true

# Demo Bot Admin User (Optional)
# Set these AFTER creating the admin user in Supabase Dashboard
# Leave empty to skip admin creation in migration
DEMO_BOT_ADMIN_UUID=
DEMO_BOT_ADMIN_EMAIL=admin@weaver.com

# Optional: Frontend API URL (defaults to http://localhost:8000)
API_URL=http://localhost:8000
````

## File: backend/app/api/v1/schemas.py
````python
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class SignupResponse(BaseModel):
    tenant_id: UUID
    user_id: UUID
    email: str
    role: str
    is_new_user: bool
    message: str


class UserMeResponse(BaseModel):
    user_id: UUID
    tenant_id: UUID
    email: str
    role: str


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)


class Source(BaseModel):
    doc_id: str
    page: Optional[int] = None
    confidence: float


class DailyUsage(BaseModel):
    current: int
    limit: int
    remaining: int
    redis_available: bool


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]
    confidence: str
    latency_ms: int
    daily_usage: Optional[DailyUsage] = None


class APIKeyCreate(BaseModel):
    name: Optional[str] = None
    rate_limit_rpm: Optional[int] = None


class APIKeyResponse(BaseModel):
    id: UUID
    key: str
    name: Optional[str]
    created_at: datetime
    rate_limit_rpm: int


class APIKeyMetadata(BaseModel):
    id: UUID
    name: Optional[str]
    created_at: datetime
    last_used_at: Optional[datetime]
    revoked: bool
    rate_limit_rpm: int


class APIKeyListResponse(BaseModel):
    keys: List[APIKeyMetadata]


class DocumentUploadResponse(BaseModel):
    doc_id: UUID
    filename: str
    status: str
    upload_url: Optional[str] = None


class DocumentMetadata(BaseModel):
    id: str
    filename: str
    size_bytes: int
    status: str
    error_message: Optional[str]
    created_at: str
    updated_at: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]
    total: int
    limit: int
    offset: int
    status_filter: Optional[str] = None


class BotConfigResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    config: dict
    created_at: datetime


class BusinessInfoRequest(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=255)
    industry: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10, max_length=1000)
    tone: str = Field(..., pattern="^(professional|friendly|technical|casual|formal)$")
    primary_goal: str = Field(..., min_length=5, max_length=500)
    special_instructions: Optional[str] = Field(None, max_length=500)


class GeneratedPromptResponse(BaseModel):
    system_prompt: str
    business_info: dict


class BotConfigUpdate(BaseModel):
    system_prompt: Optional[str] = Field(None, max_length=2000)
    business_info: Optional[dict] = None


class BotSettingsResponse(BaseModel):
    tenant_id: str
    name: str
    system_prompt: Optional[str] = None
    business_info: Optional[dict] = None
    using_default_prompt: bool
    created_at: str
    updated_at: str
````

## File: backend/app/db/connection.py
````python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_size=20, 
    max_overflow=40, 
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30,  # Timeout waiting for connection from pool
    echo_pool=False,  # Disable pool logging unless debugging
    connect_args={
        "statement_cache_size": 0,
        "server_settings": {
            "jit": "off",  # Disable JIT for faster simple queries
            "statement_timeout": "30000",  # 30s query timeout
        },
        "command_timeout": 30,  # Connection command timeout
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
````

## File: backend/app/services/query.py
````python
import time
import json
import logging
from typing import AsyncIterator
from uuid import UUID

from app.services.retrieval import RetrievalService
from app.services.llm import LLMService
from app.db.repositories import QueryLogRepository, BotRepository
from app.api.v1.schemas import QueryResponse, Source
from app.services.cache import cache_service

logger = logging.getLogger(__name__)


class QueryService:
    SLOW_RETRIEVAL_THRESHOLD_MS = 1000
    SLOW_LLM_THRESHOLD_MS = 3000
    SLOW_TOTAL_THRESHOLD_MS = 4000
    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.llm_service = LLMService()
        self.query_log_repo = QueryLogRepository()
        self.bot_repo = BotRepository()
        self.query_cache_ttl = 300  # 5 minutes cache for query results
    
    async def query(
        self,
        tenant_id: UUID,
        query: str,
        api_key_id: UUID,
    ) -> QueryResponse:
        start_time = time.time()
        timings = {}
        
        # Fetch bot config (includes system_prompt if customized)
        bot = await self.bot_repo.get_by_tenant(tenant_id)
        bot_config = bot.get("config", {}) if bot else {}
        
        # Check cache first
        cache_key = cache_service.generate_key("query", str(tenant_id), query.lower().strip())
        cached = cache_service.get(cache_key)
        if cached:
            logger.info(f"Cache HIT for tenant:{tenant_id}")
            # Still log the cached query
            await self.query_log_repo.log_query(
                tenant_id=tenant_id,
                api_key_id=api_key_id,
                query=query,
                answer=cached['answer'],
                confidence=cached['confidence'],
                latency_ms=cached['latency_ms'],
                sources=cached['sources'],
            )
            return QueryResponse(**cached)
        
        # Retrieval (embedding + vector search)
        t1 = time.time()
        context_chunks = await self.retrieval_service.retrieve_context(
            tenant_id=tenant_id,
            query=query,
        )
        timings['retrieval_ms'] = int((time.time() - t1) * 1000)
        if timings['retrieval_ms'] > self.SLOW_RETRIEVAL_THRESHOLD_MS:
            logger.warning(
                "Slow retrieval detected",
                extra={
                    "tenant_id": str(tenant_id),
                    "retrieval_ms": timings['retrieval_ms'],
                    "query_length": len(query),
                    "chunks_returned": len(context_chunks),
                },
            )
        
        if not context_chunks:
            answer = "I don't know based on the available information."
            confidence = "low"
            sources = []
            timings['llm_ms'] = 0
        else:
            # LLM generation with bot config (includes system_prompt)
            t2 = time.time()
            answer = await self.llm_service.generate_answer(query, context_chunks, bot_config)
            timings['llm_ms'] = int((time.time() - t2) * 1000)
            if timings['llm_ms'] > self.SLOW_LLM_THRESHOLD_MS:
                logger.warning(
                    "Slow LLM generation detected",
                    extra={
                        "tenant_id": str(tenant_id),
                        "llm_ms": timings['llm_ms'],
                        "context_chunks": len(context_chunks),
                    },
                )
            
            avg_similarity = sum(c["similarity"] for c in context_chunks) / len(context_chunks)
            if avg_similarity > 0.8:
                confidence = "high"
            elif avg_similarity > 0.6:
                confidence = "medium"
            else:
                confidence = "low"
            
            sources = [
                Source(
                    doc_id=chunk["doc_id"],
                    page=chunk.get("page_num"),
                    confidence=chunk["similarity"],
                )
                for chunk in context_chunks[:3]
            ]
        
        latency_ms = int((time.time() - start_time) * 1000)
        timings['total_ms'] = latency_ms
        
        logger.info(f"Query performance - tenant:{tenant_id} | timings:{timings} | chunks:{len(context_chunks)}")
        if latency_ms > self.SLOW_TOTAL_THRESHOLD_MS:
            logger.warning(
                "Slow query detected",
                extra={
                    "tenant_id": str(tenant_id),
                    "latency_ms": latency_ms,
                    "retrieval_ms": timings.get("retrieval_ms", 0),
                    "llm_ms": timings.get("llm_ms", 0),
                },
            )
        
        await self.query_log_repo.log_query(
            tenant_id=tenant_id,
            api_key_id=api_key_id,
            query=query,
            answer=answer,
            confidence=confidence,
            latency_ms=latency_ms,
            sources=[
                {
                    "doc_id": str(s.doc_id),
                    "page": s.page,
                    "confidence": s.confidence,
                }
                for s in sources
            ],
        )
        
        response = QueryResponse(
            answer=answer,
            sources=sources,
            confidence=confidence,
            latency_ms=latency_ms,
        )
        
        # Cache the result for future identical queries
        cache_data = {
            "answer": answer,
            "sources": [{"doc_id": str(s.doc_id), "page": s.page, "confidence": s.confidence} for s in sources],
            "confidence": confidence,
            "latency_ms": latency_ms,
        }
        if cache_service.set(cache_key, cache_data, self.query_cache_ttl):
            logger.info(f"Cached query result for tenant:{tenant_id}")
        
        return response
    
    async def query_stream(
        self,
        tenant_id: UUID,
        query: str,
        api_key_id: UUID,
    ) -> AsyncIterator[str]:
        start_time = time.time()
        
        # Fetch bot config (includes system_prompt if customized)
        bot = await self.bot_repo.get_by_tenant(tenant_id)
        bot_config = bot.get("config", {}) if bot else {}
        
        context_chunks = await self.retrieval_service.retrieve_context(
            tenant_id=tenant_id,
            query=query,
        )
        
        if not context_chunks:
            yield f"data: {json.dumps({'content': "I don't know based on the available information."})}\n\n"
            return
        
        full_answer = ""
        async for chunk in self.llm_service.generate_answer_stream(query, context_chunks, bot_config):
            full_answer += chunk
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        
        avg_similarity = sum(c["similarity"] for c in context_chunks) / len(context_chunks)
        if avg_similarity > 0.8:
            confidence = "high"
        elif avg_similarity > 0.6:
            confidence = "medium"
        else:
            confidence = "low"
        
        sources = [
            {
                "doc_id": str(chunk["doc_id"]),
                "page": chunk.get("page_num"),
                "confidence": chunk["similarity"],
            }
            for chunk in context_chunks[:3]
        ]
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        await self.query_log_repo.log_query(
            tenant_id=tenant_id,
            api_key_id=api_key_id,
            query=query,
            answer=full_answer,
            confidence=confidence,
            latency_ms=latency_ms,
            sources=sources,
        )
        
        yield f"data: {json.dumps({'sources': sources, 'confidence': confidence})}\n\n"
        yield "data: [DONE]\n\n"
````

## File: backend/app/workers/tasks.py
````python
import io
import asyncio
from uuid import UUID
from typing import List
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from celery import Celery
import fitz
from docx import Document
import html2text

from app.config import settings
from app.services.embeddings import EmbeddingService
from app.services.storage import StorageService
from app.db.repositories import DocumentRepository, ChunkRepository
from app.workers.db import WorkerAsyncSessionLocal


def _ensure_rediss_ssl_params(url: str) -> str:
    """
    Celery's Redis backend requires rediss:// URLs to specify ssl_cert_reqs.
    Upstash uses TLS with CA verification, so we set ssl_cert_reqs=required if missing.
    """
    if not url.startswith("rediss://"):
        return url

    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query))

    if "ssl_cert_reqs" not in query:
        # Use 'required' to validate server certs (recommended for Upstash)
        query["ssl_cert_reqs"] = "required"

    new_query = urlencode(query)
    return urlunparse(parsed._replace(query=new_query))


redis_url = _ensure_rediss_ssl_params(settings.REDIS_URL)

celery_app = Celery(
    "weaver",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    broker_pool_limit=None,
    broker_heartbeat=None,
    broker_connection_timeout=30,
    redis_socket_keepalive=True,
    redis_socket_keepalive_options={
        1: 30,  # TCP_KEEPIDLE
        2: 10,  # TCP_KEEPINTVL  
        3: 3,   # TCP_KEEPCNT
    },
)


def extract_text_from_pdf(content: bytes) -> List[dict]:
    chunks = []
    doc = fitz.open(stream=content, filetype="pdf")
    
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        if text.strip():
            chunks.append({
                "text": text,
                "page_num": page_num,
            })
    
    return chunks


def extract_text_from_docx(content: bytes) -> List[dict]:
    doc = Document(io.BytesIO(content))
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    
    return [{"text": text, "page_num": None}]


def extract_text_from_txt(content: bytes) -> List[dict]:
    text = content.decode("utf-8", errors="ignore")
    return [{"text": text, "page_num": None}]


def extract_text_from_html(content: bytes) -> List[dict]:
    html = content.decode("utf-8", errors="ignore")
    h = html2text.HTML2Text()
    h.ignore_links = False
    text = h.handle(html)
    
    return [{"text": text, "page_num": None}]


def chunk_text(text: str, chunk_size: int = 800, overlap_pct: int = 20) -> List[str]:
    words = text.split()
    overlap_size = int(chunk_size * overlap_pct / 100)
    
    chunks = []
    start = 0
    
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap_size
    
    return chunks


async def _process_document_async(doc_id: str, tenant_id: str, gcs_path: str):
    """Async function that does the actual document processing"""
    doc_repo = DocumentRepository(session_factory=WorkerAsyncSessionLocal)
    chunk_repo = ChunkRepository(session_factory=WorkerAsyncSessionLocal)
    embedding_service = EmbeddingService()
    
    # Download file from GCS
    content = StorageService.download_file(
        bucket_name=settings.GCS_BUCKET_NAME,
        key=gcs_path
    )
    
    filename = gcs_path.split("/")[-1]
    ext = filename.lower().split(".")[-1]
    
    if ext == "pdf":
        extracted = extract_text_from_pdf(content)
    elif ext in ["docx", "doc"]:
        extracted = extract_text_from_docx(content)
    elif ext == "txt":
        extracted = extract_text_from_txt(content)
    elif ext in ["html", "htm"]:
        extracted = extract_text_from_html(content)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    all_chunks = []
    chunk_index = 0
    
    for page_data in extracted:
        text_chunks = chunk_text(
            page_data["text"],
            chunk_size=settings.CHUNK_SIZE,
            overlap_pct=settings.CHUNK_OVERLAP_PCT,
        )
        
        for text_chunk in text_chunks:
            all_chunks.append({
                "text": text_chunk,
                "page_num": page_data.get("page_num"),
                "chunk_index": chunk_index,
            })
            chunk_index += 1
    
    texts = [c["text"] for c in all_chunks]
    embeddings = await embedding_service.embed_documents(texts)
    
    chunk_records = []
    for chunk, embedding in zip(all_chunks, embeddings):
        chunk_records.append({
            "doc_id": doc_id,
            "tenant_id": tenant_id,
            "embedding": embedding,
            "text": chunk["text"],
            "page_num": chunk["page_num"],
            "chunk_index": chunk["chunk_index"],
            "metadata": {},
        })
    
    await chunk_repo.insert_chunks(chunk_records)
    await doc_repo.update_status(UUID(doc_id), "completed")


async def _process_and_mark(doc_id: str, tenant_id: str, gcs_path: str) -> None:
    """Async wrapper that does the full document processing."""
    await _process_document_async(doc_id, tenant_id, gcs_path)


async def _mark_failed(doc_id: str, error_message: str) -> None:
    """Async helper to mark a document as failed."""
    doc_repo = DocumentRepository(session_factory=WorkerAsyncSessionLocal)
    await doc_repo.update_status(UUID(doc_id), "failed", error_message)


@celery_app.task(bind=True, max_retries=3)
def process_document(self, doc_id: str, tenant_id: str, gcs_path: str):
    """Celery entrypoint – runs async processing via asyncio.run."""
    try:
        asyncio.run(_process_and_mark(doc_id, tenant_id, gcs_path))
    except Exception as e:
        # Try to record failure in the DB; if that also fails, we still retry.
        try:
            asyncio.run(_mark_failed(doc_id, str(e)))
        finally:
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
````

## File: frontend/src/components/ui/button.tsx
````typescript
import * as React from 'react'
import { cn } from '@/lib/utils'

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'
  size?: 'default' | 'sm' | 'lg' | 'icon'
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'default', ...props }, ref) => {
    return (
      <button
        className={cn(
          'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
          {
            'bg-primary text-primary-foreground hover:bg-primary/90':
              variant === 'default',
            'bg-destructive text-destructive-foreground hover:bg-destructive/90':
              variant === 'destructive',
            'border border-input bg-background hover:bg-accent hover:text-accent-foreground':
              variant === 'outline',
            'bg-secondary text-secondary-foreground hover:bg-secondary/80':
              variant === 'secondary',
            'hover:bg-accent hover:text-accent-foreground': variant === 'ghost',
            'text-primary underline-offset-4 hover:underline': variant === 'link',
          },
          {
            'h-10 px-4 py-2': size === 'default',
            'h-9 rounded-md px-3': size === 'sm',
            'h-11 rounded-md px-8': size === 'lg',
            'h-10 w-10': size === 'icon',
          },
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'

export { Button }
````

## File: frontend/src/components/ui/card.tsx
````typescript
import * as React from 'react'
import { cn } from '@/lib/utils'

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'rounded-lg border bg-card text-card-foreground shadow-sm',
      className
    )}
    {...props}
  />
))
Card.displayName = 'Card'

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 p-6', className)}
    {...props}
  />
))
CardHeader.displayName = 'CardHeader'

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      'text-2xl font-semibold leading-none tracking-tight',
      className
    )}
    {...props}
  />
))
CardTitle.displayName = 'CardTitle'

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-muted-foreground', className)}
    {...props}
  />
))
CardDescription.displayName = 'CardDescription'

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
))
CardContent.displayName = 'CardContent'

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center p-6 pt-0', className)}
    {...props}
  />
))
CardFooter.displayName = 'CardFooter'

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
````

## File: frontend/src/components/ui/dialog.tsx
````typescript
import * as React from "react"
import * as DialogPrimitive from "@radix-ui/react-dialog"
import { X } from "lucide-react"

import { cn } from "@/lib/utils"

const Dialog = DialogPrimitive.Root

const DialogTrigger = DialogPrimitive.Trigger

const DialogPortal = DialogPrimitive.Portal

const DialogClose = DialogPrimitive.Close

const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      "fixed inset-0 z-50 bg-black/80  data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
      className
    )}
    {...props}
  />
))
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        "fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg",
        className
      )}
      {...props}
    >
      {children}
      <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-white transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-gray-950 focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-gray-100 data-[state=open]:text-gray-500">
        <X className="h-4 w-4" />
        <span className="sr-only">Close</span>
      </DialogPrimitive.Close>
    </DialogPrimitive.Content>
  </DialogPortal>
))
DialogContent.displayName = DialogPrimitive.Content.displayName

const DialogHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex flex-col space-y-1.5 text-center sm:text-left",
      className
    )}
    {...props}
  />
)
DialogHeader.displayName = "DialogHeader"

const DialogFooter = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2",
      className
    )}
    {...props}
  />
)
DialogFooter.displayName = "DialogFooter"

const DialogTitle = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn(
      "text-lg font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
DialogTitle.displayName = DialogPrimitive.Title.displayName

const DialogDescription = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn("text-sm text-gray-500", className)}
    {...props}
  />
))
DialogDescription.displayName = DialogPrimitive.Description.displayName

export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogClose,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
}
````

## File: frontend/src/components/ui/input.tsx
````typescript
import * as React from 'react'
import { cn } from '@/lib/utils'

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = 'Input'

export { Input }
````

## File: frontend/src/components/ui/select.tsx
````typescript
import * as React from "react"
import * as SelectPrimitive from "@radix-ui/react-select"
import { Check, ChevronDown, ChevronUp } from "lucide-react"

import { cn } from "@/lib/utils"

const Select = SelectPrimitive.Root

const SelectGroup = SelectPrimitive.Group

const SelectValue = SelectPrimitive.Value

const SelectTrigger = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Trigger>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Trigger
    ref={ref}
    className={cn(
      "flex h-10 w-full items-center justify-between rounded-md border border-gray-200 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-950 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1",
      className
    )}
    {...props}
  >
    {children}
    <SelectPrimitive.Icon asChild>
      <ChevronDown className="h-4 w-4 opacity-50" />
    </SelectPrimitive.Icon>
  </SelectPrimitive.Trigger>
))
SelectTrigger.displayName = SelectPrimitive.Trigger.displayName

const SelectScrollUpButton = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.ScrollUpButton>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.ScrollUpButton>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.ScrollUpButton
    ref={ref}
    className={cn(
      "flex cursor-default items-center justify-center py-1",
      className
    )}
    {...props}
  >
    <ChevronUp className="h-4 w-4" />
  </SelectPrimitive.ScrollUpButton>
))
SelectScrollUpButton.displayName = SelectPrimitive.ScrollUpButton.displayName

const SelectScrollDownButton = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.ScrollDownButton>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.ScrollDownButton>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.ScrollDownButton
    ref={ref}
    className={cn(
      "flex cursor-default items-center justify-center py-1",
      className
    )}
    {...props}
  >
    <ChevronDown className="h-4 w-4" />
  </SelectPrimitive.ScrollDownButton>
))
SelectScrollDownButton.displayName =
  SelectPrimitive.ScrollDownButton.displayName

const SelectContent = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Content>
>(({ className, children, position = "popper", ...props }, ref) => (
  <SelectPrimitive.Portal>
    <SelectPrimitive.Content
      ref={ref}
      className={cn(
        "relative z-50 max-h-96 min-w-[8rem] overflow-hidden rounded-md border bg-white text-gray-950 shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
        position === "popper" &&
          "data-[side=bottom]:translate-y-1 data-[side=left]:-translate-x-1 data-[side=right]:translate-x-1 data-[side=top]:-translate-y-1",
        className
      )}
      position={position}
      {...props}
    >
      <SelectScrollUpButton />
      <SelectPrimitive.Viewport
        className={cn(
          "p-1",
          position === "popper" &&
            "h-[var(--radix-select-trigger-height)] w-full min-w-[var(--radix-select-trigger-width)]"
        )}
      >
        {children}
      </SelectPrimitive.Viewport>
      <SelectScrollDownButton />
    </SelectPrimitive.Content>
  </SelectPrimitive.Portal>
))
SelectContent.displayName = SelectPrimitive.Content.displayName

const SelectLabel = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Label>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Label>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.Label
    ref={ref}
    className={cn("py-1.5 pl-8 pr-2 text-sm font-semibold", className)}
    {...props}
  />
))
SelectLabel.displayName = SelectPrimitive.Label.displayName

const SelectItem = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Item>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Item
    ref={ref}
    className={cn(
      "relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-gray-100 focus:text-gray-900 data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
      className
    )}
    {...props}
  >
    <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
      <SelectPrimitive.ItemIndicator>
        <Check className="h-4 w-4" />
      </SelectPrimitive.ItemIndicator>
    </span>

    <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
  </SelectPrimitive.Item>
))
SelectItem.displayName = SelectPrimitive.Item.displayName

const SelectSeparator = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Separator>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Separator>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.Separator
    ref={ref}
    className={cn("-mx-1 my-1 h-px bg-gray-100", className)}
    {...props}
  />
))
SelectSeparator.displayName = SelectPrimitive.Separator.displayName

export {
  Select,
  SelectGroup,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectLabel,
  SelectItem,
  SelectSeparator,
  SelectScrollUpButton,
  SelectScrollDownButton,
}
````

## File: frontend/src/components/ui/skeleton.tsx
````typescript
import { cn } from "@/lib/utils"

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-gray-200", className)}
      {...props}
    />
  )
}

export { Skeleton }
````

## File: frontend/src/components/ui/tabs.tsx
````typescript
import * as React from 'react'
import { cn } from '@/lib/utils'

interface TabsContextValue {
  value: string
  onValueChange: (value: string) => void
}

const TabsContext = React.createContext<TabsContextValue | undefined>(undefined)

const Tabs = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    value: string
    onValueChange: (value: string) => void
  }
>(({ className, value, onValueChange, ...props }, ref) => (
  <TabsContext.Provider value={{ value, onValueChange }}>
    <div ref={ref} className={cn('', className)} {...props} />
  </TabsContext.Provider>
))
Tabs.displayName = 'Tabs'

const TabsList = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground',
      className
    )}
    {...props}
  />
))
TabsList.displayName = 'TabsList'

const TabsTrigger = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & { value: string }
>(({ className, value, ...props }, ref) => {
  const context = React.useContext(TabsContext)
  if (!context) throw new Error('TabsTrigger must be used within Tabs')

  const isActive = context.value === value

  return (
    <button
      ref={ref}
      className={cn(
        'inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
        isActive
          ? 'bg-background text-foreground shadow-sm'
          : 'hover:bg-background/50',
        className
      )}
      onClick={() => context.onValueChange(value)}
      {...props}
    />
  )
})
TabsTrigger.displayName = 'TabsTrigger'

const TabsContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { value: string }
>(({ className, value, ...props }, ref) => {
  const context = React.useContext(TabsContext)
  if (!context) throw new Error('TabsContent must be used within Tabs')

  if (context.value !== value) return null

  return (
    <div
      ref={ref}
      className={cn(
        'mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        className
      )}
      {...props}
    />
  )
})
TabsContent.displayName = 'TabsContent'

export { Tabs, TabsList, TabsTrigger, TabsContent }
````

## File: frontend/src/hooks/useAPIKeys.ts
````typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/axios'
import { useAuthStore } from '../store/authStore'
import { APIKey, CreateAPIKeyResponse } from '../types'

export function useAPIKeys(tenantId: string | undefined) {
  const session = useAuthStore((state) => state.session)

  return useQuery({
    queryKey: ['apiKeys', tenantId],
    queryFn: async () => {
      if (!tenantId || !session) return []
      
      const response = await apiClient.get<{ keys: APIKey[] }>(
        `/v1/tenants/${tenantId}/api-keys`,
        {
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
      return response.data.keys
    },
    enabled: !!tenantId && !!session,
  })
}

export function useCreateAPIKey(tenantId: string | undefined) {
  const session = useAuthStore((state) => state.session)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (name: string) => {
      if (!tenantId || !session) {
        throw new Error('Tenant ID or session not available')
      }

      const response = await apiClient.post<CreateAPIKeyResponse>(
        `/v1/tenants/${tenantId}/api-keys`,
        { name },
        {
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys', tenantId] })
    },
  })
}

export function useRevokeAPIKey(tenantId: string | undefined) {
  const session = useAuthStore((state) => state.session)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (keyId: string) => {
      if (!tenantId || !session) {
        throw new Error('Tenant ID or session not available')
      }

      await apiClient.delete(
        `/v1/tenants/${tenantId}/api-keys/${keyId}`,
        {
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys', tenantId] })
    },
  })
}
````

## File: frontend/src/hooks/useDailyUsage.ts
````typescript
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/axios'
import { useAuthStore } from '../store/authStore'

interface DailyUsage {
  current: number
  limit: number
  remaining: number
  redis_available: boolean
}

export const useDailyUsage = (tenantId: string | undefined) => {
  const session = useAuthStore((state) => state.session)

  return useQuery<DailyUsage>({
    queryKey: ['daily-usage', tenantId],
    queryFn: async () => {
      if (!tenantId || !session) {
        return {
          current: 0,
          limit: 50,
          remaining: 50,
          redis_available: false
        }
      }
      
      const { data } = await apiClient.get(`/v1/tenants/${tenantId}/usage/daily`, {
        headers: { Authorization: `Bearer ${session.access_token}` },
      })
      return data
    },
    enabled: !!tenantId && !!session,
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 20000, // Consider data stale after 20 seconds
  })
}
````

## File: frontend/package.json
````json
{
  "name": "weaver-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
  },
  "dependencies": {
    "@hookform/resolvers": "^5.2.2",
    "@radix-ui/react-dialog": "^1.1.15",
    "@radix-ui/react-select": "^2.2.6",
    "@supabase/supabase-js": "^2.39.3",
    "@tanstack/react-query": "^5.17.19",
    "axios": "^1.6.5",
    "clsx": "^2.1.0",
    "date-fns": "^3.2.0",
    "lucide-react": "^0.312.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-dropzone": "^14.3.8",
    "react-hook-form": "^7.66.0",
    "react-router-dom": "^6.21.3",
    "recharts": "^3.4.1",
    "sonner": "^2.0.7",
    "tailwind-merge": "^2.2.1",
    "zod": "^4.1.12",
    "zustand": "^4.5.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "@typescript-eslint/eslint-plugin": "^6.19.0",
    "@typescript-eslint/parser": "^6.19.0",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.17",
    "eslint": "^8.56.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "postcss": "^8.4.33",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.11"
  }
}
````

## File: docker-compose.yml
````yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: infra/docker/Dockerfile
      target: api
    container_name: weaver-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - WORKER_DATABASE_URL=${WORKER_DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - RUN_MIGRATIONS=true
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - GCS_BUCKET_NAME=${GCS_BUCKET_NAME}
      - GCS_ACCESS_KEY=${GCS_ACCESS_KEY}
      - GCS_SECRET_KEY=${GCS_SECRET_KEY}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - ENVIRONMENT=${ENVIRONMENT:-development}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - MAX_QUERIES_PER_DAY=${MAX_QUERIES_PER_DAY:-50}
      - DEMO_BOT_TENANT_ID=${DEMO_BOT_TENANT_ID:-00000000-0000-0000-0000-000000000000}
      - DEMO_BOT_ENABLED=${DEMO_BOT_ENABLED:-true}
      - DEMO_BOT_ADMIN_UUID=${DEMO_BOT_ADMIN_UUID:-}
      - DEMO_BOT_ADMIN_EMAIL=${DEMO_BOT_ADMIN_EMAIL:-admin@weaver.com}
    volumes:
      - ./backend/app:/app/app
      - gcs_credentials:/app/credentials
    networks:
      - weaver-network
    restart: unless-stopped

  worker:
    build:
      context: .
      dockerfile: infra/docker/Dockerfile
      target: worker
    container_name: weaver-worker
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - WORKER_DATABASE_URL=${WORKER_DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - GCS_BUCKET_NAME=${GCS_BUCKET_NAME}
      - GCS_ACCESS_KEY=${GCS_ACCESS_KEY}
      - GCS_SECRET_KEY=${GCS_SECRET_KEY}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - ENVIRONMENT=${ENVIRONMENT:-development}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    depends_on:
      api:
        condition: service_started
    volumes:
      - ./backend/app:/app/app
      - ./worker:/app/worker
      - gcs_credentials:/app/credentials
    networks:
      - weaver-network
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        VITE_API_URL: ${API_URL:-http://localhost:8000}
        VITE_SUPABASE_URL: ${SUPABASE_URL}
        VITE_SUPABASE_ANON_KEY: ${SUPABASE_KEY}
        VITE_SITE_URL: ${SITE_URL:-http://localhost:3000}
    container_name: weaver-frontend
    ports:
      - "3000:3000"
    depends_on:
      - api
    networks:
      - weaver-network
    restart: unless-stopped

volumes:
  gcs_credentials:

networks:
  weaver-network:
    driver: bridge
````

## File: backend/app/db/repositories.py
````python
from typing import Optional, List, Callable
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update, delete, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import connection
AsyncSessionLocal = connection.AsyncSessionLocal
from app.db.models import Tenant, Profile, Bot, Document, DocumentChunk, APIKey, BotQuery
from app.auth.utils import generate_api_key, hash_api_key, verify_key_hash
from app.auth.types import APIKeyData
from app.api.v1.schemas import APIKeyMetadata


class TenantRepository:
    async def create(self, name: str) -> UUID:
        """Create a new tenant"""
        async with AsyncSessionLocal() as session:
            tenant = Tenant(name=name)
            session.add(tenant)
            await session.commit()
            await session.refresh(tenant)
            return tenant.id
    
    async def get_by_id(self, tenant_id: UUID) -> Optional[dict]:
        """Get tenant by ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Tenant).where(Tenant.id == tenant_id)
            )
            tenant = result.scalar_one_or_none()
            
            if not tenant:
                return None
            
            return {
                "id": tenant.id,
                "name": tenant.name,
                "plan_tier": tenant.plan_tier,
                "storage_used_bytes": tenant.storage_used_bytes,
                "created_at": tenant.created_at,
            }


class ProfileRepository:
    async def create(
        self,
        user_id: UUID,
        tenant_id: UUID,
        email: str,
        role: str = "owner"
    ) -> UUID:
        """Create a new user profile"""
        async with AsyncSessionLocal() as session:
            profile = Profile(
                id=user_id,
                tenant_id=tenant_id,
                email=email,
                role=role,
            )
            session.add(profile)
            await session.commit()
            await session.refresh(profile)
            return profile.id
    
    async def get_by_id(self, user_id: UUID) -> Optional[dict]:
        """Get user profile by ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Profile).where(Profile.id == user_id)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                return None
            
            return {
                "id": profile.id,
                "tenant_id": profile.tenant_id,
                "email": profile.email,
                "role": profile.role,
                "created_at": profile.created_at,
            }
    
    async def get_by_email(self, email: str) -> Optional[dict]:
        """Get user profile by email"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Profile).where(Profile.email == email)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                return None
            
            return {
                "id": profile.id,
                "tenant_id": profile.tenant_id,
                "email": profile.email,
                "role": profile.role,
                "created_at": profile.created_at,
            }


class APIKeyRepository:
    async def create_key(
        self,
        tenant_id: UUID,
        name: Optional[str] = None,
        rate_limit_rpm: Optional[int] = None,
    ) -> dict:
        key = generate_api_key()
        key_hash = hash_api_key(key)
        
        async with AsyncSessionLocal() as session:
            api_key = APIKey(
                tenant_id=tenant_id,
                name=name,
                key_hash=key_hash,
                rate_limit_rpm=rate_limit_rpm or 60,
            )
            session.add(api_key)
            await session.commit()
            await session.refresh(api_key)
            
            return {
                "id": api_key.id,
                "key": key,
                "name": api_key.name,
                "created_at": api_key.created_at,
                "rate_limit_rpm": api_key.rate_limit_rpm,
            }
    
    async def verify_key(self, api_key: str) -> Optional[APIKeyData]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(APIKey).where(APIKey.revoked == False)
            )
            keys = result.scalars().all()
            
            for key_obj in keys:
                if verify_key_hash(api_key, key_obj.key_hash):
                    return APIKeyData(
                        key_id=key_obj.id,
                        tenant_id=key_obj.tenant_id,
                        rate_limit_rpm=key_obj.rate_limit_rpm,
                    )
            
            return None
    
    async def update_last_used(self, key_id: UUID):
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(APIKey)
                .where(APIKey.id == key_id)
                .values(last_used_at=func.now())
            )
            await session.commit()
    
    async def list_keys(self, tenant_id: UUID) -> List[APIKeyMetadata]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(APIKey)
                .where(APIKey.tenant_id == tenant_id)
                .order_by(desc(APIKey.created_at))
            )
            keys = result.scalars().all()
            
            return [
                APIKeyMetadata(
                    id=key.id,
                    name=key.name,
                    created_at=key.created_at,
                    last_used_at=key.last_used_at,
                    revoked=key.revoked,
                    rate_limit_rpm=key.rate_limit_rpm,
                )
                for key in keys
            ]
    
    async def revoke_key(self, tenant_id: UUID, key_id: UUID):
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(APIKey)
                .where(APIKey.id == key_id, APIKey.tenant_id == tenant_id)
                .values(revoked=True)
            )
            await session.commit()


class DocumentRepository:
    def __init__(self, session_factory: Callable[[], AsyncSession] = AsyncSessionLocal):
        self._session_factory = session_factory

    async def create_document(
        self,
        tenant_id: UUID,
        filename: str,
        gcs_path: str,
        size_bytes: int,
    ) -> UUID:
        async with self._session_factory() as session:
            doc = Document(
                tenant_id=tenant_id,
                filename=filename,
                gcs_path=gcs_path,
                size_bytes=size_bytes,
                status='pending',
            )
            session.add(doc)
            await session.commit()
            await session.refresh(doc)
            return doc.id
    
    async def update_status(self, doc_id: UUID, status: str, error_message: Optional[str] = None):
        async with self._session_factory() as session:
            await session.execute(
                update(Document)
                .where(Document.id == doc_id)
                .values(status=status, error_message=error_message)
            )
            await session.commit()
    
    async def list_by_tenant(
        self,
        tenant_id: UUID,
        *,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> dict:
        """List documents for a tenant with pagination."""
        # Clamp pagination values
        limit = max(1, min(limit, 200))
        offset = max(0, offset)
        
        async with self._session_factory() as session:
            base_query = select(Document).where(Document.tenant_id == tenant_id)
            count_query = select(func.count()).select_from(Document).where(Document.tenant_id == tenant_id)
            
            if status:
                base_query = base_query.where(Document.status == status)
                count_query = count_query.where(Document.status == status)
            
            result = await session.execute(
                base_query
                .order_by(desc(Document.created_at))
                .limit(limit)
                .offset(offset)
            )
            documents = result.scalars().all()
            
            total_result = await session.execute(count_query)
            total = total_result.scalar_one()
            
            return {
                "documents": [
                    {
                        "id": str(doc.id),
                        "filename": doc.filename,
                        "size_bytes": doc.size_bytes,
                        "status": doc.status,
                        "error_message": doc.error_message,
                        "created_at": doc.created_at.isoformat(),
                        "updated_at": doc.updated_at.isoformat(),
                    }
                    for doc in documents
                ],
                "total": total,
                "limit": limit,
                "offset": offset,
                "status_filter": status,
            }


class ChunkRepository:
    def __init__(self, session_factory: Callable[[], AsyncSession] = AsyncSessionLocal):
        self._session_factory = session_factory

    async def insert_chunks(self, chunks: List[dict]):
        async with self._session_factory() as session:
            chunk_objects = [
                DocumentChunk(
                    doc_id=chunk["doc_id"],
                    tenant_id=chunk["tenant_id"],
                    embedding=chunk["embedding"],
                    text=chunk["text"],
                    page_num=chunk.get("page_num"),
                    chunk_index=chunk["chunk_index"],
                    chunk_metadata=chunk.get("metadata", {}),
                )
                for chunk in chunks
            ]
            session.add_all(chunk_objects)
            await session.commit()
    
    async def search_similar(
        self,
        tenant_id: UUID,
        query_embedding: List[float],
        top_k: int = 8,
    ) -> List[dict]:
        async with self._session_factory() as session:
            # Using raw SQL for vector similarity search as SQLAlchemy doesn't have full pgvector support yet
            from sqlalchemy import text
            
            # Format the embedding as a PostgreSQL array string
            embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'
            
            query = text("""
                SELECT 
                    id,
                    doc_id,
                    text,
                    page_num,
                    chunk_metadata,
                    1 - (embedding <=> (:query_embedding)::vector) as similarity
                FROM doc_chunks
                WHERE tenant_id = :tenant_id
                ORDER BY embedding <=> (:query_embedding)::vector
                LIMIT :top_k
            """)
            
            result = await session.execute(
                query,
                {
                    "tenant_id": str(tenant_id),
                    "query_embedding": embedding_str,
                    "top_k": top_k,
                }
            )
            rows = result.fetchall()
            
            return [
                {
                    "id": str(row[0]),
                    "doc_id": str(row[1]),  # Convert UUID to string
                    "text": row[2],
                    "page_num": row[3],
                    "metadata": row[4],
                    "similarity": float(row[5]),
                }
                for row in rows
            ]


class BotRepository:
    async def get_by_tenant_id(self, tenant_id: UUID) -> Optional[dict]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Bot).where(Bot.tenant_id == tenant_id)
            )
            bot = result.scalar_one_or_none()
            
            if not bot:
                return None
            
            return {
                "id": bot.id,
                "tenant_id": bot.tenant_id,
                "name": bot.name,
                "config": bot.config_json,
                "created_at": bot.created_at,
                "updated_at": bot.updated_at,
            }
    
    # Alias for compatibility
    async def get_by_tenant(self, tenant_id: UUID) -> Optional[dict]:
        return await self.get_by_tenant_id(tenant_id)
    
    async def update_config(self, tenant_id: UUID, config: dict) -> None:
        """Update bot configuration (system_prompt, business_info, etc.)"""
        from sqlalchemy import update
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                update(Bot)
                .where(Bot.tenant_id == tenant_id)
                .values(
                    config_json=config,
                    updated_at=func.now()
                )
            )
            await session.commit()
            
            if result.rowcount == 0:
                raise ValueError("Bot not found")


class QueryLogRepository:
    async def log_query(
        self,
        tenant_id: UUID,
        api_key_id: UUID,
        query: str,
        answer: str,
        confidence: str,
        latency_ms: int,
        sources: List[dict],
    ):
        async with AsyncSessionLocal() as session:
            # Ensure payload is JSON-serializable
            def convert(obj):
                if isinstance(obj, UUID):
                    return str(obj)
                if isinstance(obj, list):
                    return [convert(item) for item in obj]
                if isinstance(obj, dict):
                    return {key: convert(value) for key, value in obj.items()}
                return obj

            safe_sources = convert(sources)

            bot_query = BotQuery(
                tenant_id=tenant_id,
                api_key_id=api_key_id,
                query=query,
                answer=answer,
                confidence=confidence,
                latency_ms=latency_ms,
                sources=safe_sources,
            )
            session.add(bot_query)
            await session.commit()


class AnalyticsRepository:
    async def get_query_stats(self, tenant_id: UUID, start_date, end_date) -> dict:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text, cast, Date
            
            query = text("""
                SELECT 
                    COUNT(*) as total_queries,
                    AVG(latency_ms) as avg_latency,
                    COUNT(CASE WHEN confidence = 'low' THEN 1 END) as low_confidence_count,
                    DATE(created_at) as query_date
                FROM bot_queries
                WHERE tenant_id = :tenant_id
                  AND created_at BETWEEN :start_date AND :end_date
                GROUP BY DATE(created_at)
                ORDER BY query_date DESC
            """)
            
            result = await session.execute(
                query,
                {
                    "tenant_id": str(tenant_id),
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )
            rows = result.fetchall()
            
            return {
                "daily_stats": [
                    {
                        "date": str(row[3]),
                        "total_queries": row[0],
                        "avg_latency_ms": int(row[1]) if row[1] else 0,
                        "low_confidence_count": row[2],
                    }
                    for row in rows
                ]
            }
    
    async def get_top_queries(self, tenant_id: UUID, limit: int = 10) -> List[dict]:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            
            query = text("""
                SELECT query, COUNT(*) as count
                FROM bot_queries
                WHERE tenant_id = :tenant_id
                GROUP BY query
                ORDER BY count DESC
                LIMIT :limit
            """)
            
            result = await session.execute(
                query,
                {"tenant_id": str(tenant_id), "limit": limit}
            )
            rows = result.fetchall()
            
            return [
                {"query": row[0], "count": row[1]}
                for row in rows
            ]
    
    async def get_unanswered_queries(self, tenant_id: UUID, limit: int = 20) -> List[dict]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(BotQuery.query, BotQuery.created_at)
                .where(BotQuery.tenant_id == tenant_id, BotQuery.confidence == 'low')
                .order_by(desc(BotQuery.created_at))
                .limit(limit)
            )
            rows = result.all()
            
            return [
                {"query": row[0], "created_at": row[1].isoformat()}
                for row in rows
            ]
````

## File: frontend/src/components/dashboard/AnalyticsTab.tsx
````typescript
import { useState } from 'react'
import { useBotConfig } from '@/hooks/useBot'
import { useQueryStats, useTopQueries, useUnansweredQueries } from '@/hooks/useAnalytics'
import { useDailyUsage } from '@/hooks/useDailyUsage'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts'
import { BarChart3, TrendingUp, Clock, AlertCircle, Zap } from 'lucide-react'
import type { DailyStat, TopQuery, UnansweredQuery } from '@/types'

interface AnalyticsTabProps {
  tenantId: string
}

export default function AnalyticsTab({ tenantId }: AnalyticsTabProps) {
  const [timeRange, setTimeRange] = useState<'7' | '30' | '90'>('30')
  
  const { data: botConfig, isLoading: botLoading } = useBotConfig(tenantId)
  const { data: stats, isLoading: statsLoading } = useQueryStats(tenantId, timeRange)
  const { data: topQueries, isLoading: topLoading } = useTopQueries(tenantId)
  const { data: unanswered, isLoading: unansweredLoading } = useUnansweredQueries(tenantId)
  const { data: dailyUsage, isLoading: usageLoading } = useDailyUsage(tenantId)

  const isLoading = botLoading || statsLoading

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-64 mb-2" />
          <Skeleton className="h-4 w-48" />
        </div>
        <Skeleton className="h-24" /> {/* Daily usage card */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  const totalQueries =
    stats?.daily_stats?.reduce((sum: number, day: DailyStat) => sum + day.total_queries, 0) || 0

  const avgLatency = stats?.daily_stats?.length
    ? Math.round(
        stats.daily_stats.reduce(
          (sum: number, day: DailyStat) => sum + day.avg_latency_ms,
          0
        ) / stats.daily_stats.length
      )
    : 0

  const lowConfidenceCount =
    stats?.daily_stats?.reduce(
      (sum: number, day: DailyStat) => sum + day.low_confidence_count,
      0
    ) || 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold mb-2">Analytics</h2>
          {botConfig && (
            <p className="text-gray-600">
              Bot: <span className="font-medium">{botConfig.name}</span>
            </p>
          )}
        </div>
        <div className="w-48">
          <Select value={timeRange} onValueChange={(value: any) => setTimeRange(value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Daily Usage Alert */}
      {dailyUsage && !usageLoading && (
        <div className={`p-4 border rounded-lg ${
          dailyUsage.remaining === 0 
            ? 'bg-red-50 border-red-200' 
            : dailyUsage.remaining <= 10 
            ? 'bg-yellow-50 border-yellow-200' 
            : 'bg-blue-50 border-blue-200'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Zap className={`w-5 h-5 ${
                dailyUsage.remaining === 0 
                  ? 'text-red-600' 
                  : dailyUsage.remaining <= 10 
                  ? 'text-yellow-600' 
                  : 'text-blue-600'
              }`} />
              <div>
                <p className="font-medium text-gray-900">
                  Daily Usage: {dailyUsage.current} / {dailyUsage.limit} queries
                </p>
                <p className="text-sm text-gray-600">
                  {dailyUsage.remaining > 0 
                    ? `${dailyUsage.remaining} queries remaining today` 
                    : 'Daily limit reached. Resets at midnight UTC.'}
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">
                {Math.round((dailyUsage.current / dailyUsage.limit) * 100)}%
              </div>
              <div className="text-xs text-gray-500">used</div>
            </div>
          </div>
          {/* Progress bar */}
          <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all ${
                dailyUsage.remaining === 0 
                  ? 'bg-red-600' 
                  : dailyUsage.remaining <= 10 
                  ? 'bg-yellow-600' 
                  : 'bg-blue-600'
              }`}
              style={{ width: `${Math.min((dailyUsage.current / dailyUsage.limit) * 100, 100)}%` }}
            />
          </div>
        </div>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-6 bg-white border rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Total Queries</h3>
            <BarChart3 className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{totalQueries.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-1">Last {timeRange} days</p>
        </div>

        <div className="p-6 bg-white border rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Avg Latency</h3>
            <Clock className="w-5 h-5 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{avgLatency}ms</p>
          <p className="text-xs text-gray-500 mt-1">Response time</p>
        </div>

        <div className="p-6 bg-white border rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Low Confidence</h3>
            <AlertCircle className="w-5 h-5 text-yellow-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{lowConfidenceCount}</p>
          <p className="text-xs text-gray-500 mt-1">
            {totalQueries > 0 ? `${Math.round((lowConfidenceCount / totalQueries) * 100)}%` : '0%'} of
            total
          </p>
        </div>
      </div>

      {/* Query Volume Chart */}
      {stats?.daily_stats && stats.daily_stats.length > 0 && (
        <div className="p-6 bg-white border rounded-lg">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Query Volume
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={[...stats.daily_stats].reverse()}>
              <defs>
                <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '6px' }}
                labelFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <Area
                type="monotone"
                dataKey="total_queries"
                stroke="#6366F1"
                strokeWidth={2}
                fill="url(#colorQueries)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Top Queries */}
      <div className="p-6 bg-white border rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Top Queries</h3>
        {topLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-12" />
            ))}
          </div>
        ) : topQueries && topQueries.length > 0 ? (
          <div className="space-y-2">
            {topQueries.map((item: TopQuery, index: number) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <p className="text-sm text-gray-700 flex-1">{item.query}</p>
                <span className="ml-4 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                  {item.count} {item.count === 1 ? 'time' : 'times'}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No queries yet</p>
        )}
      </div>

      {/* Unanswered/Low Confidence Queries */}
      <div className="p-6 bg-white border rounded-lg">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-yellow-600" />
          Low Confidence Queries
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          These queries received low-confidence answers. Consider adding more relevant documents.
        </p>
        {unansweredLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-12" />
            ))}
          </div>
        ) : unanswered && unanswered.length > 0 ? (
          <div className="space-y-2">
            {unanswered.map((item: UnansweredQuery, index: number) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border border-yellow-200"
              >
                <p className="text-sm text-gray-700 flex-1">{item.query}</p>
                <span className="ml-4 text-xs text-gray-500">
                  {new Date(item.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">
            No low-confidence queries
          </p>
        )}
      </div>
    </div>
  )
}
````

## File: frontend/src/hooks/useAnalytics.ts
````typescript
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/axios'
import { useAuthStore } from '../store/authStore'
import type { QueryStatsResponse, TopQuery, UnansweredQuery } from '../types'

export function useQueryStats(tenantId: string | undefined, days: string = '30') {
  const session = useAuthStore((state) => state.session)
  
  // Calculate start_date based on days
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - parseInt(days))
  const endDate = new Date()
  
  return useQuery({
    queryKey: ['analytics', 'stats', tenantId, days],
    queryFn: async () => {
      if (!tenantId || !session) return { daily_stats: [] } as QueryStatsResponse
      const res = await apiClient.get<QueryStatsResponse>(`/v1/tenants/${tenantId}/analytics/queries`, {
        params: {
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString(),
        },
        headers: { Authorization: `Bearer ${session.access_token}` },
      })
      return res.data
    },
    enabled: !!tenantId && !!session,
    refetchInterval: 15000,
  })
}

export function useTopQueries(tenantId: string | undefined, limit = 10) {
  const session = useAuthStore((state) => state.session)
  return useQuery({
    queryKey: ['analytics', 'top', tenantId, limit],
    queryFn: async () => {
      if (!tenantId || !session) return [] as TopQuery[]
      const res = await apiClient.get<{ queries: TopQuery[] }>(
        `/v1/tenants/${tenantId}/analytics/top-queries`,
        {
          params: { limit },
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
      return res.data.queries
    },
    enabled: !!tenantId && !!session,
    refetchInterval: 15000,
  })
}

export function useUnansweredQueries(tenantId: string | undefined, limit = 20) {
  const session = useAuthStore((state) => state.session)
  return useQuery({
    queryKey: ['analytics', 'unanswered', tenantId, limit],
    queryFn: async () => {
      if (!tenantId || !session) return [] as UnansweredQuery[]
      const res = await apiClient.get<{ queries: UnansweredQuery[] }>(
        `/v1/tenants/${tenantId}/analytics/unanswered`,
        {
          params: { limit },
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
      return res.data.queries
    },
    enabled: !!tenantId && !!session,
    refetchInterval: 15000,
  })
}
````

## File: frontend/src/hooks/useBot.ts
````typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/axios'
import { useAuthStore } from '../store/authStore'
import type { BotConfig } from '../types'

export function useBotConfig(tenantId: string | undefined) {
  const session = useAuthStore((state) => state.session)

  return useQuery({
    queryKey: ['botConfig', tenantId],
    queryFn: async () => {
      if (!tenantId || !session) return null
      const res = await apiClient.get<BotConfig>(`/v1/tenants/${tenantId}/bot`, {
        headers: { Authorization: `Bearer ${session.access_token}` },
      })
      return res.data
    },
    enabled: !!tenantId && !!session,
  })
}

export function useGenerateSystemPrompt(tenantId: string) {
  const session = useAuthStore((state) => state.session)

  return useMutation({
    mutationFn: async (businessInfo: {
      businessName: string
      industry: string
      description: string
      tone: string
      primaryGoal: string
      specialInstructions?: string
    }) => {
      if (!session) throw new Error('Not authenticated')
      
      const response = await apiClient.post(
        `/v1/tenants/${tenantId}/bot/generate-prompt`,
        {
          business_name: businessInfo.businessName,
          industry: businessInfo.industry,
          description: businessInfo.description,
          tone: businessInfo.tone,
          primary_goal: businessInfo.primaryGoal,
          special_instructions: businessInfo.specialInstructions,
        },
        {
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
      return response.data
    },
  })
}

export function useUpdateBotConfig(tenantId: string) {
  const session = useAuthStore((state) => state.session)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: { system_prompt: string | null; business_info?: any }) => {
      if (!session) throw new Error('Not authenticated')
      
      const response = await apiClient.put(
        `/v1/tenants/${tenantId}/bot`,
        data,
        {
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
      return response.data
    },
    onSuccess: () => {
      // Invalidate bot config cache
      queryClient.invalidateQueries({ queryKey: ['botConfig', tenantId] })
    },
  })
}
````

## File: frontend/src/hooks/useDocuments.ts
````typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/axios'
import { useAuthStore } from '../store/authStore'
import type { DocumentListResponse } from '../types'

type DocumentQueryOptions = {
  limit?: number
  offset?: number
  status?: string | null
  enabled?: boolean
}

const buildEmptyResponse = (options: DocumentQueryOptions): DocumentListResponse => ({
  documents: [],
  total: 0,
  limit: options.limit ?? 50,
  offset: options.offset ?? 0,
  status_filter: options.status ?? null,
})

export function useDocuments(tenantId: string | undefined, options: DocumentQueryOptions = {}) {
  const session = useAuthStore((state) => state.session)
  const limit = options.limit ?? 50
  const offset = options.offset ?? 0
  const status = options.status ?? null

  return useQuery<DocumentListResponse>({
    queryKey: ['documents', tenantId, limit, offset, status],
    queryFn: async () => {
      if (!tenantId || !session) return buildEmptyResponse(options)
      
      const response = await apiClient.get<DocumentListResponse>(
        `/v1/tenants/${tenantId}/docs`,
        {
          params: {
            limit,
            offset,
            status: status || undefined,
          },
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
      return response.data
    },
    enabled: !!tenantId && !!session && (options.enabled ?? true),
    refetchInterval: 5000, // Poll for status updates
    keepPreviousData: true,
  })
}

export function useUploadDocument(tenantId: string | undefined) {
  const session = useAuthStore((state) => state.session)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (file: File) => {
      if (!tenantId || !session) {
        throw new Error('Tenant ID or session not available')
      }

      const formData = new FormData()
      formData.append('file', file)

      const response = await apiClient.post(
        `/v1/tenants/${tenantId}/docs:upload`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      )
      return response.data
    },
    onSuccess: () => {
      // Invalidate and refetch documents list
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })
}
````

## File: frontend/src/pages/AuthCallback.tsx
````typescript
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '@/lib/supabase'
import { apiClient } from '@/lib/axios'

export default function AuthCallback() {
  const navigate = useNavigate()

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Check if we have a hash (implicit flow) or code (PKCE flow)
        const hashParams = new URLSearchParams(window.location.hash.substring(1))
        const queryParams = new URLSearchParams(window.location.search)
        
        const accessToken = hashParams.get('access_token')
        const code = queryParams.get('code')

        if (accessToken) {
          // Implicit flow - tokens are in the hash
          // Supabase client will automatically handle this via onAuthStateChange
          console.log('Handling implicit flow callback')
          
          // Wait briefly for Supabase to process the session (reduced from 500ms to 200ms)
          await new Promise(resolve => setTimeout(resolve, 200))
          
          // Get the current session
          const { data: { session }, error } = await supabase.auth.getSession()
          
          if (error) {
            console.error('Error getting session:', error)
            navigate('/', { replace: true })
            return
          }

          // Complete signup on backend (creates tenant/user/bot if needed)
          // Don't wait for this - let it happen in background
          if (session) {
            apiClient.post(
              '/v1/auth/complete-signup',
              {},
              {
                headers: {
                  Authorization: `Bearer ${session.access_token}`,
                },
              }
            ).catch((error: unknown) => {
              console.error('Error completing signup:', error)
              // Dashboard will handle this fallback
            })
          }
        } else if (code) {
          // PKCE flow - exchange code for session
          console.log('Handling PKCE flow callback')
          const { data, error } = await supabase.auth.exchangeCodeForSession(code)

          if (error) {
            console.error('Error exchanging code for session:', error)
            navigate('/')
            return
          }

          // Complete signup on backend (creates tenant/user/bot if needed)
          if (data.session) {
            try {
              await apiClient.post(
                '/v1/auth/complete-signup',
                {},
                {
                  headers: {
                    Authorization: `Bearer ${data.session.access_token}`,
                  },
                }
              )
            } catch (error) {
              console.error('Error completing signup:', error)
              // Continue anyway - the dashboard will handle this
            }
          }
        }

        // Redirect to dashboard immediately (replace history to avoid back button issues)
        navigate('/dashboard', { replace: true })
      } catch (error: unknown) {
        console.error('Error in auth callback:', error)
        navigate('/', { replace: true })
      }
    }

    handleCallback()
  }, [navigate])

  // Minimal UI - just show nothing or a subtle indicator
  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      {/* Invisible loading - processing happens in background */}
      <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
    </div>
  )
}
````

## File: frontend/src/store/authStore.ts
````typescript
import { create } from 'zustand'
import { User as SupabaseUser, Session, AuthChangeEvent } from '@supabase/supabase-js'
import { supabase } from '@/lib/supabase'
import { apiClient } from '@/lib/axios'
import { User } from '../types'

interface AuthState {
  session: Session | null
  supabaseUser: SupabaseUser | null
  user: User | null
  loading: boolean
  initialized: boolean
  setSession: (session: Session | null) => void
  setUser: (user: User | null) => void
  fetchUserProfile: () => Promise<void>
  signOut: () => Promise<void>
  initialize: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  session: null,
  supabaseUser: null,
  user: null,
  loading: true,
  initialized: false,

  setSession: (session) => {
    set({ session, supabaseUser: session?.user || null })
  },

  setUser: (user) => {
    set({ user })
  },

  fetchUserProfile: async () => {
    const { session } = get()
    if (!session) {
      set({ user: null, loading: false })
      return
    }

    try {
      const response = await apiClient.get<User>('/v1/users/me', {
        headers: { Authorization: `Bearer ${session.access_token}` },
      })
      set({ user: response.data, loading: false })
    } catch (error: any) {
      console.error('Error fetching user profile:', error)
      
      // If user not found (404), try to complete signup
      if (error.response?.status === 404) {
        try {
          const signupResponse = await apiClient.post(
            '/v1/auth/complete-signup',
            {},
            { headers: { Authorization: `Bearer ${session.access_token}` } }
          )
          set({ user: signupResponse.data, loading: false })
        } catch (signupError) {
          console.error('Error completing signup:', signupError)
          set({ loading: false })
        }
      } else {
        set({ loading: false })
      }
    }
  },

  signOut: async () => {
    await supabase.auth.signOut()
    set({ session: null, supabaseUser: null, user: null })
  },

  initialize: async () => {
    if (get().initialized) return

    // Get initial session
    const { data: { session } } = await supabase.auth.getSession()
    set({ session, supabaseUser: session?.user || null })

    // Fetch user profile if session exists
    if (session) {
      await get().fetchUserProfile()
    } else {
      set({ loading: false })
    }

    // Listen for auth changes
    supabase.auth.onAuthStateChange(async (_event: AuthChangeEvent, session: Session | null) => {
      set({ session, supabaseUser: session?.user || null })
      
      if (session) {
        await get().fetchUserProfile()
      } else {
        set({ user: null, loading: false })
      }
    })

    set({ initialized: true })
  },
}))
````

## File: frontend/tsconfig.json
````json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path alias */
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    },

    /* React / module interop */
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
````

## File: worker/entrypoint.sh
````bash
#!/bin/bash
set -e

echo "🔄 Starting Weaver Worker..."

# Worker tuning knobs (with sensible defaults)
CONCURRENCY=${WORKER_CONCURRENCY:-4}
MAX_TASKS_PER_CHILD=${WORKER_MAX_TASKS_PER_CHILD:-10}
SOFT_TIME_LIMIT=${WORKER_SOFT_TIME_LIMIT:-240}
TIME_LIMIT=${WORKER_TIME_LIMIT:-300}
WORKER_POOL=${WORKER_POOL:-prefork}

# Avoid libpq/asyncpg probing ~/.postgresql client cert/key paths
unset PGSSLKEY
unset PGSSLCERT
unset PGSSLROOTCERT
unset PGSYSCONFDIR
# Ensure it doesn't default to /root as HOME
export HOME=/tmp

# Start health check server in background (for Cloud Run)
echo "🏥 Starting health check server on port ${PORT:-8080}..."
python3 /app/health_server.py &
HEALTH_PID=$!

# Trap signals to ensure graceful shutdown
trap "echo '🛑 Shutting down...'; kill $HEALTH_PID 2>/dev/null; exit 0" SIGTERM SIGINT

echo "🔨 Starting Celery worker..."
exec celery -A app.workers.tasks worker \
  --loglevel=info \
  --pool="${WORKER_POOL}" \
  --concurrency="${CONCURRENCY}" \
  --uid=nobody --gid=nogroup \
  --max-tasks-per-child="${MAX_TASKS_PER_CHILD}" \
  --soft-time-limit="${SOFT_TIME_LIMIT}" \
  --time-limit="${TIME_LIMIT}" \
  --without-gossip --without-mingle --without-heartbeat
````

## File: frontend/src/components/dashboard/UploadTab.tsx
````typescript
import { useState, useCallback, useEffect, useMemo } from 'react'
import { useDocuments, useUploadDocument } from '@/hooks/useDocuments'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { formatFileSize, formatDate } from '@/lib/utils'
import { Loader2, CheckCircle, XCircle, Clock, Upload, FileText, ChevronLeft, ChevronRight } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import { toast } from 'sonner'
import type { Document as DocumentType } from '@/types'
import { useDebounce } from '@/hooks/useDebounce'

type StatusFilter = 'all' | 'pending' | 'processing' | 'completed' | 'failed'

interface UploadTabProps {
  tenantId: string
}

export default function UploadTab({ tenantId }: UploadTabProps) {
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({})
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [page, setPage] = useState(0)
  const limit = 20

  const debouncedSearch = useDebounce(searchTerm, 300)

  const { data: documentsResponse, isLoading, isFetching } = useDocuments(tenantId, {
    limit,
    offset: page * limit,
    status: statusFilter === 'all' ? null : statusFilter,
  })
  const uploadMutation = useUploadDocument(tenantId)

  const totalDocuments = documentsResponse?.total ?? 0
  const documents = documentsResponse?.documents ?? []
  const totalPages = Math.max(1, Math.ceil(totalDocuments / limit))

  useEffect(() => {
    setPage(0)
  }, [statusFilter, debouncedSearch])

  const filteredDocuments = useMemo(() => {
    if (!debouncedSearch) return documents
    const lower = debouncedSearch.toLowerCase()
    return documents.filter((doc) => doc.filename.toLowerCase().includes(lower))
  }, [documents, debouncedSearch])

  const onDrop = useCallback(async (acceptedFiles: File[], fileRejections) => {
    if (fileRejections.length > 0) {
      toast.error('You can only upload a maximum of 2 files at once.')
      return
    }

    for (const file of acceptedFiles) {
      const fileId = `${file.name}-${Date.now()}`
      setUploadProgress(prev => ({ ...prev, [fileId]: 0 }))
      
      try {
        // Simulate progress (in a real app, you'd track actual upload progress)
        const progressInterval = setInterval(() => {
          setUploadProgress(prev => {
            const current = prev[fileId] || 0
            if (current >= 90) {
              clearInterval(progressInterval)
              return prev
            }
            return { ...prev, [fileId]: current + 10 }
          })
        }, 200)

        await uploadMutation.mutateAsync(file)
        
        clearInterval(progressInterval)
        setUploadProgress(prev => ({ ...prev, [fileId]: 100 }))
        toast.success(`${file.name} uploaded successfully!`)
        
        // Remove from progress after a delay
        setTimeout(() => {
          setUploadProgress(prev => {
            const newProgress = { ...prev }
            delete newProgress[fileId]
            return newProgress
          })
        }, 2000)
      } catch (error: any) {
        toast.error(`Failed to upload ${file.name}: ${error?.message || 'Unknown error'}`)
        setUploadProgress(prev => {
          const newProgress = { ...prev }
          delete newProgress[fileId]
          return newProgress
        })
      }
    }
  }, [uploadMutation])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
      'text/html': ['.html', '.htm'],
    },
    maxSize: 200 * 1024 * 1024, // 200MB
    multiple: true,
    maxFiles: 2, // Add this line
  })

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      processing: 'bg-blue-100 text-blue-800 border-blue-200',
      completed: 'bg-green-100 text-green-800 border-green-200',
      failed: 'bg-red-100 text-red-800 border-red-200',
    }
    return badges[status as keyof typeof badges] || 'bg-gray-100 text-gray-800 border-gray-200'
  }

  const getStatusIcon = (status: string) => {
    if (status === 'pending' || status === 'processing') {
      return <Loader2 className="w-4 h-4 animate-spin" />
    }
    if (status === 'completed') {
      return <CheckCircle className="w-4 h-4" />
    }
    if (status === 'failed') {
      return <XCircle className="w-4 h-4" />
    }
    return <Clock className="w-4 h-4" />
  }

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div>
          <Skeleton className="h-8 w-64 mb-2" />
          <Skeleton className="h-4 w-96 mb-6" />
          <Skeleton className="h-48 w-full" />
        </div>
        <div>
          <Skeleton className="h-6 w-48 mb-4" />
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-semibold mb-2">Upload Documents</h2>
        <p className="text-gray-600 mb-6">
          Upload PDF, DOCX, TXT, or HTML files to train your bot (max 200MB per file)
        </p>

        {/* Drag & Drop Upload Area */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          {isDragActive ? (
            <p className="text-lg font-medium text-blue-600">Drop files here...</p>
          ) : (
            <>
              <p className="text-lg font-medium text-gray-700 mb-2">
                Drag & drop files here, or click to browse
              </p>
              <p className="text-sm text-gray-500">
                Supports PDF, DOCX, TXT, HTML • Max 200MB per file
              </p>
            </>
          )}
        </div>

        {/* Upload Progress */}
        {Object.keys(uploadProgress).length > 0 && (
          <div className="mt-4 space-y-2">
            {Object.entries(uploadProgress).map(([fileId, progress]) => {
              const fileName = fileId.split('-').slice(0, -1).join('-')
              return (
                <div key={fileId} className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-blue-900">{fileName}</span>
                    <span className="text-sm text-blue-700">{progress}%</span>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Documents List */}
      <div>
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h3 className="text-xl font-semibold mb-2">Your Documents</h3>
            <p className="text-sm text-gray-500">Track processing status and manage uploads</p>
          </div>
          {totalDocuments > 0 && (
            <div className="text-sm text-gray-600">
              Showing {(page * limit) + 1}-
              {Math.min((page + 1) * limit, totalDocuments)} of {totalDocuments} documents
            </div>
          )}
        </div>

        {totalDocuments === 0 ? (
          <div className="text-center py-16 border-2 border-dashed rounded-lg">
            <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-gray-600 mb-4 text-lg">No documents uploaded yet</p>
            <p className="text-gray-500 text-sm mb-6">
              Upload your first document to start training your bot
            </p>
            <Button onClick={() => (document.querySelector('input[type="file"]') as HTMLInputElement)?.click()}>
              <Upload className="w-4 h-4 mr-2" />
              Upload Document
            </Button>
          </div>
        ) : (
          <>
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <div>
                <label className="text-sm font-medium text-gray-700">Search</label>
                <Input
                  placeholder="Search by filename..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Status</label>
                <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as StatusFilter)}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="All statuses" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All statuses</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="processing">Processing</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="failed">Failed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {isFetching && (
              <div className="flex items-center gap-2 text-sm text-gray-500 mt-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                Refreshing status...
              </div>
            )}

            {filteredDocuments.length === 0 ? (
              <div className="text-center py-12 border rounded-lg mt-4">
                <p className="text-gray-600">No documents match the current filters.</p>
              </div>
            ) : (
              <div className="space-y-3 mt-4">
                {filteredDocuments.map((doc: DocumentType) => (
              <div
                key={doc.id}
                className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium text-gray-900">{doc.filename}</h4>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium border inline-flex items-center gap-1 ${getStatusBadge(
                          doc.status
                        )}`}
                      >
                        {getStatusIcon(doc.status)}
                        {doc.status}
                      </span>
                    </div>
                    <div className="flex gap-4 text-sm text-gray-600">
                      <span>{formatFileSize(doc.size_bytes)}</span>
                      <span>Uploaded: {formatDate(doc.created_at)}</span>
                    </div>
                    {doc.error_message && (
                      <p className="mt-2 text-sm text-red-600">
                        Error: {doc.error_message}
                      </p>
                    )}
                    {doc.status === 'completed' && (
                      <p className="mt-2 text-sm text-green-600 flex items-center gap-1">
                        <CheckCircle className="w-4 h-4" />
                        Ready for querying! Your bot can now answer questions about this
                        document.
                      </p>
                    )}
                    {doc.status === 'processing' && (
                      <p className="mt-2 text-sm text-blue-600 flex items-center gap-1">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Processing document... This may take a few minutes.
                      </p>
                    )}
                  </div>
                </div>
              </div>
                ))}
              </div>
            )}

            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-6">
                <Button
                  variant="outline"
                  onClick={() => setPage((prev) => Math.max(prev - 1, 0))}
                  disabled={page === 0}
                >
                  <ChevronLeft className="w-4 h-4 mr-2" />
                  Previous
                </Button>
                <span className="text-sm text-gray-600">
                  Page {page + 1} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  onClick={() => setPage((prev) => Math.min(prev + 1, totalPages - 1))}
                  disabled={page >= totalPages - 1}
                >
                  Next
                  <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
````

## File: frontend/src/pages/Login.tsx
````typescript
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { supabase } from '@/lib/supabase'
import { Button } from '../components/ui/button'

export default function Login() {
  const navigate = useNavigate()
  const { session, loading } = useAuthStore()
  const [isAuthenticating, setIsAuthenticating] = useState(false)

  const handleGoogleLogin = async () => {
    setIsAuthenticating(true)
    const redirectUrl = `${window.location.origin}/auth/callback`
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: redirectUrl,
      },
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
          <div className="text-slate-400">Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-x-hidden">
      {/* Animated background grid */}
      <div className="fixed inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)] pointer-events-none"></div>
      
      {/* Gradient orbs */}
      <div className="fixed top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-[120px] animate-pulse"></div>
      <div className="fixed bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-[120px] animate-pulse delay-1000"></div>

      <div className="relative z-10">
        {/* Navigation */}
        <nav className="max-w-7xl mx-auto px-6 py-8 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-900 rounded-lg flex items-center justify-center font-bold">
              W
            </div>
            <span className="text-xl font-semibold">Weaver</span>
          </div>
          <Button 
            onClick={session ? () => navigate('/dashboard') : handleGoogleLogin}
            disabled={isAuthenticating}
            variant="outline" 
            className="bg-blue-900 hover:bg-blue-500 text-white hover:text-white"
          >
            {isAuthenticating ? 'Redirecting...' : session ? 'Go to Dashboard' : 'Sign In'}
          </Button>
        </nav>

        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-6 pt-20 pb-32">
          <div className="text-center max-w-4xl mx-auto">
            {/* Floating badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-800/50 border border-slate-700 mb-8 animate-fade-in">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-slate-300">Powered by Gemini + LangChain</span>
            </div>

            <h1 className="text-6xl md:text-7xl font-bold mb-6 leading-tight">
              Turn Your Business Knowledge Into an{' '}
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent animate-gradient">
                AI Support Bot
              </span>
            </h1>
            
            <p className="text-xl text-slate-400 mb-4 max-w-3xl mx-auto leading-relaxed">
              Upload your docs. Get a custom AI that answers your customers — instantly.
            </p>
            
            <p className="text-lg text-slate-500 mb-12 max-w-2xl mx-auto">
              Weaver takes your PDFs, manuals, and help guides and turns them into an intelligent customer-service bot. 
              <span className="text-slate-400"> No training, coding, or prompt engineering required.</span>
            </p>

            {/* CTA */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button 
                onClick={session ? () => navigate('/dashboard') : handleGoogleLogin}
                disabled={isAuthenticating}
                size="lg"
                className="bg-blue-900 hover:bg-slate-900 text-white shadow-lg shadow-blue-500/30 text-lg px-8 h-14 group"
              >
                {isAuthenticating ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin mr-3"></div>
                    Redirecting to Google...
                  </>
                ) : session ? (
                  <>
                    Go to Dashboard
                    <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="currentColor"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                    </svg>
                    Get Started with Google
                    <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </>
                )}
              </Button>
              <div className="text-sm text-slate-500">
                {session ? 'Welcome back!' : 'Free to start • No credit card required'}
              </div>
            </div>

            {/* Social proof */}
            <div className="mt-16 flex items-center justify-center gap-8 text-slate-600 text-sm">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Secure & Private</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M13 7H7v6h6V7z" />
                  <path fillRule="evenodd" d="M7 2a1 1 0 012 0v1h2V2a1 1 0 112 0v1h2a2 2 0 012 2v2h1a1 1 0 110 2h-1v2h1a1 1 0 110 2h-1v2a2 2 0 01-2 2h-2v1a1 1 0 11-2 0v-1H9v1a1 1 0 11-2 0v-1H5a2 2 0 01-2-2v-2H2a1 1 0 110-2h1V9H2a1 1 0 010-2h1V5a2 2 0 012-2h2V2zM5 5h10v10H5V5z" clipRule="evenodd" />
                </svg>
                <span>Sub-2s Response</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Built on GCP</span>
              </div>
            </div>
          </div>
        </section>

        {/* Built for Businesses Section */}
        <section className="max-w-7xl mx-auto px-6 py-32 border-t border-slate-800">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl font-bold mb-6">
                Built for Businesses That <span className="text-blue-400">Live in Their Docs</span>
              </h2>
              <p className="text-lg text-slate-400 mb-6 leading-relaxed">
                Your company already has all the answers — in PDFs, Word files, FAQs, and internal wikis.
              </p>
              <p className="text-lg text-slate-300 leading-relaxed">
                Weaver reads them, understands them, and builds a private AI assistant that speaks your brand's voice.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {['PDF', 'DOCX', 'TXT', 'HTML'].map((format, i) => (
                <div 
                  key={format}
                  className="p-6 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-blue-500/50 transition-all duration-300 hover:scale-105"
                  style={{ animationDelay: `${i * 100}ms` }}
                >
                  <div className="text-3xl mb-2">📄</div>
                  <div className="text-xl font-semibold">{format}</div>
                  <div className="text-sm text-slate-500 mt-1">Supported</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="max-w-7xl mx-auto px-6 py-32">
          <h2 className="text-5xl font-bold text-center mb-20">
            How It <span className="text-blue-500">Works</span>
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { 
                step: '01', 
                icon: '📤', 
                title: 'Upload your documents', 
                desc: 'PDFs, DOCX, TXT — drag and drop right into your dashboard.',
                color: 'blue'
              },
              { 
                step: '02', 
                icon: '🤖', 
                title: 'Weaver builds your bot', 
                desc: 'Your content is chunked, embedded, and indexed securely using Google Cloud + pgvector.',
                color: 'purple'
              },
              { 
                step: '03', 
                icon: '🚀', 
                title: 'Deploy anywhere', 
                desc: 'Get an API endpoint you can embed in your site, app, or internal tools.',
                color: 'pink'
              },
            ].map((item) => (
              <div 
                key={item.step}
                className="group relative p-8 rounded-2xl bg-slate-800/30 border border-slate-700 hover:border-slate-600 transition-all duration-300 hover:-translate-y-2"
              >
                <div className="absolute top-4 right-4 text-6xl font-bold text-slate-800">{item.step}</div>
                <div className="text-5xl mb-4">{item.icon}</div>
                <h3 className="text-2xl font-bold mb-3">{item.title}</h3>
                <p className="text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Why Choose Weaver */}
        <section className="max-w-7xl mx-auto px-6 py-32 border-t border-slate-800">
          <h2 className="text-5xl font-bold text-center mb-20">
            Why Teams Choose <span className="text-blue-400">Weaver</span>
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              { icon: '💬', title: 'Custom AI trained on your knowledge', desc: 'Every response is grounded in your actual content — not the open internet.' },
              { icon: '🔐', title: 'Secure, private, multi-tenant architecture', desc: 'Your data never mixes with anyone else\'s. Hosted entirely on Google Cloud with per-tenant isolation.' },
              { icon: '⚡', title: 'Blazing fast responses', desc: 'RAG pipeline built with LangChain + Gemini, optimized to answer in under 2 seconds.' },
              { icon: '🧩', title: 'Integrate anywhere', desc: 'Call your bot via REST API. Connect to your app, CRM, or customer portal in minutes.' },
              { icon: '📊', title: 'Built-in analytics', desc: 'See what customers are asking, where your docs fall short, and how your AI performs.' },
              { icon: '🔒', title: 'Security First', desc: 'Per-tenant isolation, AES-256 encryption, TLS 1.3, key rotation, and access control built-in.' },
            ].map((feature, i) => (
              <div 
                key={i}
                className="p-6 rounded-xl bg-slate-800/50 border border-slate-700 hover:bg-slate-800/80 transition-all duration-300"
              >
                <div className="text-4xl mb-3">{feature.icon}</div>
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-slate-400">{feature.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Tech Stack */}
        <section className="max-w-7xl mx-auto px-6 py-32">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Under the Hood</h2>
            <p className="text-slate-400 text-lg">Enterprise-grade tech — without the enterprise complexity.</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: 'Google Gemini', tag: 'LLM' },
              { name: 'Postgres + pgvector', tag: 'Vector DB' },
              { name: 'Google Cloud Storage', tag: 'Storage' },
              { name: 'FastAPI', tag: 'Backend' },
              { name: 'React', tag: 'Frontend' },
              { name: 'Celery', tag: 'Workers' },
              { name: 'Supabase', tag: 'Auth' },
              { name: 'LangChain', tag: 'Framework' },
            ].map((tech) => (
              <div 
                key={tech.name}
                className="p-4 rounded-lg bg-slate-800/30 border border-slate-700 text-center hover:border-blue-500/50 transition-all duration-300"
              >
                <div className="font-semibold mb-1">{tech.name}</div>
                <div className="text-xs text-slate-500">{tech.tag}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Use Cases */}
        <section className="max-w-7xl mx-auto px-6 py-32 border-t border-slate-800">
          <h2 className="text-4xl font-bold text-center mb-16">Use Weaver For</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              'Customer support automation',
              'Internal knowledge assistants',
              'Product documentation Q&A',
              'HR & IT policy chatbots',
              'SaaS help centers',
              'Managed service FAQs',
            ].map((useCase, i) => (
              <div 
                key={i}
                className="p-6 rounded-xl bg-gradient-to-br from-slate-800/50 to-slate-800/30 border border-slate-700 hover:border-slate-600 transition-all"
              >
                <div className="text-blue-400 mb-2">✓</div>
                <div className="text-lg">{useCase}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Example */}
        <section className="max-w-4xl mx-auto px-6 py-32">
          <div className="p-12 rounded-2xl bg-gradient-to-br from-blue-900/30 to-purple-900/30 border border-blue-500/30">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-4">It's Simple</h2>
            </div>
            <div className="space-y-4 text-lg">
              <div className="flex items-start gap-4">
                <div className="text-3xl">📄</div>
                <div>
                  <div className="font-semibold mb-2">Upload your "Customer Support Manual.pdf"</div>
                  <div className="text-slate-400">↓</div>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="text-3xl">🤖</div>
                <div>
                  <div className="font-semibold mb-2">Weaver builds an AI bot that instantly knows:</div>
                  <div className="text-blue-400 italic">"What's your refund policy?"</div>
                  <div className="text-purple-400 italic">"How do I reset my password?"</div>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="text-3xl">✨</div>
                <div className="text-slate-300">
                  And answers accurately, <span className="text-green-400 font-semibold">24/7</span>.
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="max-w-4xl mx-auto px-6 py-32 text-center">
          <h2 className="text-5xl font-bold mb-6">
            Start Free. <span className="text-blue-500">Scale Securely.</span>
          </h2>
          <p className="text-xl text-slate-400 mb-12">
            Your business knowledge deserves an AI that actually knows your business.
          </p>
          <Button 
            onClick={session ? () => navigate('/dashboard') : handleGoogleLogin}
            disabled={isAuthenticating}
            size="lg"
            className="bg-blue-900 hover:bg-blue-500 text-white shadow-xl shadow-blue-500/30 text-xl px-12 h-16"
          >
            {isAuthenticating ? (
              <>
                <div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin mr-3"></div>
                Authenticating...
              </>
            ) : session ? (
              <>
                Go to Dashboard
                <svg className="w-6 h-6 ml-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </>
            ) : (
              <>
                Get Started with Weaver
                <svg className="w-6 h-6 ml-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </>
            )}
          </Button>
        </section>

        {/* Footer */}
        <footer className="border-t border-slate-800 py-12">
          <div className="max-w-7xl mx-auto px-6 text-center">
            <div className="text-2xl font-semibold mb-2">
              Weaver — weave your knowledge into intelligence.
            </div>
            <div className="text-slate-500 text-sm">
              © 2025 Weaver. Built with Gemini, LangChain, and ❤️
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}
````

## File: frontend/src/components/dashboard/APIKeysTab.tsx
````typescript
import { useState, useRef, useEffect } from 'react'
import { useAPIKeys, useCreateAPIKey, useRevokeAPIKey } from '@/hooks/useAPIKeys'
import { useDocuments } from '@/hooks/useDocuments'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Copy, Check, Trash2, Play, Square } from 'lucide-react'
import { API_URL } from '@/lib/axios'
import { toast } from 'sonner'
import type { APIKey } from '@/types'

const DEMO_BOT_ID = '00000000-0000-0000-0000-000000000000'

interface APIKeysTabProps {
  tenantId: string
}

export default function APIKeysTab({ tenantId }: APIKeysTabProps) {
  const [newKey, setNewKey] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [keyName, setKeyName] = useState('')
  const [activeCodeTab, setActiveCodeTab] = useState('curl')
  
  // Bot selector state
  const [selectedBot, setSelectedBot] = useState<'demo' | 'own'>('demo')
  
  // Test panel state
  const [testKey, setTestKey] = useState<string>('')
  const [testQuery, setTestQuery] = useState<string>('')
  const [stream, setStream] = useState<boolean>(true)
  const [testing, setTesting] = useState<boolean>(false)
  const [testOutput, setTestOutput] = useState<string>('')
  const [testError, setTestError] = useState<string>('')
  const abortControllerRef = useRef<AbortController | null>(null)

  const { data: keys = [], isLoading } = useAPIKeys(tenantId)
  const { data: documentsResponse } = useDocuments(tenantId, { limit: 5 })
  const createMutation = useCreateAPIKey(tenantId)
  const revokeMutation = useRevokeAPIKey(tenantId)
  
  const hasDocs = (documentsResponse?.total ?? 0) > 0
  const activeTenantId = selectedBot === 'demo' ? DEMO_BOT_ID : tenantId

  // Load test panel state from localStorage
  useEffect(() => {
    const savedKey = localStorage.getItem('wvr_test_key')
    const savedQuery = localStorage.getItem('wvr_test_query')
    if (savedKey) setTestKey(savedKey)
    if (savedQuery) setTestQuery(savedQuery)
  }, [])

  // Save test panel state to localStorage
  useEffect(() => {
    localStorage.setItem('wvr_test_key', testKey)
  }, [testKey])

  useEffect(() => {
    localStorage.setItem('wvr_test_query', testQuery)
  }, [testQuery])

  const handleCreateKey = async () => {
    if (!keyName.trim()) {
      toast.error('Please enter a key name')
      return
    }
    
    try {
      const result = await createMutation.mutateAsync(keyName)
      setNewKey(result.key)
      setKeyName('')
      setDialogOpen(false)
      toast.success('API key created successfully!')
    } catch (error: any) {
      toast.error(error?.message || 'Failed to create API key')
    }
  }

  const handleRevokeKey = async (keyId: string) => {
    try {
      await revokeMutation.mutateAsync(keyId)
      toast.success('API key revoked successfully')
    } catch (error: any) {
      toast.error(error?.message || 'Failed to revoke API key')
    }
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      toast.success('Copied to clipboard!')
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      toast.error('Failed to copy')
    }
  }

  const handleRunTest = async () => {
    if (!testKey || !testQuery) {
      toast.error('Please provide both API key and query')
      return
    }

    setTesting(true)
    setTestOutput('')
    setTestError('')
    abortControllerRef.current = new AbortController()

    try {
      if (stream) {
        // Streaming SSE
        const response = await fetch(
          `${API_URL}/v1/tenants/${activeTenantId}/query/stream?query=${encodeURIComponent(testQuery)}`,
          {
            headers: {
              'Authorization': `Bearer ${testKey}`,
              'Accept': 'text/event-stream',
            },
            signal: abortControllerRef.current.signal,
          }
        )

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const reader = response.body?.getReader()
        const decoder = new TextDecoder()

        if (!reader) throw new Error('No response body')

        let buffer = ''
        // eslint-disable-next-line no-constant-condition
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6)
              if (data === '[DONE]') continue
              
              try {
                const parsed = JSON.parse(data)
                if (parsed.content) {
                  setTestOutput((prev) => prev + parsed.content)
                } else if (parsed.sources) {
                  setTestOutput((prev) => prev + `\n\n📊 Confidence: ${parsed.confidence}\n📚 Sources: ${parsed.sources.length}`)
                }
              } catch (e) {
                // Ignore parse errors
              }
            }
          }
        }
      } else {
        // Non-streaming POST
        const response = await fetch(`${API_URL}/v1/tenants/${activeTenantId}/query`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${testKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: testQuery }),
          signal: abortControllerRef.current.signal,
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const result = await response.json()
        setTestOutput(
          `${result.answer}\n\n📊 Confidence: ${result.confidence}\n⏱️ Latency: ${result.latency_ms}ms\n📚 Sources: ${result.sources.length}`
        )
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        setTestError('Request cancelled')
        toast.info('Test cancelled')
      } else {
        setTestError(error.message)
        toast.error(error.message)
      }
    } finally {
      setTesting(false)
      abortControllerRef.current = null
    }
  }

  const handleStopTest = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
  }

  const handleUseNewKey = () => {
    if (newKey) {
      setTestKey(newKey)
      toast.success('API key added to test panel')
    }
  }

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold mb-2">API Keys</h2>
        <p className="text-gray-600">
          Manage API keys for programmatic access to your bot
        </p>
      </div>

      {/* API Endpoint Information */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="font-semibold mb-3 text-blue-900">Available Bot Endpoints</h3>
        
        <div className="space-y-3 mb-4">
          {/* Demo Bot Endpoint */}
          <div className="p-3 bg-white rounded border border-blue-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">🎯 Demo Bot</span>
              <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded font-medium">
                Ready to use
              </span>
            </div>
            <code className="text-xs text-gray-600 break-all block">
              POST {API_URL}/v1/tenants/{DEMO_BOT_ID}/query
            </code>
            <p className="text-xs text-gray-500 mt-1">
              Try out Weaver with pre-loaded sample content
            </p>
          </div>

          {/* User's Bot Endpoint */}
          <div className={`p-3 rounded border ${hasDocs ? 'bg-white border-blue-200' : 'bg-gray-100 border-gray-300 opacity-60'}`}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">📚 Your Bot</span>
              <span className={`text-xs px-2 py-1 rounded font-medium ${
                hasDocs 
                  ? 'text-green-600 bg-green-50' 
                  : 'text-gray-500 bg-gray-200'
              }`}>
                {hasDocs ? 'Ready' : 'Upload docs first'}
              </span>
            </div>
            <code className="text-xs text-gray-600 break-all block">
              POST {API_URL}/v1/tenants/{tenantId}/query
            </code>
            <p className="text-xs text-gray-500 mt-1">
              {hasDocs ? 'Query your custom knowledge base' : 'Upload documents to activate your bot'}
            </p>
          </div>
        </div>
        
        <Tabs value={activeCodeTab} onValueChange={setActiveCodeTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="curl">cURL</TabsTrigger>
            <TabsTrigger value="javascript">JavaScript</TabsTrigger>
            <TabsTrigger value="python">Python</TabsTrigger>
          </TabsList>
          
          <TabsContent value="curl" className="space-y-4">
            <div>
              <p className="text-sm text-gray-700 mb-2 font-medium">Non-streaming (POST):</p>
              <pre className="p-3 bg-white rounded border text-xs overflow-x-auto">
{`# Demo Bot
curl -X POST ${API_URL}/v1/tenants/${DEMO_BOT_ID}/query \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "What is Weaver?"}'

# Your Bot (replace with your tenant ID)
curl -X POST ${API_URL}/v1/tenants/${tenantId}/query \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "What is your product about?"}'`}
              </pre>
            </div>
            
            <div>
              <p className="text-sm text-gray-700 mb-2 font-medium">Streaming (SSE):</p>
              <pre className="p-3 bg-white rounded border text-xs overflow-x-auto">
{`# Demo Bot
curl -N -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Accept: text/event-stream" \\
  "${API_URL}/v1/tenants/${DEMO_BOT_ID}/query/stream?query=What+is+Weaver"

# Your Bot
curl -N -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Accept: text/event-stream" \\
  "${API_URL}/v1/tenants/${tenantId}/query/stream?query=What+is+your+product+about"`}
              </pre>
            </div>
          </TabsContent>
          
          <TabsContent value="javascript" className="space-y-4">
            <pre className="p-3 bg-white rounded border text-xs overflow-x-auto">
{`// Demo Bot - Non-streaming
const response = await fetch('${API_URL}/v1/tenants/${DEMO_BOT_ID}/query', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ query: 'What is Weaver?' }),
});
const data = await response.json();
console.log(data.answer);

// Your Bot - Streaming (replace tenantId)
const response = await fetch(
  '${API_URL}/v1/tenants/YOUR_TENANT_ID/query/stream?query=' + 
  encodeURIComponent('What is your product about?'),
  {
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY',
      'Accept': 'text/event-stream',
    },
  }
);

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      if (data.content) console.log(data.content);
    }
  }
}`}
            </pre>
          </TabsContent>
          
          <TabsContent value="python" className="space-y-4">
            <pre className="p-3 bg-white rounded border text-xs overflow-x-auto">
{`import requests
import json

# Demo Bot - Non-streaming
response = requests.post(
    '${API_URL}/v1/tenants/${DEMO_BOT_ID}/query',
    headers={'Authorization': 'Bearer YOUR_API_KEY'},
    json={'query': 'What is Weaver?'}
)
data = response.json()
print(data['answer'])

# Your Bot - Streaming (replace YOUR_TENANT_ID)
response = requests.get(
    '${API_URL}/v1/tenants/YOUR_TENANT_ID/query/stream',
    params={'query': 'What is your product about?'},
    headers={
        'Authorization': 'Bearer YOUR_API_KEY',
        'Accept': 'text/event-stream'
    },
    stream=True
)

for line in response.iter_lines():
    if line.startswith(b'data: '):
        data = json.loads(line[6:])
        if 'content' in data:
            print(data['content'], end='', flush=True)`}
            </pre>
          </TabsContent>
        </Tabs>
      </div>

      {/* Create New Key */}
      <div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>Create New API Key</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create API Key</DialogTitle>
              <DialogDescription>
                Give your API key a descriptive name to help you identify it later.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <label htmlFor="keyName" className="block text-sm font-medium mb-2">
                  Key Name
                </label>
                <Input
                  id="keyName"
                  placeholder="e.g., Production API, Test Environment"
                  value={keyName}
                  onChange={(e) => setKeyName(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleCreateKey()}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="ghost" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateKey} disabled={createMutation.isPending || !keyName.trim()}>
                {createMutation.isPending ? 'Creating...' : 'Create Key'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* New Key Display */}
      {newKey && (
        <div className="p-4 bg-yellow-50 border border-yellow-300 rounded-lg">
          <p className="font-semibold mb-2 text-yellow-900">
            New API Key (save this, it won't be shown again):
          </p>
          <div className="flex items-center gap-2 mb-3">
            <code className="flex-1 p-3 bg-white rounded font-mono text-sm border">
              {newKey}
            </code>
            <Button
              onClick={() => copyToClipboard(newKey)}
              variant="secondary"
              size="icon"
              title="Copy to clipboard"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-600" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </Button>
          </div>
          <div className="flex gap-2">
            <Button
              onClick={handleUseNewKey}
              variant="secondary"
              size="sm"
            >
              Add to Test Panel
            </Button>
            <Button
              onClick={() => setNewKey(null)}
              variant="ghost"
              size="sm"
            >
              Dismiss
            </Button>
          </div>
        </div>
      )}

      {/* Keys List */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Your API Keys</h3>
        {keys.length === 0 ? (
          <div className="text-center py-12 border-2 border-dashed rounded-lg">
            <p className="text-gray-600 mb-4">No API keys yet.</p>
            <Button onClick={() => setDialogOpen(true)}>Create your first key</Button>
          </div>
        ) : (
          <div className="space-y-3">
            {keys.map((key: APIKey) => (
              <div
                key={key.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
              >
                <div className="flex-1">
                  <p className="font-medium">{key.name || 'Unnamed Key'}</p>
                  <div className="text-sm text-gray-600 space-y-1 mt-1">
                    <p>Created: {new Date(key.created_at).toLocaleDateString()}</p>
                    {key.last_used_at && (
                      <p>Last used: {new Date(key.last_used_at).toLocaleDateString()}</p>
                    )}
                    <p>Rate limit: {key.rate_limit_rpm} rpm</p>
                  </div>
                </div>
                <Button
                  onClick={() => handleRevokeKey(key.id)}
                  disabled={key.revoked || revokeMutation.isPending}
                  variant={key.revoked ? 'secondary' : 'destructive'}
                  size="sm"
                >
                  {key.revoked ? (
                    'Revoked'
                  ) : (
                    <>
                      <Trash2 className="w-4 h-4 mr-2" />
                      Revoke
                    </>
                  )}
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Test Your Bot Panel */}
      <div className="border-t pt-6">
        <h3 className="text-lg font-semibold mb-4">Test Your Bot</h3>
        <div className="space-y-4 p-4 bg-gray-50 rounded-lg border">
          {/* Bot Selector */}
          <div className="flex items-center gap-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <label className="text-sm font-medium text-gray-700">Query:</label>
            <div className="flex gap-2">
              <button
                onClick={() => setSelectedBot('demo')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedBot === 'demo'
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                🎯 Demo Bot
              </button>
              <button
                onClick={() => hasDocs && setSelectedBot('own')}
                disabled={!hasDocs}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedBot === 'own' && hasDocs
                    ? 'bg-blue-600 text-white shadow-sm'
                    : hasDocs
                    ? 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 cursor-pointer'
                    : 'bg-white text-gray-400 border border-gray-300 cursor-not-allowed opacity-60'
                }`}
                title={!hasDocs ? 'Upload documents first to test your own bot' : 'Test your custom bot'}
              >
                📚 Your Bot {!hasDocs && '(Upload docs first)'}
              </button>
            </div>
          </div>

          {/* Info Banner */}
          {selectedBot === 'demo' && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm">
              <p className="text-yellow-800">
                <strong>Testing Demo Bot:</strong> Try out Weaver with pre-loaded sample content.
                Upload your own documents to create your custom bot!
              </p>
            </div>
          )}

          <div>
            <label htmlFor="testKey" className="block text-sm font-medium mb-2">
              API Key
            </label>
            <Input
              id="testKey"
              type="password"
              placeholder="Paste your API key here"
              value={testKey}
              onChange={(e) => setTestKey(e.target.value)}
            />
          </div>

          <div>
            <label htmlFor="testQuery" className="block text-sm font-medium mb-2">
              Query
            </label>
            <textarea
              id="testQuery"
              className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder={selectedBot === 'demo' ? "Ask about Weaver..." : "Ask your bot a question..."}
              value={testQuery}
              onChange={(e) => setTestQuery(e.target.value)}
            />
          </div>

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={stream}
                onChange={(e) => setStream(e.target.checked)}
                className="rounded"
              />
              Stream response (SSE)
            </label>
          </div>

          <div className="flex gap-2">
            {!testing ? (
              <Button onClick={handleRunTest} disabled={!testKey || !testQuery}>
                <Play className="w-4 h-4 mr-2" />
                Run Test
              </Button>
            ) : (
              <Button onClick={handleStopTest} variant="destructive">
                <Square className="w-4 h-4 mr-2" />
                Stop
              </Button>
            )}
          </div>

          {/* Output */}
          {(testOutput || testError || testing) && (
            <div>
              <label className="block text-sm font-medium mb-2">Response</label>
              <div 
                className="p-4 bg-white border rounded-md min-h-[200px] max-h-[400px] overflow-y-auto font-mono text-sm whitespace-pre-wrap"
                aria-live="polite"
              >
                {testing && !testOutput && (
                  <span className="text-gray-400">Streaming response...</span>
                )}
                {testOutput && <div>{testOutput}</div>}
                {testError && (
                  <div className="text-red-600">Error: {testError}</div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
````
