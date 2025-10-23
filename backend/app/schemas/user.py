"""
用户相关的Schema
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    """用户基础Schema"""
    username: str = Field(..., min_length=3, max_length=50)
    role: UserRole


class UserCreate(UserBase):
    """创建用户Schema"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """更新用户Schema"""
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """用户响应Schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录Schema"""
    username: str
    password: str


class Token(BaseModel):
    """Token响应Schema"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
