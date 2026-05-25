from typing import Literal

from pydantic import BaseModel, Field


AuthRole = Literal["admin", "analyst", "viewer"]


class AuthUser(BaseModel):
    username: str = Field(..., min_length=1)
    display_name: str = Field(..., min_length=1)
    role: AuthRole


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    auth_mode: str
    access_token: str
    token_type: str = "bearer"
    user: AuthUser


class MeResponse(BaseModel):
    auth_mode: str
    authenticated: bool
    user: AuthUser | None = None


class LogoutResponse(BaseModel):
    auth_mode: str
    status: str = "logged_out"
