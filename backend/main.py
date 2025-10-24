"""
FastAPI主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.config import settings
from app.api.endpoints import auth, users, projects, test_cases, test_runs, recorder, auth_states

# 创建FastAPI应用
app = FastAPI(
    title="自然语言驱动UI测试平台",
    description="基于Web的自然语言驱动UI测试平台API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(test_cases.router, prefix="/api")
app.include_router(test_runs.router, prefix="/api")
app.include_router(recorder.router, prefix="/api")
app.include_router(auth_states.router, prefix="/api")  # 认证状态管理

# 配置静态文件服务 - 提供测试工件访问
# artifacts目录在backend目录下
artifacts_path = os.path.join(os.path.dirname(__file__), "artifacts")
os.makedirs(artifacts_path, exist_ok=True)
app.mount("/artifacts", StaticFiles(directory=artifacts_path), name="artifacts")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "自然语言驱动UI测试平台",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
