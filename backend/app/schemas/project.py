"""
项目相关的Schema
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime


class LLMConfig(BaseModel):
    """LLM配置Schema"""
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(2000, gt=0)
    top_p: Optional[float] = Field(1.0, ge=0.0, le=1.0)


class ProjectBase(BaseModel):
    """项目基础Schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    base_url: str = Field(..., min_length=1, max_length=500)
    llm_provider: str = Field(..., description="LLM提供商: openai, anthropic, dashscope, openai-completion")
    llm_model: str = Field(..., description="模型名称")
    llm_api_key: str = Field(..., min_length=1)
    llm_base_url: Optional[str] = Field(None, description="LLM API自定义基础URL")
    llm_config: Optional[Dict[str, Any]] = None
    executor_type: str = Field("playwright", description="执行器类型: playwright 或 midscene")


class ProjectCreate(ProjectBase):
    """创建项目Schema"""
    pass


class ProjectUpdate(BaseModel):
    """更新项目Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    base_url: Optional[str] = Field(None, min_length=1, max_length=500)
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_config: Optional[Dict[str, Any]] = None
    executor_type: Optional[str] = Field(None, description="执行器类型: playwright 或 midscene")


class ProjectResponse(ProjectBase):
    """项目响应Schema"""
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    llm_api_key: str = Field("***", description="隐藏API密钥")
    
    class Config:
        from_attributes = True


class ProjectWithStatsResponse(ProjectResponse):
    """带统计数据的项目响应Schema"""
    test_case_count: int = Field(0, description="测试用例数")
    execution_count: int = Field(0, description="执行次数")
    pass_rate: float = Field(0.0, description="通过率")
