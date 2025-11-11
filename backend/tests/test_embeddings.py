import pytest
from app.services.embeddings import EmbeddingService


@pytest.mark.asyncio
async def test_embed_text():
    service = EmbeddingService()
    
    text = "This is a test document about password reset procedures."
    embedding = await service.embed_text(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == 1536
    assert all(isinstance(x, float) for x in embedding)


@pytest.mark.asyncio
async def test_embed_documents():
    service = EmbeddingService()
    
    texts = [
        "First document about authentication.",
        "Second document about authorization.",
    ]
    embeddings = await service.embed_documents(texts)
    
    assert len(embeddings) == 2
    assert all(len(emb) == 1536 for emb in embeddings)

