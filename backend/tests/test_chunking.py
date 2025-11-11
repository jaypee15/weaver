from app.workers.tasks import chunk_text


def test_chunk_text():
    text = " ".join([f"word{i}" for i in range(1000)])
    
    chunks = chunk_text(text, chunk_size=100, overlap_pct=20)
    
    assert len(chunks) > 1
    assert all(isinstance(chunk, str) for chunk in chunks)
    
    first_chunk_words = chunks[0].split()
    second_chunk_words = chunks[1].split()
    
    assert len(first_chunk_words) == 100
    
    overlap_words = set(first_chunk_words[-20:]) & set(second_chunk_words[:20])
    assert len(overlap_words) > 0


def test_chunk_text_small():
    text = "This is a small text"
    
    chunks = chunk_text(text, chunk_size=100, overlap_pct=20)
    
    assert len(chunks) == 1
    assert chunks[0] == text

