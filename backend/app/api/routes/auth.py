from typing import Annotated
import base64
from dataclasses import dataclass
import hashlib
import hmac
import json

from fastapi import APIRouter, Depends, Header, HTTPException

from app.core.config import get_settings
from app.schemas.auth import AuthRole, AuthUser, LoginRequest, LoginResponse, LogoutResponse, MeResponse


router = APIRouter(prefix="/auth", tags=["auth"])

DEMO_USERS = {
    "admin": {
        "password": "demo-admin-pass",
        "display_name": "Demo Admin",
        "role": "admin",
    },
    "analyst": {
        "password": "demo-analyst-pass",
        "display_name": "Demo Analyst",
        "role": "analyst",
    },
    "viewer": {
        "password": "demo-viewer-pass",
        "display_name": "Demo Viewer",
        "role": "viewer",
    },
}

AUTH_ROLES = {"admin", "analyst", "viewer"}


@dataclass(frozen=True)
class RequestAuthContext:
    auth_mode: str
    username: str
    display_name: str
    role: AuthRole
    organization_id: str | None = None
    active_project_id: str | None = None
    project_ids: frozenset[str] | None = None

    def has_project_access(self, project_id: str | None) -> bool:
        if self.project_ids is None:
            return True

        if project_id is None:
            return False

        return project_id in self.project_ids


def auth_mode() -> str:
    mode = get_settings().auth_mode.strip().lower()
    if mode not in {"disabled", "demo", "formal"}:
        raise HTTPException(status_code=500, detail=f"Unsupported auth mode configured: {get_settings().auth_mode}")

    return mode


def create_demo_token(user: AuthUser) -> str:
    payload = {
        "sub": user.username,
        "role": user.role,
    }
    return _create_signed_token(payload, get_settings().auth_demo_secret)


def create_formal_token(
    username: str,
    display_name: str,
    role: AuthRole,
    organization_id: str,
    project_ids: list[str],
    active_project_id: str | None = None,
) -> str:
    payload = {
        "sub": username,
        "display_name": display_name,
        "role": role,
        "organization_id": organization_id,
        "project_ids": project_ids,
        "project_id": active_project_id or (project_ids[0] if project_ids else None),
    }
    return _create_signed_token(payload, get_settings().auth_formal_secret)


def get_optional_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> AuthUser | None:
    mode = auth_mode()
    if mode == "disabled":
        return None

    if not authorization:
        return None

    context = _auth_context_from_authorization(authorization, mode)
    return AuthUser(
        username=context.username,
        display_name=context.display_name,
        role=context.role,
    )


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> AuthUser | None:
    mode = auth_mode()
    if mode == "disabled":
        return None

    if not authorization:
        raise HTTPException(status_code=401, detail=_required_token_message(mode))

    context = _auth_context_from_authorization(authorization, mode)
    return AuthUser(
        username=context.username,
        display_name=context.display_name,
        role=context.role,
    )


def get_current_auth_context(
    authorization: Annotated[str | None, Header()] = None,
) -> RequestAuthContext | None:
    mode = auth_mode()
    if mode == "disabled":
        return None

    if not authorization:
        raise HTTPException(status_code=401, detail=_required_token_message(mode))

    return _auth_context_from_authorization(authorization, mode)


def require_authenticated_user(
    user: Annotated[RequestAuthContext | None, Depends(get_current_auth_context)],
) -> RequestAuthContext | None:
    return user


def require_ingestion_user(
    user: Annotated[RequestAuthContext | None, Depends(get_current_auth_context)],
) -> RequestAuthContext | None:
    if user is None:
        return None

    if user.role not in {"admin", "analyst"}:
        raise HTTPException(
            status_code=403,
            detail={
                "status": "forbidden",
                "error": "Permission denied for ingestion action.",
                "required_roles": ["admin", "analyst"],
                "role": user.role,
            },
        )

    if user.auth_mode == "formal" and not user.active_project_id:
        raise HTTPException(
            status_code=403,
            detail={
                "status": "forbidden",
                "error": "Project access is required for formal auth write APIs.",
                "required_permission": "project access",
            },
        )

    return user


def require_project_access(user: RequestAuthContext | None, project_id: str | None) -> None:
    if user is None or user.has_project_access(project_id):
        return

    raise HTTPException(
        status_code=403,
        detail={
            "status": "forbidden",
            "error": "Project access denied.",
            "required_permission": "project access",
        },
    )


def filter_documents_for_project_access(user: RequestAuthContext | None, documents):
    if user is None or user.project_ids is None:
        return list(documents)

    return [
        document
        for document in documents
        if document.project_id is not None and user.has_project_access(document.project_id)
    ]


