import json
import socket
from typing import Any
import urllib.error
import urllib.request

import pytest

from app.services.vector_store import QdrantPoint, QdrantVectorStore, QdrantVectorStoreError


class FakeResponse:
    def __init__(self, payload: dict[str, Any] | None = None) -> None:
        self.payload = payload
        self.closed = False

    def read(self) -> bytes:
        if self.payload is None:
            return b""
        return json.dumps(self.payload).encode("utf-8")

    def close(self) -> None:
        self.closed = True


def collection_payload(size: int = 1024, distance: str = "Cosine") -> dict[str, Any]:
    return {
        "result": {
            "config": {
                "params": {
                    "vectors": {
                        "size": size,
                        "distance": distance,
                    }
                }
            }
        }
    }


def test_qdrant_ensure_collection_returns_existing_collection() -> None:
    captured: dict[str, Any] = {}

    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        captured["url"] = request.full_url
        captured["method"] = request.get_method()
        captured["timeout"] = timeout
        return FakeResponse(collection_payload())

    store = QdrantVectorStore(
        base_url="http://127.0.0.1:6333/",
        collection_name="docurag_chunks_v1",
        vector_size=1024,
        timeout_seconds=5,
        transport=transport,
    )

    status = store.ensure_collection()

    assert captured == {
        "url": "http://127.0.0.1:6333/collections/docurag_chunks_v1",
        "method": "GET",
        "timeout": 5,
    }
    assert status.exists is True
    assert status.collection_name == "docurag_chunks_v1"
    assert status.vector_size == 1024
    assert status.distance == "Cosine"


def test_qdrant_ensure_collection_creates_missing_collection() -> None:
    requests: list[dict[str, Any]] = []

    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        requests.append(
            {
                "url": request.full_url,
                "method": request.get_method(),
                "body": json.loads(request.data.decode("utf-8")) if request.data else None,
            }
        )
        if request.get_method() == "GET":
            raise urllib.error.HTTPError(
                url=request.full_url,
                code=404,
                msg="not found",
                hdrs=None,
                fp=FakeResponse({"status": "not found"}),
            )
        return FakeResponse({"result": True})

    store = QdrantVectorStore(
        base_url="http://127.0.0.1:6333",
        collection_name="docurag_chunks_v1",
        vector_size=1024,
        transport=transport,
    )

    status = store.ensure_collection()

    assert requests == [
        {
            "url": "http://127.0.0.1:6333/collections/docurag_chunks_v1",
            "method": "GET",
            "body": None,
        },
        {
            "url": "http://127.0.0.1:6333/collections/docurag_chunks_v1",
            "method": "PUT",
            "body": {"vectors": {"size": 1024, "distance": "Cosine"}},
        },
    ]
    assert status.exists is True
    assert status.vector_size == 1024
    assert status.distance == "Cosine"
    assert "created" in status.message


def test_qdrant_ensure_collection_rejects_vector_size_mismatch() -> None:
    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        return FakeResponse(collection_payload(size=768))

    store = QdrantVectorStore(
        base_url="http://127.0.0.1:6333",
        collection_name="docurag_chunks_v1",
        vector_size=1024,
        transport=transport,
    )

    with pytest.raises(QdrantVectorStoreError, match="expected 1024"):
        store.ensure_collection()


def test_qdrant_ensure_collection_reports_connection_error() -> None:
    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        raise urllib.error.URLError(ConnectionRefusedError("connection refused"))

    store = QdrantVectorStore(
        base_url="http://127.0.0.1:6333",
        collection_name="docurag_chunks_v1",
        vector_size=1024,
        transport=transport,
    )

    with pytest.raises(QdrantVectorStoreError, match="Cannot connect to Qdrant"):
        store.ensure_collection()


