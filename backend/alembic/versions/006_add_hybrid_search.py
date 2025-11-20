"""add hybrid search and optimize hnsw

Revision ID: 006
Revises: 005
Create Date: 2025-11-19

"""
from alembic import op
import sqlalchemy as sa

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Add search_vector
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='doc_chunks' AND column_name='search_vector') THEN
                ALTER TABLE doc_chunks
                ADD COLUMN search_vector tsvector
                GENERATED ALWAYS AS (to_tsvector('english', text)) STORED;
            END IF;
        END $$;
    """)

    # 2. Indexes
    op.execute("CREATE INDEX IF NOT EXISTS idx_doc_chunks_search_vector ON doc_chunks USING gin (search_vector)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_doc_chunks_metadata ON doc_chunks USING gin (chunk_metadata)")

    # 3. Optimize HNSW
    op.execute("DROP INDEX IF EXISTS idx_doc_chunks_embedding")
    op.execute("DROP INDEX IF EXISTS idx_doc_chunks_embedding_hnsw")
    # Note: We do NOT drop idx_doc_chunks_tenant_embedding here because it was just created in 004
    # and works fine. We only replace the main one.

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_doc_chunks_vec_hnsw 
        ON doc_chunks 
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 32, ef_construction = 128)
    """)
    
    op.execute("ANALYZE doc_chunks")

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_doc_chunks_vec_hnsw")
    op.execute("DROP INDEX IF EXISTS idx_doc_chunks_metadata")
    op.execute("DROP INDEX IF EXISTS idx_doc_chunks_search_vector")
    op.drop_column('doc_chunks', 'search_vector')
    
    # Restore old basic index
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_doc_chunks_embedding 
        ON doc_chunks 
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)