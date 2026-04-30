from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, users, tokens, orders, proxy, admin, user_config
from app.routers.orders import plan_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="竞彩足球Web平台API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tokens.router)
app.include_router(orders.router)
app.include_router(plan_router)
app.include_router(proxy.router)
app.include_router(admin.router)
app.include_router(user_config.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
