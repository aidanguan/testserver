"""
测试用例模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class TestCase(Base):
    """测试用例表模型"""
    __tablename__ = "test_case"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    natural_language = Column(Text, nullable=False)
    standard_steps = Column(JSON, nullable=False)
    playwright_script = Column(JSON, nullable=False)
    expected_result = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    project = relationship("Project", back_populates="test_cases")
    creator = relationship("User", back_populates="created_test_cases", foreign_keys=[created_by])
    test_runs = relationship("TestRun", back_populates="test_case", cascade="all, delete-orphan")
