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

