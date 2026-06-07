from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
import base64
import hashlib
from typing import Any


SEED_CREATED_AT = datetime(2026, 6, 1, tzinfo=UTC)

AUTH_RBAC_SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        email TEXT NULL UNIQUE,
        display_name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        disabled BOOLEAN NOT NULL DEFAULT FALSE,
        auth_source TEXT NOT NULL DEFAULT 'local',
        created_at TIMESTAMPTZ NOT NULL,
        updated_at TIMESTAMPTZ NULL,
        payload JSONB NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_users_disabled ON users (disabled)",
    """
    CREATE TABLE IF NOT EXISTS organizations (
        organization_id TEXT PRIMARY KEY,
        slug TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        disabled BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMPTZ NOT NULL,
        updated_at TIMESTAMPTZ NULL,
        payload JSONB NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_organizations_disabled ON organizations (disabled)",
    """
    CREATE TABLE IF NOT EXISTS projects (
        project_id TEXT PRIMARY KEY,
        organization_id TEXT NOT NULL,
        slug TEXT NOT NULL,
        name TEXT NOT NULL,
        disabled BOOLEAN NOT NULL DEFAULT FALSE,
        created_by TEXT NULL,
        created_at TIMESTAMPTZ NOT NULL,
        updated_at TIMESTAMPTZ NULL,
        payload JSONB NOT NULL,
        UNIQUE (organization_id, slug)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_projects_organization_id ON projects (organization_id)",
    "CREATE INDEX IF NOT EXISTS idx_projects_disabled ON projects (disabled)",
    """
    CREATE TABLE IF NOT EXISTS roles (
        role_id TEXT PRIMARY KEY,
        role_name TEXT NOT NULL UNIQUE,
        description TEXT NOT NULL,
        permissions JSONB NOT NULL,
        created_at TIMESTAMPTZ NOT NULL,
        payload JSONB NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS memberships (
        membership_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        organization_id TEXT NOT NULL,
        role_id TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL,
        updated_at TIMESTAMPTZ NULL,
        payload JSONB NOT NULL,
        UNIQUE (user_id, organization_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_memberships_user_id ON memberships (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_memberships_organization_id ON memberships (organization_id)",
    """
    CREATE TABLE IF NOT EXISTS project_memberships (
        project_membership_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        organization_id TEXT NOT NULL,
        project_id TEXT NOT NULL,
        role_id TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL,
        updated_at TIMESTAMPTZ NULL,
        payload JSONB NOT NULL,
        UNIQUE (user_id, project_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_project_memberships_user_id ON project_memberships (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_project_memberships_project_id ON project_memberships (project_id)",
    "CREATE INDEX IF NOT EXISTS idx_project_memberships_status ON project_memberships (status)",
]

AUTH_RBAC_ROLES = [
    {
        "role_id": "role-viewer",
        "role_name": "viewer",
        "description": "Read-only access to project documents, RAG query and downloads.",
        "permissions": [
            "project:read",
            "document:read",
            "document:download",
            "rag:query",
        ],
    },
    {
        "role_id": "role-analyst",
        "role_name": "analyst",
        "description": "Project analyst access for ingestion, OCR, parser, indexing, eval and Agent runs.",
        "permissions": [
            "project:read",
            "document:read",
            "document:download",
            "document:upload",
            "document:process",
            "eval:run",
            "agent:run",
        ],
    },
    {
        "role_id": "role-admin",
        "role_name": "admin",
        "description": "Project admin access for analyst permissions plus membership and project management.",
        "permissions": [
            "project:read",
            "project:manage",
            "document:read",
            "document:download",
            "document:upload",
            "document:process",
            "eval:run",
            "agent:run",
            "membership:manage",
        ],
    },
]

AUTH_RBAC_DEMO_ORGANIZATION = {
    "organization_id": "org-demo",
    "slug": "demo-org",
    "name": "Demo Organization",
}

AUTH_RBAC_DEMO_PROJECT = {
    "project_id": "proj-demo",
    "organization_id": "org-demo",
    "slug": "demo-project",
    "name": "Demo Project",
    "created_by": "user-admin",
}

AUTH_RBAC_DEMO_SEED_USERS = [
    {
        "user_id": "user-admin",
        "username": "admin",
        "email": "admin@example.local",
        "display_name": "Demo Admin",
        "password": "demo-admin-pass",
        "role_name": "admin",
        "disabled": False,
    },
    {
        "user_id": "user-analyst",
        "username": "analyst",
        "email": "analyst@example.local",
        "display_name": "Demo Analyst",
        "password": "demo-analyst-pass",
        "role_name": "analyst",
        "disabled": False,
    },
    {
        "user_id": "user-viewer",
        "username": "viewer",
        "email": "viewer@example.local",
        "display_name": "Demo Viewer",
        "password": "demo-viewer-pass",
        "role_name": "viewer",
        "disabled": False,
    },
    {
        "user_id": "user-disabled",
        "username": "disabled-viewer",
        "email": "disabled-viewer@example.local",
        "display_name": "Disabled Demo Viewer",
        "password": "demo-disabled-pass",
        "role_name": "viewer",
        "disabled": True,
    },
]


@dataclass(frozen=True)
class AuthUserRecord:
    user_id: str
    username: str
    display_name: str
    password_hash: str
    disabled: bool
    email: str | None = None


@dataclass(frozen=True)
class ProjectMembershipRecord:
    project_membership_id: str
    user_id: str
    organization_id: str
    project_id: str
    role_name: str
    status: str


class PostgresAuthRbacRepository:
    name = "postgresql_auth_rbac"

    def __init__(
        self,
        database_url: str,
        connection_factory: Callable[[], Any] | None = None,
    ) -> None:
        if not database_url:
            raise ValueError("Auth RBAC schema migration requires DOCURAG_DATABASE_URL.")

        self.database_url = database_url
        self._connection_factory = connection_factory

    def ensure_schema(self) -> None:
        with self._connect() as connection:
            for statement in AUTH_RBAC_SCHEMA_STATEMENTS:
                connection.execute(statement)

    def seed_demo_foundation(self) -> dict[str, int]:
        self.ensure_schema()
        with self._connect() as connection:
            for role in AUTH_RBAC_ROLES:
                self._upsert_role(connection, role)
            self._upsert_organization(connection, AUTH_RBAC_DEMO_ORGANIZATION)
            self._upsert_project(connection, AUTH_RBAC_DEMO_PROJECT)
            for user in AUTH_RBAC_DEMO_SEED_USERS:
                self._upsert_user(connection, user)
                self._upsert_membership(connection, user)
                self._upsert_project_membership(connection, user)

        return {
            "roles": len(AUTH_RBAC_ROLES),
            "users": len(AUTH_RBAC_DEMO_SEED_USERS),
            "organizations": 1,
            "projects": 1,
            "memberships": len(AUTH_RBAC_DEMO_SEED_USERS),
            "project_memberships": len(AUTH_RBAC_DEMO_SEED_USERS),
        }

    def get_user_by_username(self, username: str) -> AuthUserRecord | None:
        self.ensure_schema()
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM users WHERE username = %s",
                (username,),
            ).fetchall()

        if not rows:
            return None

        payload = _row_payload(rows[0])
        return AuthUserRecord(
            user_id=str(payload["user_id"]),
            username=str(payload["username"]),
            display_name=str(payload["display_name"]),
            email=payload.get("email"),
            password_hash=str(payload["password_hash"]),
            disabled=bool(payload["disabled"]),
        )

    def list_project_memberships(self, user_id: str) -> list[ProjectMembershipRecord]:
        self.ensure_schema()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload
                FROM project_memberships
                WHERE user_id = %s
                ORDER BY project_id ASC
                """,
                (user_id,),
            ).fetchall()

        memberships: list[ProjectMembershipRecord] = []
        for row in rows:
            payload = _row_payload(row)
            memberships.append(
                ProjectMembershipRecord(
                    project_membership_id=str(payload["project_membership_id"]),
                    user_id=str(payload["user_id"]),
                    organization_id=str(payload["organization_id"]),
                    project_id=str(payload["project_id"]),
                    role_name=str(payload["role_name"]),
                    status=str(payload["status"]),
                )
            )

        return memberships

    def _upsert_role(self, connection: Any, role: dict[str, Any]) -> None:
        payload = {
            **role,
            "created_at": SEED_CREATED_AT.isoformat(),
        }
        connection.execute(
            """
            INSERT INTO roles (role_id, role_name, description, permissions, created_at, payload)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (role_id) DO UPDATE SET
                role_name = EXCLUDED.role_name,
                description = EXCLUDED.description,
                permissions = EXCLUDED.permissions,
                payload = EXCLUDED.payload
            """,
            (
                role["role_id"],
                role["role_name"],
                role["description"],
                _json_payload({"permissions": role["permissions"]}),
                SEED_CREATED_AT,
                _json_payload(payload),
            ),
        )

    def _upsert_organization(self, connection: Any, organization: dict[str, Any]) -> None:
        payload = {
            **organization,
            "disabled": False,
            "created_at": SEED_CREATED_AT.isoformat(),
            "updated_at": None,
        }
        connection.execute(
            """
            INSERT INTO organizations (
                organization_id, slug, name, disabled, created_at, updated_at, payload
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (organization_id) DO UPDATE SET
                slug = EXCLUDED.slug,
                name = EXCLUDED.name,
                disabled = EXCLUDED.disabled,
                updated_at = EXCLUDED.updated_at,
                payload = EXCLUDED.payload
            """,
            (
                organization["organization_id"],
                organization["slug"],
                organization["name"],
                False,
                SEED_CREATED_AT,
                None,
                _json_payload(payload),
            ),
        )

    def _upsert_project(self, connection: Any, project: dict[str, Any]) -> None:
        payload = {
            **project,
            "disabled": False,
            "created_at": SEED_CREATED_AT.isoformat(),
            "updated_at": None,
        }
        connection.execute(
            """
            INSERT INTO projects (
                project_id, organization_id, slug, name, disabled, created_by, created_at, updated_at, payload
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (project_id) DO UPDATE SET
                organization_id = EXCLUDED.organization_id,
                slug = EXCLUDED.slug,
                name = EXCLUDED.name,
                disabled = EXCLUDED.disabled,
                updated_at = EXCLUDED.updated_at,
                payload = EXCLUDED.payload
            """,
            (
                project["project_id"],
                project["organization_id"],
                project["slug"],
                project["name"],
                False,
                project["created_by"],
                SEED_CREATED_AT,
                None,
                _json_payload(payload),
            ),
        )

    def _upsert_user(self, connection: Any, user: dict[str, Any]) -> None:
        password_hash = seed_password_hash(str(user["password"]), str(user["user_id"]))
        payload = {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "display_name": user["display_name"],
            "password_hash": password_hash,
            "disabled": user["disabled"],
            "auth_source": "phase32_demo_seed",
            "created_at": SEED_CREATED_AT.isoformat(),
            "updated_at": None,
        }
        connection.execute(
            """
            INSERT INTO users (
                user_id, username, email, display_name, password_hash, disabled,
                auth_source, created_at, updated_at, payload
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                username = EXCLUDED.username,
                email = EXCLUDED.email,
                display_name = EXCLUDED.display_name,
                password_hash = EXCLUDED.password_hash,
                disabled = EXCLUDED.disabled,
                auth_source = EXCLUDED.auth_source,
                updated_at = EXCLUDED.updated_at,
                payload = EXCLUDED.payload
            """,
            (
                user["user_id"],
                user["username"],
                user["email"],
                user["display_name"],
                password_hash,
                user["disabled"],
                "phase32_demo_seed",
                SEED_CREATED_AT,
                None,
                _json_payload(payload),
            ),
        )

    def _upsert_membership(self, connection: Any, user: dict[str, Any]) -> None:
        role_id = f"role-{user['role_name']}"
        status = "disabled" if user["disabled"] else "active"
        membership_id = f"membership-{user['user_id']}-{AUTH_RBAC_DEMO_ORGANIZATION['organization_id']}"
        payload = {
            "membership_id": membership_id,
            "user_id": user["user_id"],
            "organization_id": AUTH_RBAC_DEMO_ORGANIZATION["organization_id"],
            "role_id": role_id,
            "role_name": user["role_name"],
            "status": status,
            "created_at": SEED_CREATED_AT.isoformat(),
            "updated_at": None,
        }
        connection.execute(
            """
            INSERT INTO memberships (
                membership_id, user_id, organization_id, role_id, status, created_at, updated_at, payload
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (membership_id) DO UPDATE SET
                role_id = EXCLUDED.role_id,
                status = EXCLUDED.status,
                updated_at = EXCLUDED.updated_at,
                payload = EXCLUDED.payload
            """,
            (
                membership_id,
                user["user_id"],
                AUTH_RBAC_DEMO_ORGANIZATION["organization_id"],
                role_id,
                status,
                SEED_CREATED_AT,
                None,
                _json_payload(payload),
            ),
        )

    def _upsert_project_membership(self, connection: Any, user: dict[str, Any]) -> None:
        role_id = f"role-{user['role_name']}"
        status = "disabled" if user["disabled"] else "active"
        project_membership_id = f"project-membership-{user['user_id']}-{AUTH_RBAC_DEMO_PROJECT['project_id']}"
        payload = {
            "project_membership_id": project_membership_id,
            "user_id": user["user_id"],
            "organization_id": AUTH_RBAC_DEMO_ORGANIZATION["organization_id"],
            "project_id": AUTH_RBAC_DEMO_PROJECT["project_id"],
            "role_id": role_id,
            "role_name": user["role_name"],
            "status": status,
            "created_at": SEED_CREATED_AT.isoformat(),
            "updated_at": None,
        }
        connection.execute(
            """
            INSERT INTO project_memberships (
                project_membership_id, user_id, organization_id, project_id, role_id,
                status, created_at, updated_at, payload
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (project_membership_id) DO UPDATE SET
                role_id = EXCLUDED.role_id,
                status = EXCLUDED.status,
                updated_at = EXCLUDED.updated_at,
                payload = EXCLUDED.payload
            """,
            (
                project_membership_id,
                user["user_id"],
                AUTH_RBAC_DEMO_ORGANIZATION["organization_id"],
                AUTH_RBAC_DEMO_PROJECT["project_id"],
                role_id,
                status,
                SEED_CREATED_AT,
                None,
                _json_payload(payload),
            ),
        )

    def _connect(self) -> Any:
        if self._connection_factory is not None:
            return self._connection_factory()

        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError(
                "Auth RBAC schema migration requires the optional postgres dependency. "
                'Install the backend with ".[postgres]" before running the Phase 32 migration.'
            ) from exc

        return psycopg.connect(self.database_url)


def seed_password_hash(password: str, salt: str) -> str:
    iterations = 120_000
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    encoded_digest = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return f"pbkdf2_sha256${iterations}${salt}${encoded_digest}"


def _json_payload(payload: dict[str, Any]) -> Any:
    try:
        from psycopg.types.json import Jsonb
    except ImportError:
        return payload

    return Jsonb(payload)


def _row_payload(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        payload = row.get("payload", row)
    else:
        payload = row[0]

    return getattr(payload, "obj", payload)
