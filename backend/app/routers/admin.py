from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User, Admin, Role, Order, TokenUsage
from app.schemas.admin import AdminLoginRequest, AdminCreate, RoleCreate, RoleUpdate, StatisticsResponse
from app.services.auth_service import hash_password, verify_password, create_access_token, get_current_admin
from app.schemas.user import UserListResponse

router = APIRouter(prefix="/api/admin", tags=["后台管理"])


@router.post("/login")
def admin_login(req: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == req.username).first()
    if not admin or not verify_password(req.password, admin.hashed_password):
        raise HTTPException(status_code=401, detail="管理员用户名或密码错误")
    if not admin.is_active:
        raise HTTPException(status_code=403, detail="管理员账号已被禁用")
    token = create_access_token(data={"sub": str(admin.id), "is_admin": True})
    return {"access_token": token, "token_type": "bearer", "admin_info": {"id": admin.id, "username": admin.username}}


@router.get("/users")
def admin_list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    membership_level: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if membership_level:
        query = query.filter(User.membership_level == membership_level)
    if search:
        query = query.filter(
            (User.username.contains(search)) | (User.email.contains(search)) | (User.phone.contains(search))
        )
    users = query.offset(skip).limit(limit).all()
    return {
        "items": [
            {
                "id": u.id, "username": u.username, "email": u.email, "phone": u.phone,
                "membership_level": u.membership_level, "membership_expires_at": u.membership_expires_at.isoformat() if u.membership_expires_at else None,
                "token_quota": u.token_quota, "token_used": u.token_used, "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ]
    }


@router.put("/users/{user_id}")
def admin_update_user(user_id: int, update_data: dict, admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    for key in ["email", "phone", "token_quota"]:
        if key in update_data:
            setattr(user, key, update_data[key])
    db.commit()
    return {"status": "ok"}


@router.put("/users/{user_id}/level")
def admin_update_user_level(user_id: int, update_data: dict, admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    level = update_data.get("membership_level")
    duration_days = update_data.get("duration_days", 30)
    if level not in ["free", "silver", "gold", "diamond"]:
        raise HTTPException(status_code=400, detail="无效的会员等级")
    user.membership_level = level
    if level != "free":
        user.membership_expires_at = datetime.now() + timedelta(days=duration_days)
    else:
        user.membership_expires_at = None
    db.commit()
    return {"status": "ok"}


@router.put("/users/{user_id}/toggle-active")
def admin_toggle_user_active(user_id: int, admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.is_active = not user.is_active
    db.commit()
    return {"status": "ok", "is_active": user.is_active}


@router.get("/orders")
def admin_list_orders(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.created_at.desc()).limit(100).all()
    return [
        {
            "id": o.id, "order_no": o.order_no, "username": db.query(User).filter(User.id == o.user_id).first().username if o.user_id else "",
            "plan_name": o.plan_name, "amount": o.amount, "status": o.payment_status,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }
        for o in orders
    ]


@router.put("/orders/{order_id}/confirm")
def admin_confirm_order(order_id: int, admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    order.payment_status = "paid"
    order.paid_at = datetime.now()
    user = db.query(User).filter(User.id == order.user_id).first()
    if user and order.plan_level:
        user.membership_level = order.plan_level
        user.membership_expires_at = datetime.now() + timedelta(days=30)
    db.commit()
    return {"status": "ok"}


@router.put("/orders/{order_id}/cancel")
def admin_cancel_order(order_id: int, admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    order.payment_status = "cancelled"
    db.commit()
    return {"status": "ok"}


@router.get("/token-stats")
def admin_token_stats(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    total_quota = sum(u.token_quota for u in users)
    total_used = sum(u.token_used for u in users)
    active_users = sum(1 for u in users if u.is_active)
    records = [
        {
            "username": u.username, "token_quota": u.token_quota, "token_used": u.token_used,
            "last_used_at": u.updated_at.isoformat() if u.updated_at else None,
        }
        for u in users if u.token_quota > 0
    ]
    return {"total_quota": total_quota, "total_used": total_used, "active_users": active_users, "records": records}


@router.get("/stats/overview")
def admin_stats_overview(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    paid_users = db.query(User).filter(User.membership_level != "free").count()
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = sum(o.amount for o in db.query(Order).filter(Order.payment_status == "paid", Order.paid_at >= month_start).all())
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_new = db.query(User).filter(User.created_at >= today_start).count()

    free_count = db.query(User).filter(User.membership_level == "free").count()
    silver_count = db.query(User).filter(User.membership_level == "silver").count()
    gold_count = db.query(User).filter(User.membership_level == "gold").count()
    diamond_count = db.query(User).filter(User.membership_level == "diamond").count()

    recent_days = []
    recent_counts = []
    for i in range(6, -1, -1):
        d = datetime.now() - timedelta(days=i)
        d_start = d.replace(hour=0, minute=0, second=0, microsecond=0)
        d_end = d_start + timedelta(days=1)
        count = db.query(User).filter(User.created_at >= d_start, User.created_at < d_end).count()
        recent_days.append(d.strftime("%m/%d"))
        recent_counts.append(count)

    return {
        "totalUsers": total_users, "paidUsers": paid_users, "monthlyRevenue": monthly_revenue, "todayNew": today_new,
        "freeCount": free_count, "silverCount": silver_count, "goldCount": gold_count, "diamondCount": diamond_count,
        "recentDays": recent_days, "recentCounts": recent_counts,
    }


@router.get("/roles")
def admin_list_roles(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    return [
        {
            "id": r.id, "name": r.name, "level": r.name.lower() if r.name else "free",
            "description": r.permissions or "", "sections": ["titan", "five", "macau", "odds_trend", "jc_index", "detail", "ai_chat", "history"],
        }
        for r in roles
    ]


@router.put("/roles/{role_id}")
def admin_update_role(role_id: int, req: dict, admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if "name" in req:
        role.name = req["name"]
    if "description" in req:
        role.permissions = req["description"]
    if "sections" in req:
        role.permissions = ",".join(req["sections"])
    db.commit()
    return {"status": "ok"}


@router.post("/roles")
def create_role(req: dict, admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    role = Role(name=req.get("name", ""), permissions=req.get("permissions", ""))
    db.add(role)
    db.commit()
    db.refresh(role)
    return {"id": role.id, "name": role.name}


@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    users_by_level = {}
    for level in ["free", "silver", "gold", "diamond"]:
        users_by_level[level] = db.query(User).filter(User.membership_level == level).count()
    total_revenue = sum(o.amount for o in db.query(Order).filter(Order.payment_status == "paid").all())
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = sum(o.amount for o in db.query(Order).filter(Order.payment_status == "paid", Order.paid_at >= month_start).all())
    day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    daily_active = db.query(TokenUsage).filter(TokenUsage.created_at >= day_start).distinct(TokenUsage.user_id).count()
    month_active = db.query(TokenUsage).filter(TokenUsage.created_at >= month_start).distinct(TokenUsage.user_id).count()
    total_orders = db.query(Order).count()
    total_tokens = sum(u.input_tokens + u.output_tokens for u in db.query(TokenUsage).all())
    return StatisticsResponse(
        total_users=total_users, users_by_level=users_by_level, total_revenue=total_revenue,
        monthly_revenue=monthly_revenue, daily_active_users=daily_active, monthly_active_users=month_active,
        total_orders=total_orders, total_tokens_used=total_tokens,
    )


@router.get("/admins")
def list_admins(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    admins = db.query(Admin).all()
    return [{"id": a.id, "username": a.username, "is_active": a.is_active, "role_id": a.role_id} for a in admins]


@router.post("/admins")
def create_admin(req: AdminCreate, admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    existing = db.query(Admin).filter(Admin.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="管理员用户名已存在")
    new_admin = Admin(username=req.username, hashed_password=hash_password(req.password), role_id=req.role_id)
    db.add(new_admin)
    db.commit()
    return {"status": "ok"}