def accessible_project_ids(user: RequestAuthContext | None) -> frozenset[str] | None:
    if user is None:
        return None

    return user.project_ids


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    mode = auth_mode()
    if mode == "disabled":
        raise HTTPException(
            status_code=409,
            detail={
                "auth_mode": "disabled",
                "error": "Demo auth mode is disabled. Set DOCURAG_AUTH_MODE=demo to enable login.",
            },
        )
    if mode == "formal":
        raise HTTPException(
            status_code=409,
            detail={
                "auth_mode": "formal",
                "error": "Formal login runtime is not implemented in this ticket.",
            },
        )

    username = request.username.strip().lower()
    demo_user = DEMO_USERS.get(username)
    if demo_user is None or request.password != demo_user["password"]:
        raise HTTPException(status_code=401, detail="Invalid demo credentials.")

    user = AuthUser(
        username=username,
        display_name=demo_user["display_name"],
        role=demo_user["role"],
    )
    return LoginResponse(
        auth_mode="demo",
        access_token=create_demo_token(user),
        user=user,
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout() -> LogoutResponse:
    return LogoutResponse(auth_mode=auth_mode())


@router.get("/me", response_model=MeResponse)
async def me(
    user: Annotated[AuthUser | None, Depends(get_optional_current_user)],
) -> MeResponse:
    mode = auth_mode()
    return MeResponse(
        auth_mode=mode,
        authenticated=mode in {"demo", "formal"} and user is not None,
        user=user,
    )


def _user_from_authorization(authorization: str) -> AuthUser:
    context = _auth_context_from_authorization(authorization, "demo")
    return AuthUser(
        username=context.username,
        display_name=context.display_name,
        role=context.role,
    )


def _auth_context_from_authorization(authorization: str, mode: str) -> RequestAuthContext:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail=f"{mode.title()} auth token must use Bearer scheme.")

    try:
        payload_token, signature = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid {mode} auth token.") from exc

    secret = get_settings().auth_demo_secret if mode == "demo" else get_settings().auth_formal_secret
    expected_signature = _sign_token_payload(payload_token, secret)
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail=f"Invalid {mode} auth token.")

    try:
        payload = json.loads(_base64_url_decode(payload_token).decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail=f"Invalid {mode} auth token.") from exc

    if mode == "demo":
        return _demo_context_from_payload(payload)

    return _formal_context_from_payload(payload)


def _demo_context_from_payload(payload: dict[str, object]) -> RequestAuthContext:
    username = str(payload.get("sub", "")).strip().lower()
    role = str(payload.get("role", ""))
    demo_user = DEMO_USERS.get(username)
    if demo_user is None or demo_user["role"] != role:
        raise HTTPException(status_code=401, detail="Invalid demo auth token.")

    return RequestAuthContext(
        auth_mode="demo",
        username=username,
        display_name=demo_user["display_name"],
        role=demo_user["role"],
        project_ids=None,
    )


def _formal_context_from_payload(payload: dict[str, object]) -> RequestAuthContext:
    username = str(payload.get("sub", "")).strip().lower()
    display_name = str(payload.get("display_name") or username).strip()
    role = str(payload.get("role", "")).strip().lower()
    organization_id = str(payload.get("organization_id") or "").strip()
    raw_project_ids = payload.get("project_ids")
    active_project_id = str(payload.get("project_id") or "").strip() or None

    if not username or not display_name or role not in AUTH_ROLES:
        raise HTTPException(status_code=401, detail="Invalid formal auth token.")
    if not organization_id:
        raise HTTPException(status_code=401, detail="Invalid formal auth token.")
    if not isinstance(raw_project_ids, list) or not all(isinstance(project_id, str) for project_id in raw_project_ids):
        raise HTTPException(status_code=401, detail="Invalid formal auth token.")

    project_ids = frozenset(project_id.strip() for project_id in raw_project_ids if project_id.strip())
    if active_project_id is not None and active_project_id not in project_ids:
        raise HTTPException(status_code=403, detail=_project_access_forbidden_detail())

    return RequestAuthContext(
        auth_mode="formal",
        username=username,
        display_name=display_name,
        role=role,  # type: ignore[arg-type]
        organization_id=organization_id,
        active_project_id=active_project_id,
        project_ids=project_ids,
    )


def _create_signed_token(payload: dict[str, object], secret: str) -> str:
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_token = _base64_url_encode(payload_json)
    signature = _sign_token_payload(payload_token, secret)
    return f"{payload_token}.{signature}"


def _sign_token_payload(payload_token: str, secret: str) -> str:
    signature = hmac.new(
        secret.encode("utf-8"),
        payload_token.encode("ascii"),
        hashlib.sha256,
    ).digest()

    return _base64_url_encode(signature)


def _required_token_message(mode: str) -> str:
    if mode == "demo":
        return "Demo auth token is required."

    return "Formal auth token is required."


def _project_access_forbidden_detail() -> dict[str, str]:
    return {
        "status": "forbidden",
        "error": "Project access denied.",
        "required_permission": "project access",
    }


def _base64_url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64_url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}".encode("ascii"))
