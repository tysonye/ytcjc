from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TokenUsageCreate(BaseModel):
    input_tokens: int
    output_tokens: int
    model_name: str = ""
    request_text_preview: str = ""


class TokenUsageResponse(BaseModel):
    id: int
    user_id: int
    input_tokens: int
    output_tokens: int
    model_name: str
    request_text_preview: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenQuotaUpdate(BaseModel):
    token_quota: int


class AIConfigResponse(BaseModel):
    base_url: str
    api_key: str
    model_name: str
    system_prompt: str


class AIConfigUpdate(BaseModel):
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    system_prompt: Optional[str] = None
