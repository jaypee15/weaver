from sqlalchemy import Column, String, Integer, BigInteger, Boolean, Text, TIMESTAMP, ForeignKey, UniqueConstraint, Index, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
import sqlalchemy as sa

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

    search_vector = Column(
        TSVECTOR, 
        sa.Computed("to_tsvector('english', text)", persisted=True)
    )
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
              postgresql_with={'m': 32, 'ef_construction': 128},
              postgresql_ops={'embedding': 'vector_cosine_ops'}),
        Index('idx_doc_chunks_search_vector', 'search_vector', postgresql_using='gin'),
        Index('idx_doc_chunks_metadata', 'chunk_metadata', postgresql_using='gin')
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
    query_embedding = Column(Vector(1536))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant", back_populates="bot_queries")
    api_key = relationship("APIKey", back_populates="bot_queries")
    
    __table_args__ = (
        Index('idx_bot_queries_tenant_id', 'tenant_id'),
        Index('idx_bot_queries_api_key_id', 'api_key_id'),
        Index('idx_bot_queries_created_at', 'created_at'),
        Index('idx_bot_queries_confidence', 'confidence'),

        # Use partial index to only index queries for high confidence answers
        Index('idx_bot_queries_semantic_cache', 'query_embedding', postgresql_using='hnsw',
        postgresql_with={'m': 16, 'ef_construction': 64},
        postgresql_ops={'query_embedding': 'vector_cosine_ops'},
        postgresql_where=text("confidence='high'")),
    )

