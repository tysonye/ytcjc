from app.database import engine, SessionLocal, Base
from app.models import Admin, Role, Plan, AIConfig
from app.services.auth_service import hash_password
from sqlalchemy import inspect, text
import json

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    inspector = inspect(engine)
    plan_cols = [c["name"] for c in inspector.get_columns("plans")]
    if "sections" not in plan_cols:
        db.execute(text("ALTER TABLE plans ADD COLUMN sections TEXT DEFAULT ''"))
        db.commit()
        print("添加 plans.sections 字段")

    role_cols = [c["name"] for c in inspector.get_columns("roles")]
    if "sections" not in role_cols:
        db.execute(text("ALTER TABLE roles ADD COLUMN sections TEXT DEFAULT ''"))
        db.commit()
        print("添加 roles.sections 字段")
    if "description" not in role_cols:
        db.execute(text("ALTER TABLE roles ADD COLUMN description TEXT DEFAULT ''"))
        db.commit()
        print("添加 roles.description 字段")

    ai_cols = [c["name"] for c in inspector.get_columns("ai_configs")]
    if "secret_key" not in ai_cols:
        db.execute(text("ALTER TABLE ai_configs ADD COLUMN secret_key VARCHAR(200) DEFAULT ''"))
        db.commit()
        print("添加 ai_configs.secret_key 字段")

    admin_count = db.query(Admin).count()
    if admin_count == 0:
        admin = Admin(username="admin", hashed_password=hash_password("admin123"), is_active=True)
        db.add(admin)
        print("创建默认管理员: admin / admin123")

    role_count = db.query(Role).count()
    if role_count == 0:
        super_role = Role(name="超级管理员", permissions='{"all": true}')
        normal_role = Role(name="普通管理员", permissions='{"users": true, "orders": true}')
        db.add(super_role)
        db.add(normal_role)
        print("创建默认角色: 超级管理员, 普通管理员")

    plan_count = db.query(Plan).count()
    if plan_count == 0:
        plans = [
            Plan(name="免费会员", level="free", price_monthly=0, price_quarterly=0, price_yearly=0, token_amount=0, description="基础数据访问"),
            Plan(name="银牌会员", level="silver", price_monthly=29, price_quarterly=79, price_yearly=289, token_amount=0, description="基本面数据访问"),
            Plan(name="金牌会员", level="gold", price_monthly=59, price_quarterly=159, price_yearly=579, token_amount=0, description="全赔率数据访问"),
            Plan(name="钻石会员", level="diamond", price_monthly=99, price_quarterly=269, price_yearly=989, token_amount=10000, description="全部数据+AI分析师"),
        ]
        plans[0].sections = json.dumps(["titan", "detail"], ensure_ascii=False)
        plans[1].sections = json.dumps(["titan", "five", "detail", "history"], ensure_ascii=False)
        plans[2].sections = json.dumps(["titan", "five", "macau", "odds_trend", "jc_index", "detail", "history"], ensure_ascii=False)
        plans[3].sections = json.dumps(["titan", "five", "macau", "odds_trend", "jc_index", "detail", "ai_chat", "history"], ensure_ascii=False)
        for p in plans:
            db.add(p)
        print("创建默认套餐: 免费/银牌/金牌/钻石（含板块权限）")

    ai_config = db.query(AIConfig).first()
    if not ai_config:
        ai_config = AIConfig(
            base_url="",
            api_key="",
            model_name="",
            system_prompt="你是一位专业的足球分析师，擅长分析比赛数据、赔率走势和球队表现，能够根据历史数据和即时赔率变化给出专业的比赛预测和分析建议。",
        )
        db.add(ai_config)
        print("创建AI默认配置")

    db.commit()
    print("\n数据库初始化完成！")
    print("管理员账号: admin / admin123")
    print("启动命令: uvicorn app.main:app --reload --port 8000")

finally:
    db.close()
