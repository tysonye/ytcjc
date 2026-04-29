from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrderCreate(BaseModel):
    plan_id: int
    payment_method: str = "alipay"
    duration: str = "monthly"


class OrderResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    amount: float
    payment_method: str
    payment_status: str
    order_no: str
    created_at: datetime
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PlanResponse(BaseModel):
    id: int
    name: str
    level: str
    price_monthly: float
    price_quarterly: float
    price_yearly: float
    token_amount: int
    description: str
    is_active: bool

    class Config:
        from_attributes = True


class PlanCreate(BaseModel):
    name: str
    level: str
    price_monthly: float = 0
    price_quarterly: float = 0
    price_yearly: float = 0
    token_amount: int = 0
    description: str = ""
