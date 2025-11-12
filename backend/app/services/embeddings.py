from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings
from app.services.cache import cache_service


class EmbeddingService:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=settings.GOOGLE_API_KEY,
            task_type="retrieval_document",
        )
        self.cache_ttl = 3600  # 1 hour cache
    
    async def embed_text(self, text: str) -> List[float]:
        try:
            # Try cache first
            cache_key = cache_service.generate_key("emb", text.lower().strip())
            cached = cache_service.get(cache_key)
            if cached:
                return cached
            
            # Generate embedding
            embedding = await self.embeddings.aembed_query(
                text,
                output_dimensionality=1536
            )
            
            # Cache for future use
            cache_service.set(cache_key, embedding, self.cache_ttl)
            
            return embedding
        except Exception as e:
            raise Exception(f"Embedding generation failed: {str(e)}")
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            # Pass output_dimensionality per call
            embeddings = await self.embeddings.aembed_documents(
                texts,
                output_dimensionality=1536
            )
            return embeddings
        except Exception as e:
            raise Exception(f"Batch embedding generation failed: {str(e)}")

