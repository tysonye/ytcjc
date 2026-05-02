from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import re
import json

from app.database import get_db
from app.models import User, Plan
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse, WechatLoginRequest
from app.services.auth_service import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


def get_user_accessible_sections(db: Session, membership_level: str) -> list:
    plan = db.query(Plan).filter(Plan.level == membership_level, Plan.is_active == True).first()
    if not plan or not plan.sections:
        return []
    try:
        return json.loads(plan.sections)
    except:
        return []


def validate_password_strength(password: str) -> str | None:
    if len(password) < 8:
        return "密码至少需要8个字符"
    if len(password) > 30:
        return "密码不能超过30个字符"
    if not re.search(r'[a-zA-Z]', password):
        return "密码必须包含字母"
    if not re.search(r'\d', password):
        return "密码必须包含数字"
    has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?~`]', password))
    if not has_special and len(password) < 12:
        return "密码强度不足，建议包含字母、数字和特殊字符，或设置12位以上密码"
    return None


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    pass_error = validate_password_strength(req.password)
    if pass_error:
        raise HTTPException(status_code=400, detail=pass_error)
    if len(req.username) < 3:
        raise HTTPException(status_code=400, detail="用户名至少需要3个字符")
    if len(req.username) > 20:
        raise HTTPException(status_code=400, detail="用户名不能超过20个字符")
    if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', req.username):
        raise HTTPException(status_code=400, detail="用户名只能包含字母、数字、下划线或中文")
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=req.username,
        hashed_password=hash_password(req.password),
        email=req.email,
        phone=req.phone,
        membership_level="free",
        token_quota=0,
        token_used=0,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(data={"sub": user.id})
    sections = get_user_accessible_sections(db, user.membership_level)
    return TokenResponse(
        access_token=token,
        user_info=UserResponse.model_validate(user),
        accessible_sections=sections,
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    token = create_access_token(data={"sub": user.id})
    sections = get_user_accessible_sections(db, user.membership_level)
    return TokenResponse(
        access_token=token,
        user_info=UserResponse.model_validate(user),
        accessible_sections=sections,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.get("/sections")
def get_accessible_sections(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sections = get_user_accessible_sections(db, current_user.membership_level)
    return {"sections": sections, "membership_level": current_user.membership_level}


@router.post("/wechat")
def wechat_login(req: WechatLoginRequest):
    return {"message": "微信小程序功能即将上线", "code": "WECHAT_COMING_SOON"}
