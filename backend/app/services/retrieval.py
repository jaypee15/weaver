import time
import logging
import asyncio
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
        self.rrf_k = 60

    async def reciprocal_rank_fusion(self, results_lists: List[List[dict]]) -> List[dict]:
        """
        Combine multiple ranked lists using Reciprocal Rank Fusion.
        Formula: score = 1 / (k + rank)
        """

        fused_scores: Dict[str, float] = {}
        doc_map: Dict[str, dict] = {}

        for results in results_lists:
            for rank, doc in enumerate(results):
                doc_id = doc["id"]

                if doc_id not in doc_map:
                    doc_map[doc_id] = doc
                    fused_scores[doc_id] = 0.0
                
                fused_scores[doc_id] += 1 / (self.rrf_k + rank +1)

        sorted_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)

        final_results = []
        for doc_id in sorted_ids:
            doc = doc_map[doc_id]
            # adda fusion score for debugging
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
        
        # Time embedding generation
        start_time = time.time()
        query_embedding = await self.embedding_service.embed_text(query)

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

        results = await asyncio.gather(vector_task, keyword_task)
        vector_results, keyword_results = results[0], results[1]

        # apply reciprocal rank fusion
        fused_results = self.reciprocal_rank_fusion([vector_results, keyword_results])

        final_results = fused_results[:top_k]
        total_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            f"Hybrid retrieval - tenant:{tenant_id} | time:{total_ms}ms | "
            f"vector_found:{len(vector_results)} | keyword_found:{len(keyword_results)} | "
            f"fused:{len(final_results)}"
        )
        
        return final_results

