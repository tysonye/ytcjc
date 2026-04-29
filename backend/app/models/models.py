from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    membership_level = Column(String(20), default="free", nullable=False)
    membership_expires_at = Column(DateTime, nullable=True)
    token_quota = Column(Integer, default=0)
    token_used = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    wechat_openid = Column(String(100), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    orders = relationship("Order", back_populates="user")
    token_usages = relationship("TokenUsage", back_populates="user")


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    role = relationship("Role", back_populates="admins")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    permissions = Column(Text, default="{}")
    created_at = Column(DateTime, server_default=func.now())

    admins = relationship("Admin", back_populates="role")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(20), default="alipay")
    payment_status = Column(String(20), default="pending")
    order_no = Column(String(50), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    paid_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="orders")
    plan = relationship("Plan")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    level = Column(String(20), nullable=False)
    price_monthly = Column(Float, default=0)
    price_quarterly = Column(Float, default=0)
    price_yearly = Column(Float, default=0)
    token_amount = Column(Integer, default=0)
    description = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class TokenUsage(Base):
    __tablename__ = "token_usages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    model_name = Column(String(50), default="")
    request_text_preview = Column(String(200), default="")
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="token_usages")


class AIConfig(Base):
    __tablename__ = "ai_configs"

    id = Column(Integer, primary_key=True, index=True)
    base_url = Column(String(200), default="")
    api_key = Column(String(200), default="")
    model_name = Column(String(50), default="")
    system_prompt = Column(Text, default="")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
