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
            # Check cache for each text first
            cached_embeddings = []
            uncached_texts = []
            uncached_indices = []
            
            for i, text in enumerate(texts):
                cache_key = cache_service.generate_key("emb", text.lower().strip())
                cached = cache_service.get(cache_key)
                if cached:
                    cached_embeddings.append((i, cached))
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
            
            # Generate embeddings only for uncached texts
            if uncached_texts:
                new_embeddings = await self.embeddings.aembed_documents(
                    uncached_texts,
                    output_dimensionality=1536
                )
                
                # Cache new embeddings
                for text, embedding in zip(uncached_texts, new_embeddings):
                    cache_key = cache_service.generate_key("emb", text.lower().strip())
                    cache_service.set(cache_key, embedding, self.cache_ttl)
                
                # Merge cached and new embeddings in correct order
                result = [None] * len(texts)
                for i, emb in cached_embeddings:
                    result[i] = emb
                for i, emb in zip(uncached_indices, new_embeddings):
                    result[i] = emb
                
                return result
            
            # All cached - reconstruct in order
            result = [None] * len(texts)
            for i, emb in cached_embeddings:
                result[i] = emb
            return result
            
        except Exception as e:
            raise Exception(f"Batch embedding generation failed: {str(e)}")

