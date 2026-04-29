import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Order, Plan, User
from app.schemas.order import OrderCreate, OrderResponse, PlanResponse, PlanCreate
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/orders", tags=["订单管理"])
plan_router = APIRouter(prefix="/api/plans", tags=["套餐管理"])


@plan_router.get("/", response_model=List[PlanResponse])
def list_plans(db: Session = Depends(get_db)):
    return db.query(Plan).filter(Plan.is_active == True).all()


@plan_router.post("/", response_model=PlanResponse)
def create_plan(req: PlanCreate, db: Session = Depends(get_db)):
    plan = Plan(**req.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@plan_router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: int, req: PlanCreate, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="套餐不存在")
    for key, value in req.model_dump().items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan


@router.post("/", response_model=OrderResponse)
def create_order(req: OrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == req.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="套餐不存在")
    price_map = {"monthly": plan.price_monthly, "quarterly": plan.price_quarterly, "yearly": plan.price_yearly}
    amount = price_map.get(req.duration, plan.price_monthly)
    order = Order(
        user_id=current_user.id,
        plan_id=req.plan_id,
        amount=amount,
        payment_method=req.payment_method,
        order_no=f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/", response_model=List[OrderResponse])
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Order).filter(Order.user_id == current_user.id).offset(skip).limit(limit).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.post("/callback")
def payment_callback(order_no: str, status: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_no == order_no).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    order.payment_status = status
    if status == "paid":
        order.paid_at = datetime.now()
        user = db.query(User).filter(User.id == order.user_id).first()
        plan = db.query(Plan).filter(Plan.id == order.plan_id).first()
        if user and plan:
            user.membership_level = plan.level
            user.membership_expires_at = datetime.now().replace(year=datetime.now().year + 1)
            user.token_quota += plan.token_amount
    db.commit()
    return {"status": "ok"}


@router.post("/pay/wechat")
def wechat_pay(order_id: int, current_user: User = Depends(get_current_user)):
    return {"message": "微信支付功能即将上线", "code": "WECHAT_PAY_COMING_SOON"}


@router.get("/export")
def export_orders(format: str = "csv", db: Session = Depends(get_db)):
    import pandas as pd
    import io
    orders = db.query(Order).all()
    data = [{"order_no": o.order_no, "user_id": o.user_id, "amount": o.amount, "payment_status": o.payment_status, "created_at": str(o.created_at)} for o in orders]
    df = pd.DataFrame(data)
    if format == "excel":
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        from fastapi.responses import StreamingResponse
        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=orders.xlsx"})
    else:
        output = io.StringIO()
        df.to_csv(output, index=False)
        from fastapi.responses import StreamingResponse
        output.seek(0)
        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=orders.csv"})
