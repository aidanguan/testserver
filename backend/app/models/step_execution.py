"""
步骤执行记录模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class StepStatus(str, enum.Enum):
    """步骤执行状态枚举"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepExecution(Base):
    """步骤执行记录表模型"""
    __tablename__ = "step_execution"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey("test_run.id", ondelete="CASCADE"), nullable=False, index=True)
    step_index = Column(Integer, nullable=False, index=True)
    step_description = Column(Text, nullable=False)
    status = Column(Enum(StepStatus), nullable=False)
    screenshot_path = Column(String(500))
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime)
    error_message = Column(Text)
    
    # 关系
    test_run = relationship("TestRun", back_populates="step_executions")
