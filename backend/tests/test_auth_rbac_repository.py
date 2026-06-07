from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import Any

from app.api.routes.auth import DEMO_USERS
from app.repositories.auth_rbac import (
    AUTH_RBAC_SCHEMA_STATEMENTS,
    PostgresAuthRbacRepository,
    seed_password_hash,
)


class FakeCursor:
    def __init__(self, rows: list[tuple[dict[str, Any]]]) -> None:
        self.rows = rows

    def fetchall(self) -> list[tuple[dict[str, Any]]]:
        return self.rows


class FakeAuthRbacConnection:
    def __init__(self) -> None:
        self.statements: list[str] = []
        self.tables: dict[str, dict[str, dict[str, Any]]] = {
            "users": {},
            "organizations": {},
            "projects": {},
            "roles": {},
            "memberships": {},
            "project_memberships": {},
        }

    def __enter__(self):
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def execute(self, sql: str, params: tuple[object, ...] | None = None) -> FakeCursor:
        normalized = " ".join(sql.casefold().split())
        self.statements.append(normalized)

        if normalized.startswith("create table") or normalized.startswith("create index"):
            return FakeCursor([])

        if normalized.startswith("insert into roles"):
            assert params is not None
            self.tables["roles"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if normalized.startswith("insert into organizations"):
            assert params is not None
            self.tables["organizations"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if normalized.startswith("insert into projects"):
            assert params is not None
            self.tables["projects"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if normalized.startswith("insert into users"):
            assert params is not None
            self.tables["users"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if normalized.startswith("insert into memberships"):
            assert params is not None
            self.tables["memberships"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if normalized.startswith("insert into project_memberships"):
            assert params is not None
            self.tables["project_memberships"][str(params[0])] = _payload(params[-1])
            return FakeCursor([])

        if "from users" in normalized and "where username" in normalized:
            assert params is not None
            username = str(params[0])
            rows = [
                (payload,)
                for payload in self.tables["users"].values()
                if payload["username"] == username
            ]
            return FakeCursor(rows)

        if "from project_memberships" in normalized and "where user_id" in normalized:
            assert params is not None
            user_id = str(params[0])
            rows = [
                (payload,)
                for payload in self.tables["project_memberships"].values()
                if payload["user_id"] == user_id
            ]
            return FakeCursor(rows)

        raise AssertionError(f"Unhandled SQL statement: {sql}")


def test_auth_rbac_schema_statements_are_non_destructive() -> None:
    combined_sql = "\n".join(AUTH_RBAC_SCHEMA_STATEMENTS).casefold()

    assert "drop table" not in combined_sql
    assert "delete from" not in combined_sql
    assert "create table if not exists users" in combined_sql
    assert "create table if not exists organizations" in combined_sql
    assert "create table if not exists projects" in combined_sql
    assert "create table if not exists roles" in combined_sql
    assert "create table if not exists memberships" in combined_sql
    assert "create table if not exists project_memberships" in combined_sql


def test_auth_rbac_repository_persists_demo_foundation() -> None:
    connection = FakeAuthRbacConnection()
    repository = PostgresAuthRbacRepository(
        "postgresql://docurag:docurag@localhost:5432/docurag",
        connection_factory=lambda: connection,
    )

    counts = repository.seed_demo_foundation()
    admin = repository.get_user_by_username("admin")
    disabled_user = repository.get_user_by_username("disabled-viewer")
    admin_project_memberships = repository.list_project_memberships("user-admin")
    disabled_project_memberships = repository.list_project_memberships("user-disabled")

    assert counts == {
        "roles": 3,
        "users": 4,
        "organizations": 1,
        "projects": 1,
        "memberships": 4,
        "project_memberships": 4,
    }
    assert admin is not None
    assert admin.display_name == "Demo Admin"
    assert admin.password_hash.startswith("pbkdf2_sha256$120000$user-admin$")
    assert "demo-admin-pass" not in admin.password_hash
    assert disabled_user is not None
    assert disabled_user.disabled is True
    assert admin_project_memberships[0].role_name == "admin"
    assert admin_project_memberships[0].status == "active"
    assert disabled_project_memberships[0].role_name == "viewer"
    assert disabled_project_memberships[0].status == "disabled"
    assert connection.tables["projects"]["proj-demo"]["organization_id"] == "org-demo"
    assert not any("drop table" in statement or "delete from" in statement for statement in connection.statements)


def test_seed_password_hash_is_deterministic_and_not_plaintext() -> None:
    first_hash = seed_password_hash("demo-admin-pass", "user-admin")
    second_hash = seed_password_hash("demo-admin-pass", "user-admin")

    assert first_hash == second_hash
    assert first_hash.startswith("pbkdf2_sha256$120000$user-admin$")
    assert "demo-admin-pass" not in first_hash


def test_auth_rbac_migration_command_dry_run() -> None:
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "migrate-auth-rbac-schema.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--dry-run",
            "--seed-demo-users",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "schema_statements=" in result.stdout
    assert "roles=3" in result.stdout
    assert "demo_users=4" in result.stdout
    assert "seed_demo_users=true" in result.stdout


def test_phase28_demo_auth_fallback_is_not_replaced() -> None:
    assert DEMO_USERS["admin"]["password"] == "demo-admin-pass"
    assert DEMO_USERS["analyst"]["role"] == "analyst"
    assert DEMO_USERS["viewer"]["role"] == "viewer"


def _payload(value: object) -> dict[str, Any]:
    payload = getattr(value, "obj", value)
    assert isinstance(payload, dict)
    return payload
