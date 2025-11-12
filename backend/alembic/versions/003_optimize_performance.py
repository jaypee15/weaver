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

