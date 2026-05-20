from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile

from app.schemas.documents import DocumentStatus, DocumentUploadResponse


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    content = await file.read()
    filename = file.filename or "uploaded-file"

    return DocumentUploadResponse(
        document_id=str(uuid4()),
        project_id=None,
        filename=filename,
        file_type=Path(filename).suffix.lstrip(".").lower() or "unknown",
        content_type=file.content_type or "application/octet-stream",
        size=len(content),
        status=DocumentStatus.UPLOADED,
        created_at=datetime.now(UTC),
    )
