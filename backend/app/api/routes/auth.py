from typing import Annotated
import base64
import hashlib
import hmac
import json

from fastapi import APIRouter, Depends, Header, HTTPException

from app.core.config import get_settings
from app.schemas.auth import AuthUser, LoginRequest, LoginResponse, LogoutResponse, MeResponse


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


def auth_mode() -> str:
    mode = get_settings().auth_mode.strip().lower()
    if mode not in {"disabled", "demo"}:
        raise HTTPException(status_code=500, detail=f"Unsupported auth mode configured: {get_settings().auth_mode}")

    return mode


def create_demo_token(user: AuthUser) -> str:
    payload = {
        "sub": user.username,
        "role": user.role,
    }
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_token = _base64_url_encode(payload_json)
    signature = _sign_token_payload(payload_token)

    return f"{payload_token}.{signature}"


def get_optional_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> AuthUser | None:
    if auth_mode() == "disabled":
        return None

    if not authorization:
        return None

    return _user_from_authorization(authorization)


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> AuthUser | None:
    if auth_mode() == "disabled":
        return None

    if not authorization:
        raise HTTPException(status_code=401, detail="Demo auth token is required.")

    return _user_from_authorization(authorization)


def require_authenticated_user(
    user: Annotated[AuthUser | None, Depends(get_current_user)],
) -> AuthUser | None:
    return user


def require_ingestion_user(
    user: Annotated[AuthUser | None, Depends(get_current_user)],
) -> AuthUser | None:
    if user is None:
        return None

    if user.role not in {"admin", "analyst"}:
        raise HTTPException(
            status_code=403,
            detail={
                "status": "forbidden",
                "error": "Viewer role cannot perform ingestion actions in demo auth mode.",
                "required_roles": ["admin", "analyst"],
                "role": user.role,
            },
        )

    return user


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    if auth_mode() == "disabled":
        raise HTTPException(
            status_code=409,
            detail={
                "auth_mode": "disabled",
                "error": "Demo auth mode is disabled. Set DOCURAG_AUTH_MODE=demo to enable login.",
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
        authenticated=mode == "demo" and user is not None,
        user=user,
    )


def _user_from_authorization(authorization: str) -> AuthUser:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Demo auth token must use Bearer scheme.")

    try:
        payload_token, signature = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid demo auth token.") from exc

    expected_signature = _sign_token_payload(payload_token)
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid demo auth token.")

    try:
        payload = json.loads(_base64_url_decode(payload_token).decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid demo auth token.") from exc

    username = str(payload.get("sub", "")).strip().lower()
    role = str(payload.get("role", ""))
    demo_user = DEMO_USERS.get(username)
    if demo_user is None or demo_user["role"] != role:
        raise HTTPException(status_code=401, detail="Invalid demo auth token.")

    return AuthUser(
        username=username,
        display_name=demo_user["display_name"],
        role=demo_user["role"],
    )


def _sign_token_payload(payload_token: str) -> str:
    signature = hmac.new(
        get_settings().auth_demo_secret.encode("utf-8"),
        payload_token.encode("ascii"),
        hashlib.sha256,
    ).digest()

    return _base64_url_encode(signature)


def _base64_url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64_url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}".encode("ascii"))
