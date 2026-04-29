import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ytcjc.db")
SECRET_KEY = os.getenv("SECRET_KEY", "ytcjc-secret-key-change-in-production-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

PROXY_ALLOWED_DOMAINS = [
    "titan007.com",
    "jc.titan007.com",
    "zq.titan007.com",
    "vip.titan007.com",
    "500.com",
    "odds.500.com",
    "trade.500.com",
    "macauslot.com",
    "www.macauslot.com",
]

MEMBERSHIP_LEVELS = ["free", "silver", "gold", "diamond"]

MEMBERSHIP_PRICES = {
    "free": 0,
    "silver": 29,
    "gold": 59,
    "diamond": 99,
}

AI_BASE_URL = os.getenv("AI_BASE_URL", "")
AI_API_KEY = os.getenv("AI_API_KEY", "")
