"""Data access modules."""

from app.repositories.auth_rbac import PostgresAuthRbacRepository
from app.repositories.document_metadata import (
    LocalJsonDocumentRepository,
    PostgresDocumentRepository,
    create_document_repository,
    create_document_storage,
)

__all__ = [
    "LocalJsonDocumentRepository",
    "PostgresAuthRbacRepository",
    "PostgresDocumentRepository",
    "create_document_repository",
    "create_document_storage",
]
