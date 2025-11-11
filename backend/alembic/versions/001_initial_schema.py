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
            VALUES (NEW.id, NEW.id, NEW.name || ' Bot', '{"temperature": 0.2, "top_k": 8}')
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

