from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import get_settings
from app.schemas.documents import (
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentUploadResponse,
    OcrStatus,
    OcrResultResponse,
)
from app.services.document_storage import DocumentStorage
from app.services.ocr import MockOcrProvider, OcrProvider, PaddleOcrProvider


router = APIRouter(prefix="/documents", tags=["documents"])


def get_document_storage() -> DocumentStorage:
    settings = get_settings()
    return DocumentStorage(settings.data_dir)


def get_mock_ocr_provider() -> MockOcrProvider:
    return MockOcrProvider()


def get_selected_ocr_provider() -> OcrProvider:
    settings = get_settings()
    provider_name = settings.ocr_provider.strip().lower()

    if provider_name == "mock":
        return MockOcrProvider()

    if provider_name in {"paddleocr", "paddle"}:
        return PaddleOcrProvider()

    raise HTTPException(
        status_code=500,
        detail=f"Unsupported OCR provider configured: {settings.ocr_provider}",
    )


DocumentStorageDep = Annotated[DocumentStorage, Depends(get_document_storage)]
MockOcrProviderDep = Annotated[MockOcrProvider, Depends(get_mock_ocr_provider)]
SelectedOcrProviderDep = Annotated[OcrProvider, Depends(get_selected_ocr_provider)]


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


@router.post("/{document_id}/ocr", response_model=OcrResultResponse)
async def run_selected_ocr(
    document_id: str,
    storage: DocumentStorageDep,
    provider: SelectedOcrProviderDep,
) -> OcrResultResponse:
    ocr_result = storage.run_ocr(document_id, provider)

    if ocr_result is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if ocr_result.status == OcrStatus.FAILED and provider.job_type.value == "ocr_real":
        raise HTTPException(
            status_code=503,
            detail={
                "provider": getattr(provider, "provider_name", "ocr_real"),
                "error_code": ocr_result.extracted_fields.get("error_code", "ocr_provider_failed"),
                "error": ocr_result.extracted_fields.get("error", "OCR provider failed"),
                "document_id": document_id,
            },
        )

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
