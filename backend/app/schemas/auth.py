from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_info: "UserResponse"


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    membership_level: str
    membership_expires_at: Optional[datetime] = None
    token_quota: int
    token_used: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WechatLoginRequest(BaseModel):
    code: str
