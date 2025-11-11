from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update, delete, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.connection import AsyncSessionLocal
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
    async def create_document(
        self,
        tenant_id: UUID,
        filename: str,
        gcs_path: str,
        size_bytes: int,
    ) -> UUID:
        async with AsyncSessionLocal() as session:
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
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(Document)
                .where(Document.id == doc_id)
                .values(status=status, error_message=error_message)
            )
            await session.commit()
    
    async def list_by_tenant(self, tenant_id: UUID) -> List[dict]:
        """List all documents for a tenant"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Document)
                .where(Document.tenant_id == tenant_id)
                .order_by(desc(Document.created_at))
            )
            documents = result.scalars().all()
            
            return [
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
            ]


class ChunkRepository:
    async def insert_chunks(self, chunks: List[dict]):
        async with AsyncSessionLocal() as session:
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
        async with AsyncSessionLocal() as session:
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
                    "id": row[0],
                    "doc_id": row[1],
                    "text": row[2],
                    "page_num": row[3],
                    "metadata": row[4],
                    "similarity": row[5],
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
            }


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
            bot_query = BotQuery(
                tenant_id=tenant_id,
                api_key_id=api_key_id,
                query=query,
                answer=answer,
                confidence=confidence,
                latency_ms=latency_ms,
                sources=sources,
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
