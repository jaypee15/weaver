import time
import json
import logging
from typing import AsyncIterator
from uuid import UUID

from app.services.retrieval import RetrievalService
from app.services.llm import LLMService
from app.db.repositories import QueryLogRepository, BotRepository
from app.api.v1.schemas import QueryResponse, Source
from app.services.cache import cache_service

logger = logging.getLogger(__name__)


class QueryService:
    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.llm_service = LLMService()
        self.query_log_repo = QueryLogRepository()
        self.bot_repo = BotRepository()
        self.query_cache_ttl = 300  # 5 minutes cache for query results
    
    async def query(
        self,
        tenant_id: UUID,
        query: str,
        api_key_id: UUID,
    ) -> QueryResponse:
        start_time = time.time()
        timings = {}
        
        # Fetch bot config (includes system_prompt if customized)
        bot = await self.bot_repo.get_by_tenant(tenant_id)
        bot_config = bot.get("config", {}) if bot else {}
        
        # Check cache first
        cache_key = cache_service.generate_key("query", str(tenant_id), query.lower().strip())
        cached = cache_service.get(cache_key)
        if cached:
            logger.info(f"Cache HIT for tenant:{tenant_id}")
            # Still log the cached query
            await self.query_log_repo.log_query(
                tenant_id=tenant_id,
                api_key_id=api_key_id,
                query=query,
                answer=cached['answer'],
                confidence=cached['confidence'],
                latency_ms=cached['latency_ms'],
                sources=cached['sources'],
            )
            return QueryResponse(**cached)
        
        # Retrieval (embedding + vector search)
        t1 = time.time()
        context_chunks = await self.retrieval_service.retrieve_context(
            tenant_id=tenant_id,
            query=query,
        )
        timings['retrieval_ms'] = int((time.time() - t1) * 1000)
        
        if not context_chunks:
            answer = "I don't know based on the available information."
            confidence = "low"
            sources = []
            timings['llm_ms'] = 0
        else:
            # LLM generation with bot config (includes system_prompt)
            t2 = time.time()
            answer = await self.llm_service.generate_answer(query, context_chunks, bot_config)
            timings['llm_ms'] = int((time.time() - t2) * 1000)
            
            avg_similarity = sum(c["similarity"] for c in context_chunks) / len(context_chunks)
            if avg_similarity > 0.8:
                confidence = "high"
            elif avg_similarity > 0.6:
                confidence = "medium"
            else:
                confidence = "low"
            
            sources = [
                Source(
                    doc_id=chunk["doc_id"],
                    page=chunk.get("page_num"),
                    confidence=chunk["similarity"],
                )
                for chunk in context_chunks[:3]
            ]
        
        latency_ms = int((time.time() - start_time) * 1000)
        timings['total_ms'] = latency_ms
        
        logger.info(f"Query performance - tenant:{tenant_id} | timings:{timings} | chunks:{len(context_chunks)}")
        
        await self.query_log_repo.log_query(
            tenant_id=tenant_id,
            api_key_id=api_key_id,
            query=query,
            answer=answer,
            confidence=confidence,
            latency_ms=latency_ms,
            sources=[
                {
                    "doc_id": str(s.doc_id),
                    "page": s.page,
                    "confidence": s.confidence,
                }
                for s in sources
            ],
        )
        
        response = QueryResponse(
            answer=answer,
            sources=sources,
            confidence=confidence,
            latency_ms=latency_ms,
        )
        
        # Cache the result for future identical queries
        cache_data = {
            "answer": answer,
            "sources": [{"doc_id": str(s.doc_id), "page": s.page, "confidence": s.confidence} for s in sources],
            "confidence": confidence,
            "latency_ms": latency_ms,
        }
        if cache_service.set(cache_key, cache_data, self.query_cache_ttl):
            logger.info(f"Cached query result for tenant:{tenant_id}")
        
        return response
    
    async def query_stream(
        self,
        tenant_id: UUID,
        query: str,
        api_key_id: UUID,
    ) -> AsyncIterator[str]:
        start_time = time.time()
        
        # Fetch bot config (includes system_prompt if customized)
        bot = await self.bot_repo.get_by_tenant(tenant_id)
        bot_config = bot.get("config", {}) if bot else {}
        
        context_chunks = await self.retrieval_service.retrieve_context(
            tenant_id=tenant_id,
            query=query,
        )
        
        if not context_chunks:
            yield f"data: {json.dumps({'content': "I don't know based on the available information."})}\n\n"
            return
        
        full_answer = ""
        async for chunk in self.llm_service.generate_answer_stream(query, context_chunks, bot_config):
            full_answer += chunk
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        
        avg_similarity = sum(c["similarity"] for c in context_chunks) / len(context_chunks)
        if avg_similarity > 0.8:
            confidence = "high"
        elif avg_similarity > 0.6:
            confidence = "medium"
        else:
            confidence = "low"
        
        sources = [
            {
                "doc_id": str(chunk["doc_id"]),
                "page": chunk.get("page_num"),
                "confidence": chunk["similarity"],
            }
            for chunk in context_chunks[:3]
        ]
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        await self.query_log_repo.log_query(
            tenant_id=tenant_id,
            api_key_id=api_key_id,
            query=query,
            answer=full_answer,
            confidence=confidence,
            latency_ms=latency_ms,
            sources=sources,
        )
        
        yield f"data: {json.dumps({'sources': sources, 'confidence': confidence})}\n\n"
        yield "data: [DONE]\n\n"

