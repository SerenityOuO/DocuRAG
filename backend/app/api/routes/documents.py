import logging
from dataclasses import asdict
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
    ParserResult,
    ParserStatus,
    VectorIndexingResponse,
)
from app.services.document_parser import DeterministicInvoiceParser, VlmInvoiceParser, create_vlm_provider
from app.services.document_storage import DocumentStorage
from app.services.embedding import create_embedding_provider
from app.services.ocr import MockOcrProvider, OcrProvider, PaddleOcrProvider
from app.services.vector_indexing import VectorIndexingService
from app.services.vector_store import create_qdrant_vector_store
from app.services.vlm_input import VlmInputResolver


router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)
_selected_ocr_provider: OcrProvider | None = None
_selected_ocr_provider_cache_key: tuple[object, ...] | None = None


def get_document_storage() -> DocumentStorage:
    settings = get_settings()
    return DocumentStorage(settings.data_dir)


def get_mock_ocr_provider() -> MockOcrProvider:
    return MockOcrProvider()


def get_vector_indexing_service() -> VectorIndexingService:
    settings = get_settings()
    return VectorIndexingService(
        embedding_provider=create_embedding_provider(settings),
        vector_store=create_qdrant_vector_store(settings),
    )


def get_document_parser():
    settings = get_settings()
    parser_source = settings.parser_source.strip().lower()
    if parser_source == "deterministic_invoice":
        return DeterministicInvoiceParser()

    return VlmInvoiceParser(
        input_resolver=VlmInputResolver(settings.data_dir / "uploads"),
        provider=create_vlm_provider(
            settings.vlm_provider,
            settings.vlm_base_url,
            settings.vlm_model,
            settings.vlm_timeout_seconds,
        ),
        min_confidence=settings.vlm_min_confidence,
    )


def _selected_ocr_provider_key() -> tuple[object, ...]:
    settings = get_settings()
    return (
        settings.ocr_provider.strip().lower(),
        settings.ocr_language,
        settings.ocr_version,
        settings.ocr_det_model_name,
        settings.ocr_rec_model_name,
        settings.ocr_cls_model_name,
        settings.ocr_det_model_dir,
        settings.ocr_rec_model_dir,
        settings.ocr_cls_model_dir,
        settings.ocr_use_angle_cls,
        settings.ocr_det_limit_side_len,
        settings.ocr_rec_batch_num,
    )


def _build_selected_ocr_provider() -> OcrProvider:
    settings = get_settings()
    provider_name = settings.ocr_provider.strip().lower()

    if provider_name == "mock":
        return MockOcrProvider()

    if provider_name in {"paddleocr", "paddle"}:
        return PaddleOcrProvider(
            language=settings.ocr_language,
            ocr_version=settings.ocr_version,
            det_model_name=settings.ocr_det_model_name,
            rec_model_name=settings.ocr_rec_model_name,
            cls_model_name=settings.ocr_cls_model_name,
            det_model_dir=settings.ocr_det_model_dir,
            rec_model_dir=settings.ocr_rec_model_dir,
            cls_model_dir=settings.ocr_cls_model_dir,
            use_angle_cls=settings.ocr_use_angle_cls,
            det_limit_side_len=settings.ocr_det_limit_side_len,
            rec_batch_num=settings.ocr_rec_batch_num,
        )

    raise HTTPException(
        status_code=500,
        detail=f"Unsupported OCR provider configured: {settings.ocr_provider}",
    )


def get_selected_ocr_provider() -> OcrProvider:
    global _selected_ocr_provider, _selected_ocr_provider_cache_key

    cache_key = _selected_ocr_provider_key()
    if _selected_ocr_provider is not None and _selected_ocr_provider_cache_key == cache_key:
        return _selected_ocr_provider

    _selected_ocr_provider = _build_selected_ocr_provider()
    _selected_ocr_provider_cache_key = cache_key

    return _selected_ocr_provider


def preload_selected_ocr_provider() -> None:
    settings = get_settings()
    provider_name = settings.ocr_provider.strip().lower()
    provider = get_selected_ocr_provider()

    if provider_name in {"paddleocr", "paddle"} and isinstance(provider, PaddleOcrProvider):
        try:
            provider.preload()
        except Exception:
            logger.exception("PaddleOCR provider preload failed during backend startup.")
            raise

        logger.info(
            "PaddleOCR provider preloaded during backend startup: language=%s ocr_version=%s det_model=%s rec_model=%s cls_model=%s use_angle_cls=%s det_limit_side_len=%s rec_batch_num=%s",
            provider.language,
            provider.ocr_version,
            provider.det_model_name,
            provider.rec_model_name,
            provider.cls_model_name,
            provider.use_angle_cls,
            provider.det_limit_side_len,
            provider.rec_batch_num,
        )
        return

    logger.info("Selected OCR provider does not require startup preload: provider=%s", provider_name)


def _reset_selected_ocr_provider_cache() -> None:
    global _selected_ocr_provider, _selected_ocr_provider_cache_key

    _selected_ocr_provider = None
    _selected_ocr_provider_cache_key = None


DocumentStorageDep = Annotated[DocumentStorage, Depends(get_document_storage)]
MockOcrProviderDep = Annotated[MockOcrProvider, Depends(get_mock_ocr_provider)]
SelectedOcrProviderDep = Annotated[OcrProvider, Depends(get_selected_ocr_provider)]
VectorIndexingServiceDep = Annotated[VectorIndexingService, Depends(get_vector_indexing_service)]
DocumentParserDep = Annotated[object, Depends(get_document_parser)]


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


@router.post("/{document_id}/parse", response_model=ParserResult)
async def parse_document_fields(
    document_id: str,
    storage: DocumentStorageDep,
    parser: DocumentParserDep,
) -> ParserResult:
    parser_result = storage.run_parser(document_id, parser)

    if parser_result is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if parser_result.status == ParserStatus.FAILED:
        raise HTTPException(status_code=409, detail=parser_result.model_dump(mode="json"))

    return parser_result


@router.get("/{document_id}/fields", response_model=ParserResult)
async def get_document_fields(
    document_id: str,
    storage: DocumentStorageDep,
) -> ParserResult:
    parser_result = storage.get_parser_result(document_id)

    if parser_result is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return parser_result


@router.post("/{document_id}/index/vector", response_model=VectorIndexingResponse)
async def index_document_vector(
    document_id: str,
    storage: DocumentStorageDep,
    service: VectorIndexingServiceDep,
) -> VectorIndexingResponse:
    document = storage.get_document(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.ocr.status != OcrStatus.COMPLETED:
        raise HTTPException(
            status_code=409,
            detail={
                "document_id": document_id,
                "status": "failed",
                "error": "Document OCR must be completed before vector indexing.",
            },
        )

    result = VectorIndexingResponse(**asdict(service.index_document(document)))
    if result.status == "failed":
        raise HTTPException(status_code=503, detail=result.model_dump())

    return result


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
