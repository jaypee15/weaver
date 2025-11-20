import io
import asyncio
from uuid import UUID
from typing import List
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from celery import Celery
import fitz
from docx import Document
import html2text
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.services.embeddings import EmbeddingService
from app.services.storage import StorageService
from app.db.repositories import DocumentRepository, ChunkRepository
from app.workers.db import WorkerAsyncSessionLocal


def _ensure_rediss_ssl_params(url: str) -> str:
    """
    Celery's Redis backend requires rediss:// URLs to specify ssl_cert_reqs.
    Upstash uses TLS with CA verification, so we set ssl_cert_reqs=required if missing.
    """
    if not url.startswith("rediss://"):
        return url

    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query))

    if "ssl_cert_reqs" not in query:
        # Use 'required' to validate server certs (recommended for Upstash)
        query["ssl_cert_reqs"] = "required"

    new_query = urlencode(query)
    return urlunparse(parsed._replace(query=new_query))


redis_url = _ensure_rediss_ssl_params(settings.REDIS_URL)

celery_app = Celery(
    "weaver",
    broker=redis_url,
    backend=redis_url,
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
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    broker_pool_limit=None,
    broker_heartbeat=None,
    broker_connection_timeout=30,
    redis_socket_keepalive=True,
    redis_socket_keepalive_options={
        1: 30,  # TCP_KEEPIDLE
        2: 10,  # TCP_KEEPINTVL  
        3: 3,   # TCP_KEEPCNT
    },
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



def get_text_spliter(chunk_size: int = 1000, overlap: int = 200):
    """
    creates a splitter that respects semnatic boundaries.
    default: 1000 chars (250 tokens) with 200 char overlap.
    """

    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        legth_function=len,
        separators=["\n\n", "\n", " ", ""],
        is_separator_regex=False,
    )

async def _process_document_async(doc_id: str, tenant_id: str, gcs_path: str):
    """Async function that does the actual document processing"""
    doc_repo = DocumentRepository(session_factory=WorkerAsyncSessionLocal)
    chunk_repo = ChunkRepository(session_factory=WorkerAsyncSessionLocal)
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

    text_splitter = get_text_spliter(chunk_size=settings.CHUNK_SIZE, overlap=settings.CHUNK_OVERLAP)
    
    for page_data in extracted:
        raw_text = page_data["text"].strip()
        if not raw_text:
            continue
        text_chunks = text_splitter.split_text(raw_text)
        
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


async def _process_and_mark(doc_id: str, tenant_id: str, gcs_path: str) -> None:
    """Async wrapper that does the full document processing."""
    await _process_document_async(doc_id, tenant_id, gcs_path)


async def _mark_failed(doc_id: str, error_message: str) -> None:
    """Async helper to mark a document as failed."""
    doc_repo = DocumentRepository(session_factory=WorkerAsyncSessionLocal)
    await doc_repo.update_status(UUID(doc_id), "failed", error_message)


@celery_app.task(bind=True, max_retries=3)
def process_document(self, doc_id: str, tenant_id: str, gcs_path: str):
    """Celery entrypoint – runs async processing via asyncio.run."""
    try:
        asyncio.run(_process_and_mark(doc_id, tenant_id, gcs_path))
    except Exception as e:
        # Try to record failure in the DB; if that also fails, we still retry.
        try:
            asyncio.run(_mark_failed(doc_id, str(e)))
        finally:
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

