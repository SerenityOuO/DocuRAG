from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import default_data_dir  # noqa: E402
from app.repositories.document_metadata import (  # noqa: E402
    LocalJsonDocumentRepository,
    PostgresDocumentRepository,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import DocuRAG local JSON metadata into the PostgreSQL-backed repository."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=default_data_dir(),
        help="Local DocuRAG data directory containing documents.json and agent_runs.json.",
    )
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DOCURAG_DATABASE_URL") or os.environ.get("DATABASE_URL"),
        help="PostgreSQL connection URL. Defaults to DOCURAG_DATABASE_URL or DATABASE_URL.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read local JSON and print import counts without connecting to PostgreSQL.",
    )
    args = parser.parse_args()

    local_repository = LocalJsonDocumentRepository(args.data_dir)
    documents = local_repository.list_documents()
    agent_runs = local_repository.list_agent_runs()

    if args.dry_run:
        print(
            "Dry run: "
            f"documents={len(documents)}, "
            f"chunks={sum(len(document.chunks) for document in documents)}, "
            f"parser_results={sum(1 for document in documents if document.parser_result is not None)}, "
            f"agent_runs={len(agent_runs)}"
        )
        return 0

    if not args.database_url:
        print("DOCURAG_DATABASE_URL is required unless --dry-run is used.", file=sys.stderr)
        return 2

    postgres_repository = PostgresDocumentRepository(args.database_url)
    postgres_repository.ensure_schema()
    postgres_repository.write_documents(documents)
    postgres_repository.write_agent_runs(agent_runs)

    print(
        "Imported local JSON metadata to PostgreSQL-backed repository: "
        f"documents={len(documents)}, "
        f"chunks={sum(len(document.chunks) for document in documents)}, "
        f"parser_results={sum(1 for document in documents if document.parser_result is not None)}, "
        f"agent_runs={len(agent_runs)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
