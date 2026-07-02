from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class SessionResponse(BaseModel):
    id: str
    device_name: str | None
    device_id: str | None
    ip_address: str | None
    location: str | None
    user_agent: str | None
    is_current: bool = False
    last_activity_at: datetime | None
    created_at: datetime
    expires_at: datetime

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]
    total: int


class RevokeSessionRequest(BaseModel):
    session_id: str


class MFAEnableResponse(BaseModel):
    secret: str
    qr_code_url: str
    backup_codes: list[str]


class MFAVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


class MFAStatusResponse(BaseModel):
    mfa_enabled: bool
    mfa_type: str | None


class MFADisableRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


class SendEmailVerificationResponse(BaseModel):
    message: str = "Verification email sent"


class VerifyEmailRequest(BaseModel):
    token: str


class VerifyEmailResponse(BaseModel):
    message: str = "Email verified successfully"


class UpdateProfileRequest(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    phone: str | None = None
    locale: str | None = None
    timezone: str | None = None


class UpdateProfileResponse(BaseModel):
    id: str
    email: str
    username: str
    phone: str | None
    role: str
    status: str
    is_verified: bool
    profile_photo_url: str | None
    locale: str
    timezone: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserSessionsResponse(BaseModel):
    active_sessions: int
    current_session: SessionResponse | None
    other_sessions: list[SessionResponse]
