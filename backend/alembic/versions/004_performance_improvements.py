"""performance improvements

Revision ID: 004
Revises: 003
Create Date: 2025-11-17

"""
from alembic import op
import sqlalchemy as sa

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    # Add composite index for tenant-specific vector search
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_doc_chunks_tenant_embedding 
        ON doc_chunks 
        USING hnsw (embedding vector_cosine_ops) 
        WHERE tenant_id IS NOT NULL
    """)
    
    # Add index for created_at on bot_queries
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_bot_queries_tenant_created 
        ON bot_queries (tenant_id, created_at DESC)
    """)

def downgrade():
    op.execute('DROP INDEX IF EXISTS idx_doc_chunks_tenant_embedding')
    op.execute('DROP INDEX IF EXISTS idx_bot_queries_tenant_created')