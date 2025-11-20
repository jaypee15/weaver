"""add semantic cache

Revision ID: 007
Revises: 006
Create Date: 2025-11-20

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Add the vector column
    op.add_column('bot_queries', sa.Column('query_embedding', Vector(1536), nullable=True))

    # 2. Create HNSW index for semantic search
    # We only index 'high' confidence answers to avoid caching bad data
    op.execute("""
        CREATE INDEX idx_bot_queries_semantic_cache 
        ON bot_queries 
        USING hnsw (query_embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        WHERE confidence = 'high'
    """)

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_bot_queries_semantic_cache")
    op.drop_column('bot_queries', 'query_embedding')