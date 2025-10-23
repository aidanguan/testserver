"""
步骤执行记录模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import Optional
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
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    test_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("test_run.id", ondelete="CASCADE"), nullable=False, index=True)
    step_index: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    step_description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[StepStatus] = mapped_column(Enum(StepStatus), nullable=False)
    screenshot_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    vision_observation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 视觉观察结果（JSON格式）
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 关系
    test_run = relationship("TestRun", back_populates="step_executions")
