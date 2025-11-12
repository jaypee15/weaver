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

