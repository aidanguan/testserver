"""
项目模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import Optional
from app.database import Base


class Project(Base):
    """项目表模型"""
    __tablename__ = "project"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    llm_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    llm_model: Mapped[str] = mapped_column(String(100), nullable=False)
    llm_api_key: Mapped[str] = mapped_column(String(255), nullable=False)
    llm_base_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment='LLM API基础URL')
    llm_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    creator = relationship("User", back_populates="created_projects", foreign_keys=[created_by])
    test_cases = relationship("TestCase", back_populates="project", cascade="all, delete-orphan")
