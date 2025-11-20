import time
import json
import logging
import asyncio
from typing import AsyncIterator, List
from uuid import UUID

from app.services.retrieval import RetrievalService
from app.services.llm import LLMService
from app.db.repositories import QueryLogRepository, BotRepository
from app.api.v1.schemas import QueryResponse, Source
from app.services.cache import cache_service

logger = logging.getLogger(__name__)


class QueryService:
    SLOW_RETRIEVAL_THRESHOLD_MS = 1000
    SLOW_LLM_THRESHOLD_MS = 3000
    SLOW_TOTAL_THRESHOLD_MS = 4000
    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.llm_service = LLMService()
        self.query_log_repo = QueryLogRepository()
        self.bot_repo = BotRepository()
        self.query_cache_ttl = 600  # 10 minutes cache for query results
    
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
        
        # Check cache (exact match)
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
        
        # Generate embedding
        t1 = time.time()
        query_embedding = await self.retrieval_service.embedding_service.embed_text(query)
        timings['embedding_ms'] = int((time.time() - t1) * 1000)

        # Check Semantic Cache (Similarity Match)
        similar_query = await self.query_log_repo.find_similar_query(
            tenant_id=tenant_id,
            query_embedding=query_embedding,
            threshold=0.95
        )

        if similar_query:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.info(f"Semantic Cache HIT - tenant:{tenant_id} | sim:{similar_query['similarity']:.4f}")
            
            # Log the hit and save the new query's embedding to reinforce the cache
            await self.query_log_repo.log_query(
                tenant_id=tenant_id,
                api_key_id=api_key_id,
                query=query,
                answer=similar_query['answer'],
                confidence="high", 
                latency_ms=latency_ms,
                sources=similar_query['sources'],
                query_embedding=query_embedding 
            )
            
            # Cache in Redis for exact-match speed next time
            cache_data = {
                "answer": similar_query['answer'],
                "sources": similar_query['sources'],
                "confidence": "high",
                "latency_ms": latency_ms,
            }
            cache_service.set(cache_key, cache_data, self.query_cache_ttl)

            return QueryResponse(
                answer=similar_query['answer'],
                sources=similar_query['sources'],
                confidence="high",
                latency_ms=latency_ms
            )

        
        t_retrieval = time.time()
        context_chunks = await self.retrieval_service.retrieve_context(
            tenant_id=tenant_id,
            query=query,
        )
        timings['retrieval_ms'] = int((time.time() - t_retrieval) * 1000)
        
        if not context_chunks:
            answer = "I don't know based on the available information."
            confidence = "low"
            sources = []
        else:
            # LLM generation with bot config (includes system_prompt)
            t_llm = time.time()
            answer = await self.llm_service.generate_answer(query, context_chunks, bot_config)
            timings['llm_ms'] = int((time.time() - t_llm) * 1000)
            if timings['llm_ms'] > self.SLOW_LLM_THRESHOLD_MS:
                logger.warning(
                    "Slow LLM generation detected",
                    extra={
                        "tenant_id": str(tenant_id),
                        "llm_ms": timings['llm_ms'],
                        "context_chunks": len(context_chunks),
                    },
                )
            
            avg_similarity = sum(c.get("similarity", 0.0) for c in context_chunks) / len(context_chunks)
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
                    confidence=chunk.get("similarity", 0.0),
                )
                for chunk in context_chunks[:3]
            ]
        
        latency_ms = int((time.time() - start_time) * 1000)
        timings['total_ms'] = latency_ms

        logger.info(f"Query Miss - tenant:{tenant_id} | timings:{timings}")
        
        if latency_ms > self.SLOW_TOTAL_THRESHOLD_MS:
            logger.warning(
                "Slow query detected",
                extra={
                    "tenant_id": str(tenant_id),
                    "latency_ms": latency_ms,
                    "retrieval_ms": timings.get("retrieval_ms", 0),
                    "llm_ms": timings.get("llm_ms", 0),
                },
            )
        
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
            query_embedding=query_embedding
        )
        
        # Cache result in Redis
        cache_data = {
            "answer": answer,
            "sources": [{"doc_id": str(s.doc_id), "page": s.page, "confidence": s.confidence} for s in sources],
            "confidence": confidence,
            "latency_ms": latency_ms,
        }
        cache_service.set(cache_key, cache_data, self.query_cache_ttl)
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            confidence=confidence,
            latency_ms=latency_ms,
        )
    
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

        # Generate Embedding (Needed for Cache & Retrieval)
        query_embedding = await self.retrieval_service.embedding_service.embed_text(query)
        
        # 2. Check Semantic Cache
        similar_query = await self.query_log_repo.find_similar_query(
            tenant_id=tenant_id,
            query_embedding=query_embedding,
            threshold=0.95
        )

        if similar_query:
            logger.info(f"Semantic Cache HIT (Stream) - tenant:{tenant_id}")
            
            # Simulate streaming the cached answer for UX consistency
            cached_answer = similar_query['answer']
            chunk_size = 15 # Characters per chunk
            
            for i in range(0, len(cached_answer), chunk_size):
                chunk = cached_answer[i:i+chunk_size]
                yield f"data: {json.dumps({'content': chunk})}\n\n"
                # Tiny sleep to simulate natural typing effect (optional)
                await asyncio.sleep(0.01) 
            
            # Log Hit
            await self.query_log_repo.log_query(
                tenant_id=tenant_id,
                api_key_id=api_key_id,
                query=query,
                answer=cached_answer,
                confidence="high",
                latency_ms=int((time.time() - start_time) * 1000),
                sources=similar_query['sources'],
                query_embedding=query_embedding
            )

            yield f"data: {json.dumps({'sources': similar_query['sources'], 'confidence': 'high'})}\n\n"
            yield "data: [DONE]\n\n"
            return
        
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
        
        avg_similarity = sum(c.get("similarity", 0.0) for c in context_chunks) / len(context_chunks)
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
                "confidence": chunk.get("similarity", 0.0),
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
            query_embedding=query_embedding
        )
        
        yield f"data: {json.dumps({'sources': sources, 'confidence': confidence})}\n\n"
        yield "data: [DONE]\n\n"

