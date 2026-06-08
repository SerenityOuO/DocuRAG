from __future__ import annotations

from datetime import UTC, datetime
import json
import logging
from typing import Any

from app.core.config import Settings


OBSERVABILITY_SCHEMA_VERSION = "docurag_observability_v1"
REQUIRED_OBSERVABILITY_FIELDS = (
    "trace_id",
    "request_id",
    "organization_id",
    "project_id",
    "actor_user_id",
    "document_id",
    "strategy",
    "provider",
    "latency_ms",
    "status",
    "error_code",
)

logger = logging.getLogger(__name__)


def build_observability_event(
    settings: Settings,
    event_type: str,
    event_name: str,
    **fields: Any,
) -> dict[str, Any]:
    event = {
        "schema_version": OBSERVABILITY_SCHEMA_VERSION,
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "service_name": "docurag-backend",
        "environment": settings.environment,
        "version": settings.version,
        "event_type": event_type,
        "event_name": event_name,
    }
    for field_name in REQUIRED_OBSERVABILITY_FIELDS:
        event[field_name] = fields.pop(field_name, None)
    event.update(fields)
    return event


def emit_observability_event(
    settings: Settings,
    event_type: str,
    event_name: str,
    **fields: Any,
) -> dict[str, Any] | None:
    if settings.observability_log_path is None:
        return None

    event = build_observability_event(settings, event_type, event_name, **fields)
    try:
        settings.observability_log_path.parent.mkdir(parents=True, exist_ok=True)
        with settings.observability_log_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, ensure_ascii=False, sort_keys=True, default=str))
            file.write("\n")
    except OSError as exc:
        logger.warning("Observability JSONL emit failed: %s", exc)
        return None

    return event
