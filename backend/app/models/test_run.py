"""
测试运行记录模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
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
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    test_case_id = Column(Integer, ForeignKey("test_case.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Enum(TestRunStatus), nullable=False, index=True)
    trigger_by = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    end_time = Column(DateTime)
    llm_verdict = Column(Enum(LLMVerdict))
    llm_reason = Column(Text)
    error_message = Column(Text)
    artifacts_path = Column(String(500))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关系
    test_case = relationship("TestCase", back_populates="test_runs")
    trigger_user = relationship("User", back_populates="triggered_test_runs", foreign_keys=[trigger_by])
    step_executions = relationship("StepExecution", back_populates="test_run", cascade="all, delete-orphan")
