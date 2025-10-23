"""
测试用例相关的Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class StandardStep(BaseModel):
    """标准化步骤Schema"""
    index: int
    action: str
    description: str
    selector: Optional[str] = None
    value: Optional[str] = None
    expected: Optional[str] = None


class PlaywrightStep(BaseModel):
    """Playwright步骤Schema"""
    index: int
    action: str
    selector: Optional[str] = None
    value: Optional[str] = None
    description: str
    screenshot: bool = True


class TestCaseBase(BaseModel):
    """测试用例基础Schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    natural_language: str = Field(..., min_length=1)
    expected_result: str = Field(..., min_length=1)


class TestCaseCreate(TestCaseBase):
    """创建测试用例Schema"""
    project_id: int
    standard_steps: List[Dict[str, Any]]
    playwright_script: Dict[str, Any]


class TestCaseUpdate(BaseModel):
    """更新测试用例Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    natural_language: Optional[str] = None
    standard_steps: Optional[List[Dict[str, Any]]] = None
    playwright_script: Optional[Dict[str, Any]] = None
    expected_result: Optional[str] = None


class TestCaseResponse(TestCaseBase):
    """测试用例响应Schema"""
    id: int
    project_id: int
    standard_steps: List[Dict[str, Any]]
    playwright_script: Dict[str, Any]
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TestCaseWithStatsResponse(TestCaseResponse):
    """带统计数据的测试用例响应Schema"""
    execution_count: int = Field(0, description="执行次数")
    pass_rate: float = Field(0.0, description="成功率")


class NaturalLanguageRequest(BaseModel):
    """自然语言生成用例请求Schema"""
    project_id: int
    natural_language: str = Field(..., min_length=1)


class StandardCaseResponse(BaseModel):
    """标准化用例响应Schema"""
    name: str
    description: str
    standard_steps: List[Dict[str, Any]]
    expected_result: str


class ScriptGenerationRequest(BaseModel):
    """生成脚本请求Schema"""
    test_case_id: int


class ScriptGenerationResponse(BaseModel):
    """生成脚本响应Schema"""
    playwright_script: Dict[str, Any]
