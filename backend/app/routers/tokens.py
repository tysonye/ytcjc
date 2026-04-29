from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import TokenUsage, AIConfig, User
from app.schemas.token import TokenUsageCreate, TokenUsageResponse, TokenQuotaUpdate, AIConfigResponse, AIConfigUpdate
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/tokens", tags=["Token管理"])


@router.post("/usage", response_model=TokenUsageResponse)
def create_usage(req: TokenUsageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    usage = TokenUsage(
        user_id=current_user.id,
        input_tokens=req.input_tokens,
        output_tokens=req.output_tokens,
        model_name=req.model_name,
        request_text_preview=req.request_text_preview[:200],
    )
    current_user.token_used += req.input_tokens + req.output_tokens
    db.add(usage)
    db.commit()
    db.refresh(usage)
    return usage


@router.get("/usage", response_model=List[TokenUsageResponse])
def list_usage(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(TokenUsage).filter(TokenUsage.user_id == current_user.id).offset(skip).limit(limit).all()


@router.get("/quota")
def get_quota(current_user: User = Depends(get_current_user)):
    return {"token_quota": current_user.token_quota, "token_used": current_user.token_used, "token_remaining": current_user.token_quota - current_user.token_used}


@router.put("/quota")
def update_quota(req: TokenQuotaUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.token_quota = req.token_quota
    db.commit()
    return {"token_quota": current_user.token_quota}


@router.get("/statistics")
def get_statistics(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(TokenUsage)
    if user_id:
        query = query.filter(TokenUsage.user_id == user_id)
    usages = query.all()
    total_input = sum(u.input_tokens for u in usages)
    total_output = sum(u.output_tokens for u in usages)
    return {"total_records": len(usages), "total_input_tokens": total_input, "total_output_tokens": total_output, "total_tokens": total_input + total_output}


@router.get("/ai/config", response_model=AIConfigResponse)
def get_ai_config(db: Session = Depends(get_db)):
    config = db.query(AIConfig).first()
    if not config:
        config = AIConfig(base_url="", api_key="", model_name="", system_prompt="你是一位专业的足球分析师，擅长分析比赛数据、赔率走势和球队表现。")
        db.add(config)
        db.commit()
        db.refresh(config)
    return AIConfigResponse(base_url=config.base_url, api_key=config.api_key, model_name=config.model_name, system_prompt=config.system_prompt)


@router.put("/ai/config", response_model=AIConfigResponse)
def update_ai_config(req: AIConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(AIConfig).first()
    if not config:
        config = AIConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    if req.base_url is not None:
        config.base_url = req.base_url
    if req.api_key is not None:
        config.api_key = req.api_key
    if req.model_name is not None:
        config.model_name = req.model_name
    if req.system_prompt is not None:
        config.system_prompt = req.system_prompt
    db.commit()
    db.refresh(config)
    return AIConfigResponse(base_url=config.base_url, api_key=config.api_key, model_name=config.model_name, system_prompt=config.system_prompt)
