import time
import json
from typing import AsyncIterator
from uuid import UUID

from app.services.retrieval import RetrievalService
from app.services.llm import LLMService
from app.db.repositories import QueryLogRepository
from app.api.v1.schemas import QueryResponse, Source


class QueryService:
    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.llm_service = LLMService()
        self.query_log_repo = QueryLogRepository()
    
    async def query(
        self,
        tenant_id: UUID,
        query: str,
        api_key_id: UUID,
    ) -> QueryResponse:
        start_time = time.time()
        
        context_chunks = await self.retrieval_service.retrieve_context(
            tenant_id=tenant_id,
            query=query,
        )
        
        if not context_chunks:
            answer = "I don't know based on the available information."
            confidence = "low"
            sources = []
        else:
            answer = await self.llm_service.generate_answer(query, context_chunks)
            
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
        
        context_chunks = await self.retrieval_service.retrieve_context(
            tenant_id=tenant_id,
            query=query,
        )
        
        if not context_chunks:
            yield f"data: {json.dumps({'content': "I don't know based on the available information."})}\n\n"
            return
        
        full_answer = ""
        async for chunk in self.llm_service.generate_answer_stream(query, context_chunks):
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