def test_qdrant_ensure_collection_reports_timeout() -> None:
    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        raise socket.timeout("timed out")

    store = QdrantVectorStore(
        base_url="http://127.0.0.1:6333",
        collection_name="docurag_chunks_v1",
        vector_size=1024,
        timeout_seconds=1,
        transport=transport,
    )

    with pytest.raises(QdrantVectorStoreError, match="timed out after 1.0s"):
        store.ensure_collection()


def test_qdrant_ensure_collection_reports_malformed_response() -> None:
    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        return FakeResponse({"result": {"config": {"params": {"vectors": {"distance": "Cosine"}}}}})

    store = QdrantVectorStore(
        base_url="http://127.0.0.1:6333",
        collection_name="docurag_chunks_v1",
        vector_size=1024,
        transport=transport,
    )

    with pytest.raises(QdrantVectorStoreError, match="malformed vector params"):
        store.ensure_collection()


def test_qdrant_upsert_points_sends_points_payload() -> None:
    captured: dict[str, Any] = {}

    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        captured["url"] = request.full_url
        captured["method"] = request.get_method()
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse({"result": {"operation_id": 1}, "status": "ok"})

    store = QdrantVectorStore(
        base_url="http://127.0.0.1:6333",
        collection_name="docurag_chunks_v1",
        vector_size=1024,
        transport=transport,
    )

    store.upsert_points(
        [
            QdrantPoint(
                point_id="point-001",
                vector=[0.1, 0.2],
                payload={"chunk_id": "chunk-001"},
            )
        ]
    )

    assert captured == {
        "url": "http://127.0.0.1:6333/collections/docurag_chunks_v1/points?wait=true",
        "method": "PUT",
        "body": {
            "points": [
                {
                    "id": "point-001",
                    "vector": [0.1, 0.2],
                    "payload": {"chunk_id": "chunk-001"},
                }
            ]
        },
    }


def test_qdrant_search_sends_vector_query_and_parses_results() -> None:
    captured: dict[str, Any] = {}

    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        captured["url"] = request.full_url
        captured["method"] = request.get_method()
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse(
            {
                "result": [
                    {
                        "id": "point-001",
                        "score": 0.91,
                        "payload": {"chunk_id": "chunk-001"},
                    }
                ]
            }
        )

    store = QdrantVectorStore(
        base_url="http://127.0.0.1:6333",
        collection_name="docurag_chunks_v1",
        vector_size=1024,
        transport=transport,
    )

    results = store.search([0.1, 0.2], 3)

    assert captured == {
        "url": "http://127.0.0.1:6333/collections/docurag_chunks_v1/points/search",
        "method": "POST",
        "body": {
            "vector": [0.1, 0.2],
            "limit": 3,
            "with_payload": True,
        },
    }
    assert len(results) == 1
    assert results[0].point_id == "point-001"
    assert results[0].score == 0.91
    assert results[0].payload == {"chunk_id": "chunk-001"}


def test_qdrant_search_can_filter_to_document_ids() -> None:
    captured: dict[str, Any] = {}

    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse({"result": []})

    store = QdrantVectorStore(
        base_url="http://127.0.0.1:6333",
        collection_name="docurag_chunks_v1",
        vector_size=1024,
        transport=transport,
    )

    results = store.search([0.1, 0.2], 3, ["doc-001", "doc-002"])

    assert results == []
    assert captured["body"] == {
        "vector": [0.1, 0.2],
        "limit": 3,
        "with_payload": True,
        "filter": {
            "should": [
                {"key": "document_id", "match": {"value": "doc-001"}},
                {"key": "document_id", "match": {"value": "doc-002"}},
            ]
        },
    }


def test_qdrant_search_reports_malformed_results() -> None:
    def transport(request: urllib.request.Request, timeout: float) -> FakeResponse:
        return FakeResponse({"result": [{"id": "point-001"}]})

    store = QdrantVectorStore(
        base_url="http://127.0.0.1:6333",
        collection_name="docurag_chunks_v1",
        vector_size=1024,
        transport=transport,
    )

    with pytest.raises(QdrantVectorStoreError, match="malformed point fields"):
        store.search([0.1, 0.2], 3)
