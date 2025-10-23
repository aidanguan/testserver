"""
配置管理模块
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "ui_test_platform"
    
    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    
    # 服务器配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # 工件存储路径
    ARTIFACTS_PATH: str = "../artifacts"
    
    # 执行配置
    MAX_EXECUTION_TIME: int = 300  # 5分钟
    
    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
