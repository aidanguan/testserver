"""
测试运行相关的Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.test_run import TestRunStatus, LLMVerdict
from app.models.step_execution import StepStatus


class ExecuteTestRequest(BaseModel):
    """执行测试请求Schema"""
    test_case_id: int


class StepExecutionResponse(BaseModel):
    """步骤执行响应Schema"""
    id: int
    test_run_id: int
    step_index: int
    step_description: str
    status: StepStatus
    screenshot_path: Optional[str] = None
    vision_observation: Optional[str] = None  # 视觉观察结果（JSON字符串）
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class TestRunResponse(BaseModel):
    """测试运行响应Schema"""
    id: int
    test_case_id: int
    status: TestRunStatus
    trigger_by: int
    start_time: datetime
    end_time: Optional[datetime] = None
    llm_verdict: Optional[LLMVerdict] = None
    llm_reason: Optional[str] = None
    error_message: Optional[str] = None
    artifacts_path: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TestRunDetailResponse(TestRunResponse):
    """测试运行详情响应Schema"""
    steps: List[StepExecutionResponse] = []
    test_case: Optional[Dict[str, Any]] = None
