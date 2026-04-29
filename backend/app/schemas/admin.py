from pydantic import BaseModel
from typing import Optional, Dict, Any


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminCreate(BaseModel):
    username: str
    password: str
    role_id: Optional[int] = None


class RoleCreate(BaseModel):
    name: str
    permissions: str = "{}"


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    permissions: Optional[str] = None


class StatisticsResponse(BaseModel):
    total_users: int = 0
    users_by_level: Dict[str, int] = {}
    total_revenue: float = 0
    monthly_revenue: float = 0
    daily_active_users: int = 0
    monthly_active_users: int = 0
    total_orders: int = 0
    total_tokens_used: int = 0
