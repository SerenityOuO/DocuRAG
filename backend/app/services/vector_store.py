from __future__ import annotations

from dataclasses import dataclass, field
import json
import socket
from typing import Any, Callable
import urllib.error
import urllib.request

from app.core.config import Settings


Transport = Callable[[urllib.request.Request, float], Any]


@dataclass(frozen=True)
class QdrantCollectionStatus:
    collection_name: str
    exists: bool
    vector_size: int | None = None
    distance: str | None = None
    message: str = ""


@dataclass(frozen=True)
class QdrantPoint:
    point_id: str
    vector: list[float]
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class QdrantSearchResult:
    point_id: str
    score: float
    payload: dict[str, Any] = field(default_factory=dict)


class QdrantVectorStoreError(RuntimeError):
    pass


class QdrantVectorStore:
    PAYLOAD_INDEX_SCHEMAS = {
        "tenant_id": "keyword",
        "project_id": "keyword",
        "document_id": "keyword",
        "source_type": "keyword",
        "content_source": "keyword",
        "chunk_type": "keyword",
        "page_number": "integer",
    }

    def __init__(
        self,
        base_url: str,
        collection_name: str,
        vector_size: int,
        timeout_seconds: float = 10.0,
        transport: Transport | None = None,
    ) -> None:
        if vector_size <= 0:
            raise ValueError("vector_size must be greater than zero")

        self.base_url = base_url.rstrip("/")
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.timeout_seconds = timeout_seconds
        self._transport = transport or (lambda request, timeout: urllib.request.urlopen(request, timeout=timeout))

    def ensure_collection(self) -> QdrantCollectionStatus:
        status = self.get_collection()
        if not status.exists:
            return self.create_collection()

        if status.vector_size != self.vector_size:
            raise QdrantVectorStoreError(
                f"Qdrant collection '{self.collection_name}' vector size is {status.vector_size}; expected {self.vector_size}."
            )

        return status

    def get_collection(self) -> QdrantCollectionStatus:
        try:
            data = self._request_json("GET", f"/collections/{self.collection_name}")
        except QdrantVectorStoreError as exc:
            if "HTTP 404" in str(exc):
                return QdrantCollectionStatus(
                    collection_name=self.collection_name,
                    exists=False,
                    message=f"Qdrant collection '{self.collection_name}' does not exist.",
                )
            raise

        vector_size, distance = self._parse_collection_vectors(data)
        return QdrantCollectionStatus(
            collection_name=self.collection_name,
            exists=True,
            vector_size=vector_size,
            distance=distance,
            message=f"Qdrant collection '{self.collection_name}' exists.",
        )

    def create_collection(self) -> QdrantCollectionStatus:
        self._request_json(
            "PUT",
            f"/collections/{self.collection_name}",
            {
                "vectors": {
                    "size": self.vector_size,
                    "distance": "Cosine",
                }
            },
        )
        return QdrantCollectionStatus(
            collection_name=self.collection_name,
            exists=True,
            vector_size=self.vector_size,
            distance="Cosine",
            message=f"Qdrant collection '{self.collection_name}' was created.",
        )

    def upsert_points(self, points: list[QdrantPoint]) -> None:
        if not points:
            return

        payload = {
            "points": [
                {
                    "id": point.point_id,
                    "vector": point.vector,
                    "payload": point.payload,
                }
                for point in points
            ]
        }
        self._request_json("PUT", f"/collections/{self.collection_name}/points?wait=true", payload)

    def ensure_payload_indexes(self, fields: list[str] | None = None) -> list[str]:
        index_fields = fields or list(self.PAYLOAD_INDEX_SCHEMAS)
        ensured_fields: list[str] = []

        for field_name in index_fields:
            field_schema = self.PAYLOAD_INDEX_SCHEMAS.get(field_name, "keyword")
            try:
                self._request_json(
                    "PUT",
                    f"/collections/{self.collection_name}/index?wait=true",
                    {
                        "field_name": field_name,
                        "field_schema": field_schema,
                    },
                )
            except QdrantVectorStoreError as exc:
                message = str(exc).lower()
                if "http 409" not in message and "already exists" not in message:
                    raise

            ensured_fields.append(field_name)

        return ensured_fields

    def delete_points_by_filter(self, filter_payload: dict[str, Any]) -> None:
        if not filter_payload:
            raise ValueError("filter_payload must not be empty")

        self._request_json(
            "POST",
            f"/collections/{self.collection_name}/points/delete?wait=true",
            {"filter": filter_payload},
        )

    def cleanup_stale_points(
        self,
        document_id: str,
        active_point_ids: list[str],
        project_id: str | None = None,
        tenant_id: str | None = None,
    ) -> None:
        if not document_id:
            raise ValueError("document_id must not be empty")
        if not active_point_ids:
            return

        conditions = [self._match_filter("document_id", [document_id])]
        if project_id:
            conditions.append(self._match_filter("project_id", [project_id]))
        if tenant_id:
            conditions.append(self._match_filter("tenant_id", [tenant_id]))

        self.delete_points_by_filter(
            {
                "must": conditions,
                "must_not": [
                    {
                        "has_id": active_point_ids,
                    }
                ],
            }
        )

    def search(
        self,
        vector: list[float],
        limit: int,
        document_ids: list[str] | None = None,
        project_ids: list[str] | None = None,
        tenant_id: str | None = None,
        source_types: list[str] | None = None,
    ) -> list[QdrantSearchResult]:
        if not vector:
            raise ValueError("vector must not be empty")
        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        payload: dict[str, Any] = {
            "vector": vector,
            "limit": limit,
            "with_payload": True,
        }
        filter_conditions = []
        if document_ids:
            filter_conditions.append(self._match_filter("document_id", document_ids))
        if project_ids:
            filter_conditions.append(self._match_filter("project_id", project_ids))
        if tenant_id:
            filter_conditions.append(self._match_filter("tenant_id", [tenant_id]))
        if source_types:
            filter_conditions.append(self._match_filter("source_type", source_types))
        if filter_conditions:
            payload["filter"] = {"must": filter_conditions}

        data = self._request_json(
            "POST",
            f"/collections/{self.collection_name}/points/search",
            payload,
        )
        results = data.get("result")
        if not isinstance(results, list):
            raise QdrantVectorStoreError("Qdrant search response did not include a result list.")

        parsed_results = []
        for item in results:
            if not isinstance(item, dict):
                raise QdrantVectorStoreError("Qdrant search response included a malformed result item.")

            point_id = item.get("id")
            score = item.get("score")
            payload = item.get("payload")
            if point_id is None or not isinstance(score, (int, float)) or not isinstance(payload, dict):
                raise QdrantVectorStoreError("Qdrant search response included malformed point fields.")

            parsed_results.append(
                QdrantSearchResult(
                    point_id=str(point_id),
                    score=float(score),
                    payload=payload,
                )
            )

        return parsed_results

    def _match_filter(self, key: str, values: list[str]) -> dict[str, Any]:
        clean_values = [str(value) for value in values if str(value)]
        if not clean_values:
            raise ValueError(f"{key} filter values must not be empty")

        if len(clean_values) == 1:
            return {"key": key, "match": {"value": clean_values[0]}}

        return {"key": key, "match": {"any": clean_values}}

    def _request_json(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

        try:
            response = self._transport(request, self.timeout_seconds)
            try:
                response_body = response.read()
            finally:
                response.close()
        except urllib.error.HTTPError as exc:
            message = self._read_http_error(exc)
            raise QdrantVectorStoreError(f"Qdrant request failed with HTTP {exc.code}: {message}") from exc
        except (TimeoutError, socket.timeout) as exc:
            raise QdrantVectorStoreError(
                f"Qdrant request timed out after {self.timeout_seconds:.1f}s at {self.base_url}."
            ) from exc
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, (TimeoutError, socket.timeout)):
                raise QdrantVectorStoreError(
                    f"Qdrant request timed out after {self.timeout_seconds:.1f}s at {self.base_url}."
                ) from exc
            raise QdrantVectorStoreError(f"Cannot connect to Qdrant at {self.base_url}.") from exc

        if not response_body:
            return {}

        try:
            data = json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise QdrantVectorStoreError("Qdrant returned a non-JSON response.") from exc

        if not isinstance(data, dict):
            raise QdrantVectorStoreError("Qdrant returned an unexpected JSON response shape.")

        return data

    def _parse_collection_vectors(self, data: dict[str, Any]) -> tuple[int, str]:
        result = data.get("result")
        config = result.get("config") if isinstance(result, dict) else None
        params = config.get("params") if isinstance(config, dict) else None
        vectors = params.get("vectors") if isinstance(params, dict) else None

        if not isinstance(vectors, dict):
            raise QdrantVectorStoreError("Qdrant collection response did not include vector params.")

        size = vectors.get("size")
        distance = vectors.get("distance")
        if not isinstance(size, int) or not isinstance(distance, str):
            raise QdrantVectorStoreError("Qdrant collection response included malformed vector params.")

        return size, distance

    def _read_http_error(self, exc: urllib.error.HTTPError) -> str:
        try:
            error_body = exc.read().decode("utf-8")
        except Exception:
            return exc.reason or "unknown error"

        try:
            data = json.loads(error_body)
        except json.JSONDecodeError:
            return error_body or "unknown error"

        if isinstance(data, dict):
            message = data.get("status") or data.get("error") or data.get("message")
            if message:
                return str(message)

        return error_body or "unknown error"


def create_qdrant_vector_store(settings: Settings) -> QdrantVectorStore:
    return QdrantVectorStore(
        base_url=settings.qdrant_url,
        collection_name=settings.qdrant_collection,
        vector_size=settings.qdrant_vector_size,
        timeout_seconds=settings.qdrant_timeout_seconds,
    )
