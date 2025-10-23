"""
测试运行记录模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import Optional, List
import enum
from app.database import Base


class TestRunStatus(str, enum.Enum):
    """测试运行状态枚举"""
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"


class LLMVerdict(str, enum.Enum):
    """LLM判定结果枚举"""
    PASSED = "passed"
    FAILED = "failed"
    UNKNOWN = "unknown"


class TestRun(Base):
    """测试运行记录表模型"""
    __tablename__ = "test_run"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    test_case_id: Mapped[int] = mapped_column(Integer, ForeignKey("test_case.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[TestRunStatus] = mapped_column(Enum(TestRunStatus), nullable=False, index=True)
    trigger_by: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    llm_verdict: Mapped[Optional[LLMVerdict]] = mapped_column(Enum(LLMVerdict), nullable=True)
    llm_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    artifacts_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关系
    test_case = relationship("TestCase", back_populates="test_runs")
    trigger_user = relationship("User", back_populates="triggered_test_runs", foreign_keys=[trigger_by])
    step_executions = relationship("StepExecution", back_populates="test_run", cascade="all, delete-orphan")
