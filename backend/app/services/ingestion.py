from uuid import UUID
from fastapi import UploadFile

from app.config import settings
from app.db.repositories import DocumentRepository
from app.workers.tasks import process_document
from app.services.storage import StorageService


class IngestionService:
    def __init__(self):
        self.doc_repo = DocumentRepository()
    
    async def upload_document(
        self,
        tenant_id: UUID,
        file: UploadFile,
    ) -> dict:
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size:
            raise ValueError(f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit")
        
        # Upload to GCS using S3-compatible API
        gcs_path = f"{tenant_id}/docs/{file.filename}"
        
        StorageService.upload_file(
            bucket_name=settings.GCS_BUCKET_NAME,
            key=gcs_path,
            content=content,
            content_type=file.content_type
        )
        
        doc_id = await self.doc_repo.create_document(
            tenant_id=tenant_id,
            filename=file.filename,
            gcs_path=gcs_path,
            size_bytes=file_size,
        )

        try:
            process_document.delay(str(doc_id), str(tenant_id), gcs_path)
        except Exception as e:
            # If enqueueing to Celery fails, mark document as failed instead of leaving it pending
            await self.doc_repo.update_status(doc_id, "failed", f"Enqueue error: {e}")
            raise
        
        return {
            "doc_id": doc_id,
            "filename": file.filename,
            "status": "pending",
        }

