"""
用户模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import Optional, List
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    ADMIN = "Admin"
    MEMBER = "Member"


class User(Base):
    """用户表模型"""
    __tablename__ = "user"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # 关系
    created_projects = relationship("Project", back_populates="creator", foreign_keys="Project.created_by")
    created_test_cases = relationship("TestCase", back_populates="creator", foreign_keys="TestCase.created_by")
    triggered_test_runs = relationship("TestRun", back_populates="trigger_user", foreign_keys="TestRun.trigger_by")
    audit_logs = relationship("AuditLog", back_populates="user")
