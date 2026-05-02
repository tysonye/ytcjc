from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserSectionConfig
from app.services.auth_service import get_current_user
from app.models import User

router = APIRouter(prefix="/api/user-config", tags=["用户配置"])


@router.get("/sections")
def get_section_config(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    config = db.query(UserSectionConfig).filter(UserSectionConfig.user_id == current_user.id).first()
    if not config:
        return {"titan_config": "", "five_config": "", "ai_settings": ""}
    return {
        "titan_config": config.titan_config,
        "five_config": config.five_config,
        "ai_settings": config.ai_settings,
    }


@router.put("/sections")
def update_section_config(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    config = db.query(UserSectionConfig).filter(UserSectionConfig.user_id == current_user.id).first()
    if not config:
        config = UserSectionConfig(user_id=current_user.id)
        db.add(config)

    if "titan_config" in data:
        config.titan_config = data["titan_config"]
    if "five_config" in data:
        config.five_config = data["five_config"]
    if "ai_settings" in data:
        config.ai_settings = data["ai_settings"]

    db.commit()
    db.refresh(config)
    return {"message": "配置已保存"}
