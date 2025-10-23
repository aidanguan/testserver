"""
测试用例模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.database import Base


class TestCase(Base):
    """测试用例表模型"""
    __tablename__ = "test_case"
    __allow_unmapped__ = True  # 允许未使用 Mapped[] 的字段
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    natural_language: Mapped[str] = mapped_column(Text, nullable=False)
    # JSON 字段：运行时为 JSON 类型，但类型检查时作为 List 和 Dict
    standard_steps: Any = mapped_column(JSON, nullable=False)
    playwright_script: Any = mapped_column(JSON, nullable=False)
    expected_result: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    project = relationship("Project", back_populates="test_cases")
    creator = relationship("User", back_populates="created_test_cases", foreign_keys=[created_by])
    test_runs = relationship("TestRun", back_populates="test_case", cascade="all, delete-orphan")
