"""
用户模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    ADMIN = "Admin"
    MEMBER = "Member"


class User(Base):
    """用户表模型"""
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # 关系
    created_projects = relationship("Project", back_populates="creator", foreign_keys="Project.created_by")
    created_test_cases = relationship("TestCase", back_populates="creator", foreign_keys="TestCase.created_by")
    triggered_test_runs = relationship("TestRun", back_populates="trigger_user", foreign_keys="TestRun.trigger_by")
    audit_logs = relationship("AuditLog", back_populates="user")
