from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserUpdate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None


class MembershipUpdate(BaseModel):
    membership_level: str
    expires_at: Optional[datetime] = None


class BatchUpdateRequest(BaseModel):
    user_ids: List[int]
    membership_level: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class UserListResponse(BaseModel):
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


class UserStatusUpdate(BaseModel):
    is_active: bool
