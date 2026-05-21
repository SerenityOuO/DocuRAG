from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import get_settings
from app.schemas.documents import (
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentUploadResponse,
    OcrResultResponse,
)
from app.services.document_storage import DocumentStorage
from app.services.ocr import MockOcrProvider


router = APIRouter(prefix="/documents", tags=["documents"])


def get_document_storage() -> DocumentStorage:
    settings = get_settings()
    return DocumentStorage(settings.data_dir)


def get_mock_ocr_provider() -> MockOcrProvider:
    return MockOcrProvider()


DocumentStorageDep = Annotated[DocumentStorage, Depends(get_document_storage)]
MockOcrProviderDep = Annotated[MockOcrProvider, Depends(get_mock_ocr_provider)]


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    storage: DocumentStorageDep,
    file: UploadFile = File(...),
) -> DocumentUploadResponse:
    document = await storage.save_upload(file)
    return DocumentUploadResponse.model_validate(document.model_dump())


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    storage: DocumentStorageDep,
) -> DocumentListResponse:
    return DocumentListResponse(documents=storage.list_documents())


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: str,
    storage: DocumentStorageDep,
) -> DocumentDetailResponse:
    document = storage.get_document(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentDetailResponse.model_validate(document.model_dump())


@router.post("/{document_id}/ocr/mock", response_model=OcrResultResponse)
async def run_mock_ocr(
    document_id: str,
    storage: DocumentStorageDep,
    provider: MockOcrProviderDep,
) -> OcrResultResponse:
    ocr_result = storage.run_ocr(document_id, provider)

    if ocr_result is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return OcrResultResponse(document_id=document_id, **ocr_result.model_dump())


@router.get("/{document_id}/ocr", response_model=OcrResultResponse)
async def get_ocr_result(
    document_id: str,
    storage: DocumentStorageDep,
) -> OcrResultResponse:
    ocr_result = storage.get_ocr_result(document_id)

    if ocr_result is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return OcrResultResponse(document_id=document_id, **ocr_result.model_dump())


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    storage: DocumentStorageDep,
) -> FileResponse:
    document = storage.get_document(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = storage.get_file_path(document)

    if file_path is None:
        raise HTTPException(status_code=404, detail="Document file not found")

    return FileResponse(
        file_path,
        media_type=document.content_type,
        filename=document.filename,
    )
