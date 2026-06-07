from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.repositories.auth_rbac import (  # noqa: E402
    AUTH_RBAC_DEMO_SEED_USERS,
    AUTH_RBAC_ROLES,
    AUTH_RBAC_SCHEMA_STATEMENTS,
    PostgresAuthRbacRepository,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create the Phase 32 formal Auth / RBAC PostgreSQL schema."
    )
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DOCURAG_DATABASE_URL") or os.environ.get("DATABASE_URL"),
        help="PostgreSQL connection URL. Defaults to DOCURAG_DATABASE_URL or DATABASE_URL.",
    )
    parser.add_argument(
        "--seed-demo-users",
        action="store_true",
        help="Upsert local demo users, roles, demo organization and demo project membership rows.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the migration plan without connecting to PostgreSQL.",
    )
    args = parser.parse_args()

    if args.dry_run:
        print(
            "Dry run: "
            f"schema_statements={len(AUTH_RBAC_SCHEMA_STATEMENTS)}, "
            f"roles={len(AUTH_RBAC_ROLES)}, "
            f"demo_users={len(AUTH_RBAC_DEMO_SEED_USERS)}, "
            f"seed_demo_users={str(args.seed_demo_users).lower()}"
        )
        return 0

    if not args.database_url:
        print("DOCURAG_DATABASE_URL is required unless --dry-run is used.", file=sys.stderr)
        return 2

    repository = PostgresAuthRbacRepository(args.database_url)
    repository.ensure_schema()
    seed_counts = repository.seed_demo_foundation() if args.seed_demo_users else None

    if seed_counts is None:
        print(
            "Created Phase 32 Auth / RBAC PostgreSQL schema: "
            f"schema_statements={len(AUTH_RBAC_SCHEMA_STATEMENTS)}"
        )
    else:
        print(
            "Created Phase 32 Auth / RBAC PostgreSQL schema and demo foundation: "
            f"roles={seed_counts['roles']}, "
            f"users={seed_counts['users']}, "
            f"organizations={seed_counts['organizations']}, "
            f"projects={seed_counts['projects']}, "
            f"memberships={seed_counts['memberships']}, "
            f"project_memberships={seed_counts['project_memberships']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
