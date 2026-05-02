from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import SECRET_KEY as DEFAULT_SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_db, SessionLocal
from app.models import User, Admin, AIConfig

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

_cached_secret_key = None
_cache_time = None
CACHE_TTL = 300


def _get_effective_secret_key() -> str:
    global _cached_secret_key, _cache_time
    now = datetime.utcnow()
    if _cached_secret_key and _cache_time and (now - _cache_time).total_seconds() < CACHE_TTL:
        return _cached_secret_key
    try:
        db = SessionLocal()
        config = db.query(AIConfig).first()
        db.close()
        if config and config.secret_key:
            _cached_secret_key = config.secret_key
        else:
            _cached_secret_key = DEFAULT_SECRET_KEY
    except Exception:
        _cached_secret_key = DEFAULT_SECRET_KEY
    _cache_time = now
    return _cached_secret_key


def get_secret_key() -> str:
    return _get_effective_secret_key()


def clear_secret_cache():
    global _cached_secret_key, _cache_time
    _cached_secret_key = None
    _cache_time = None


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM], options={"verify_sub": False})
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except (JWTError, ValueError):
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="管理员验证失败",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        admin_id: int = payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)
        if admin_id is None or not is_admin:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if admin is None:
        raise credentials_exception
    return admin
