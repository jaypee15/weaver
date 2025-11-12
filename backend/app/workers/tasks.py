import io
import asyncio
from uuid import UUID
from typing import List
from celery import Celery
import fitz
from docx import Document
import html2text

from app.config import settings
from app.services.embeddings import EmbeddingService
from app.services.storage import StorageService
from app.db.repositories import DocumentRepository, ChunkRepository

# Monkey-patch the repositories to use worker connection
# This ensures workers use Transaction Mode (port 6543) with statement_cache_size=0
from app.workers.db import WorkerAsyncSessionLocal
from app.db import connection
connection.AsyncSessionLocal = WorkerAsyncSessionLocal

celery_app = Celery(
    "weaver",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


def extract_text_from_pdf(content: bytes) -> List[dict]:
    chunks = []
    doc = fitz.open(stream=content, filetype="pdf")
    
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        if text.strip():
            chunks.append({
                "text": text,
                "page_num": page_num,
            })
    
    return chunks


def extract_text_from_docx(content: bytes) -> List[dict]:
    doc = Document(io.BytesIO(content))
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    
    return [{"text": text, "page_num": None}]


def extract_text_from_txt(content: bytes) -> List[dict]:
    text = content.decode("utf-8", errors="ignore")
    return [{"text": text, "page_num": None}]


def extract_text_from_html(content: bytes) -> List[dict]:
    html = content.decode("utf-8", errors="ignore")
    h = html2text.HTML2Text()
    h.ignore_links = False
    text = h.handle(html)
    
    return [{"text": text, "page_num": None}]


def chunk_text(text: str, chunk_size: int = 800, overlap_pct: int = 20) -> List[str]:
    words = text.split()
    overlap_size = int(chunk_size * overlap_pct / 100)
    
    chunks = []
    start = 0
    
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap_size
    
    return chunks


@celery_app.task(bind=True, max_retries=3)
def process_document(self, doc_id: str, tenant_id: str, gcs_path: str):
    """Process document - wrapper that calls async function"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_process_document_async(doc_id, tenant_id, gcs_path))
    except Exception as e:
        doc_repo = DocumentRepository()
        loop.run_until_complete(doc_repo.update_status(UUID(doc_id), "failed", str(e)))
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    finally:
        loop.close()


async def _process_document_async(doc_id: str, tenant_id: str, gcs_path: str):
    """Async function that does the actual document processing"""
    doc_repo = DocumentRepository()
    chunk_repo = ChunkRepository()
    embedding_service = EmbeddingService()
    
    # Download file from GCS
    content = StorageService.download_file(
        bucket_name=settings.GCS_BUCKET_NAME,
        key=gcs_path
    )
    
    filename = gcs_path.split("/")[-1]
    ext = filename.lower().split(".")[-1]
    
    if ext == "pdf":
        extracted = extract_text_from_pdf(content)
    elif ext in ["docx", "doc"]:
        extracted = extract_text_from_docx(content)
    elif ext == "txt":
        extracted = extract_text_from_txt(content)
    elif ext in ["html", "htm"]:
        extracted = extract_text_from_html(content)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    all_chunks = []
    chunk_index = 0
    
    for page_data in extracted:
        text_chunks = chunk_text(
            page_data["text"],
            chunk_size=settings.CHUNK_SIZE,
            overlap_pct=settings.CHUNK_OVERLAP_PCT,
        )
        
        for text_chunk in text_chunks:
            all_chunks.append({
                "text": text_chunk,
                "page_num": page_data.get("page_num"),
                "chunk_index": chunk_index,
            })
            chunk_index += 1
    
    texts = [c["text"] for c in all_chunks]
    embeddings = await embedding_service.embed_documents(texts)
    
    chunk_records = []
    for chunk, embedding in zip(all_chunks, embeddings):
        chunk_records.append({
            "doc_id": doc_id,
            "tenant_id": tenant_id,
            "embedding": embedding,
            "text": chunk["text"],
            "page_num": chunk["page_num"],
            "chunk_index": chunk["chunk_index"],
            "metadata": {},
        })
    
    await chunk_repo.insert_chunks(chunk_records)
    await doc_repo.update_status(UUID(doc_id), "completed")

