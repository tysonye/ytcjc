from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User
from app.schemas.user import UserUpdate, MembershipUpdate, BatchUpdateRequest, UserListResponse, UserStatusUpdate
from app.schemas.auth import UserResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/users", tags=["会员管理"])


@router.get("/", response_model=List[UserListResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    membership_level: str = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if membership_level:
        query = query.filter(User.membership_level == membership_level)
    if search:
        query = query.filter(
            (User.username.contains(search)) | (User.email.contains(search)) | (User.phone.contains(search))
        )
    return query.offset(skip).limit(limit).all()


@router.get("/me", response_model=UserResponse)
def get_my_info(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserListResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.put("/{user_id}", response_model=UserListResponse)
def update_user(user_id: int, req: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if req.email is not None:
        user.email = req.email
    if req.phone is not None:
        user.phone = req.phone
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/membership", response_model=UserListResponse)
def update_membership(user_id: int, req: MembershipUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.membership_level = req.membership_level
    if req.expires_at:
        user.membership_expires_at = req.expires_at
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/status", response_model=UserListResponse)
def update_status(user_id: int, req: UserStatusUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.is_active = req.is_active
    db.commit()
    db.refresh(user)
    return user


@router.post("/batch-update")
def batch_update(req: BatchUpdateRequest, db: Session = Depends(get_db)):
    users = db.query(User).filter(User.id.in_(req.user_ids)).all()
    for user in users:
        if req.membership_level:
            user.membership_level = req.membership_level
        if req.expires_at:
            user.membership_expires_at = req.expires_at
        if req.is_active is not None:
            user.is_active = req.is_active
    db.commit()
    return {"updated": len(users)}


@router.post("/bind-wechat")
def bind_wechat(current_user: User = Depends(get_current_user)):
    return {"message": "微信小程序功能即将上线", "code": "WECHAT_COMING_SOON"}
