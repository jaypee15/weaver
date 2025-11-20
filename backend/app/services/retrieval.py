import time
import logging
import asyncio
from typing import List, Dict
from uuid import UUID

from app.services.embeddings import EmbeddingService
from app.db.repositories import ChunkRepository
from app.config import settings

logger = logging.getLogger(__name__)


class RetrievalService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.chunk_repo = ChunkRepository()
        self.rrf_k = 60  # Standard RRF constant
    
    def _reciprocal_rank_fusion(self, results_lists: List[List[dict]]) -> List[dict]:
        """
        Combine multiple ranked lists using Reciprocal Rank Fusion.
        Formula: score = 1 / (k + rank)
        """
        fused_scores: Dict[str, float] = {}
        doc_map: Dict[str, dict] = {}
        
        for results in results_lists:
            for rank, doc in enumerate(results):
                doc_id = doc["id"] # Chunk UUID
                
                # Store doc data if we haven't seen it
                if doc_id not in doc_map:
                    doc_map[doc_id] = doc
                    # Initialize score
                    fused_scores[doc_id] = 0.0
                
                # Add RRF score
                fused_scores[doc_id] += 1 / (self.rrf_k + rank + 1)
        
        # Sort by fused score descending
        sorted_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)
        
        # Return final re-ranked list with normalization
        final_results = []
        for doc_id in sorted_ids:
            doc = doc_map[doc_id]
            # We add a 'fusion_score' for debugging/analytics
            doc["similarity"] = fused_scores[doc_id] 
            final_results.append(doc)
            
        return final_results

    async def retrieve_context(
        self,
        tenant_id: UUID,
        query: str,
        top_k: int = None,
    ) -> List[dict]:
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
            
        start_time = time.time()
        
        # 1. Generate Embedding (Async)
        query_embedding = await self.embedding_service.embed_text(query)
        
        # 2. Run Hybrid Search concurrently (Vector + Keyword)
        # We request slightly more candidates (top_k * 2) from each source 
        # to maximize the chance of finding overlapping relevant documents for RRF
        candidate_k = top_k * 2
        
        vector_task = self.chunk_repo.search_similar(
            tenant_id=tenant_id,
            query_embedding=query_embedding,
            top_k=candidate_k,
        )
        
        keyword_task = self.chunk_repo.search_keyword(
            tenant_id=tenant_id,
            query_text=query,
            top_k=candidate_k,
        )
        
        # Execute in parallel
        results = await asyncio.gather(vector_task, keyword_task)
        vector_results, keyword_results = results[0], results[1]
        
        # 3. Apply Reciprocal Rank Fusion
        fused_results = self._reciprocal_rank_fusion([vector_results, keyword_results])
        
        # 4. Slice to final top_k
        final_results = fused_results[:top_k]
        
        total_ms = int((time.time() - start_time) * 1000)
        logger.info(
            f"Hybrid retrieval - tenant:{tenant_id} | time:{total_ms}ms | "
            f"vector_found:{len(vector_results)} | keyword_found:{len(keyword_results)} | "
            f"fused:{len(final_results)}"
        )
        
        return final_results