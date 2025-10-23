# URS 平台 - 详细实现方案

## 目录
1. [后端实现方案](#1-后端实现方案)
2. [前端实现方案](#2-前端实现方案)
3. [部署方案](#3-部署方案)
4. [开发计划](#4-开发计划)

---

## 1. 后端实现方案

### 1.1 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 应用入口
│   ├── api/                       # API 路由层
│   │   ├── __init__.py
│   │   ├── deps.py                # 依赖注入
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # 认证接口
│   │   │   ├── users.py           # 用户管理
│   │   │   ├── projects.py        # 项目管理
│   │   │   ├── test_cases.py      # 测试用例
│   │   │   ├── executions.py      # 测试执行
│   │   │   └── websocket.py       # WebSocket
│   ├── core/                      # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py              # 配置管理
│   │   ├── security.py            # 安全相关
│   │   └── database.py            # 数据库连接
│   ├── models/                    # ORM 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── test_case.py
│   │   └── execution.py
│   ├── schemas/                   # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── test_case.py
│   │   └── execution.py
│   ├── services/                  # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── llm_service.py         # LLM 调用服务
│   │   ├── executor_service.py    # 测试执行服务
│   │   ├── mcp_client.py          # MCP Playwright 客户端
│   │   └── artifact_service.py    # 工件管理服务
│   └── utils/                     # 工具函数
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
├── tests/                         # 测试代码
├── artifacts/                     # 工件存储目录
├── requirements.txt
├── .env.example
└── README.md
```

### 1.2 核心代码实现

#### 1.2.1 配置管理 (core/config.py)

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "URS Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "urs_db"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # 工件存储配置
    ARTIFACTS_BASE_PATH: str = "./artifacts"
    
    # MCP 配置
    MCP_SERVER_URL: str = "http://localhost:3000"
    
    # LLM 默认配置
    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_LLM_MODEL: str = "gpt-4-turbo-preview"
    DEFAULT_LLM_TEMPERATURE: float = 0.7
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### 1.2.2 数据库连接 (core/database.py)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 基类
Base = declarative_base()

# 数据库依赖
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

#### 1.2.3 用户模型 (models/user.py)

```python
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"

class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.MEMBER)
    email = Column(String(100))
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
```

#### 1.2.4 认证服务 (services/auth_service.py)

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.user import User

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """生成密码哈希"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """认证用户"""
        result = await db.execute(
            select(User).where(User.username == username, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        await db.commit()
        
        return user
```

#### 1.2.5 LLM 服务 (services/llm_service.py)

```python
from typing import Dict, List, Optional
import json
import base64
from openai import AsyncOpenAI
from langchain.prompts import PromptTemplate

class LLMService:
    
    TESTCASE_GENERATION_PROMPT = """
你是一个专业的测试用例设计专家。请根据用户提供的自然语言描述,生成一个标准化的测试用例。

测试用例应包含以下JSON结构:
{{
  "test_id": "唯一测试ID",
  "test_name": "测试用例名称",
  "preconditions": ["前置条件列表"],
  "steps": [
    {{
      "step_no": 1,
      "action": "navigate/click/input/select/verify/wait",
      "description": "步骤描述",
      "target": "目标元素CSS选择器",
      "input_value": "输入值(可选)",
      "expected": "预期结果"
    }}
  ],
  "postconditions": ["后置条件列表"]
}}

用户输入: {nl_input}
目标网站: {base_url}

请严格按照JSON格式输出,不要添加任何markdown标记或额外说明。
"""

    SCRIPT_GENERATION_PROMPT = """
你是Playwright自动化测试专家。请根据标准化测试用例,生成完整的Playwright Python脚本。

脚本要求:
1. 使用async/await语法
2. 包含完整错误处理
3. 每个步骤后添加截图
4. 使用合理的等待策略
5. 添加详细注释

测试用例:
{std_testcase}

目标网站: {base_url}

请直接输出Python代码,不要使用markdown代码块标记。
"""

    VERDICT_PROMPT = """
你是UI测试结果分析专家。根据测试执行的截图和日志,判定测试是否通过。

测试信息:
- 测试名称: {test_name}
- 预期结果: {expected_result}

执行步骤详情:
{steps_detail}

判定要求:
1. 仔细检查每个步骤的截图
2. 检查是否有错误提示或异常
3. 验证最终状态是否符合预期
4. 给出整体判定和信心度(0-1)

请严格按照以下JSON格式输出:
{{
  "overall_result": "passed" or "failed",
  "confidence": 0.95,
  "analysis": "整体分析说明",
  "step_verdicts": [
    {{
      "step_number": 1,
      "result": "passed" or "failed",
      "reason": "判定原因"
    }}
  ]
}}
"""
    
    def __init__(self, config: Dict):
        """初始化LLM服务"""
        self.provider = config.get("provider", "openai")
        self.model = config.get("model", "gpt-4-turbo-preview")
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2000)
        
        if self.provider == "openai":
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
    
    async def generate_testcase(self, nl_input: str, base_url: str) -> Dict:
        """从自然语言生成标准化测试用例"""
        
        prompt = self.TESTCASE_GENERATION_PROMPT.format(
            nl_input=nl_input,
            base_url=base_url
        )
        
        response = await self._call_llm(prompt)
        
        # 解析JSON响应
        try:
            testcase = json.loads(response)
            return testcase
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM返回的不是有效JSON: {response}")
    
    async def generate_script(self, std_testcase: Dict, base_url: str) -> str:
        """从标准化用例生成Playwright脚本"""
        
        prompt = self.SCRIPT_GENERATION_PROMPT.format(
            std_testcase=json.dumps(std_testcase, ensure_ascii=False, indent=2),
            base_url=base_url
        )
        
        script = await self._call_llm(prompt)
        return script
    
    async def judge_test_result(
        self,
        test_name: str,
        expected_result: str,
        steps: List[Dict],
        screenshots: List[str]
    ) -> Dict:
        """判定测试结果"""
        
        # 构建步骤详情
        steps_detail = ""
        for step in steps:
            steps_detail += f"\n步骤 {step['step_number']}: {step['action']}\n"
            steps_detail += f"状态: {step['status']}\n"
        
        prompt = self.VERDICT_PROMPT.format(
            test_name=test_name,
            expected_result=expected_result,
            steps_detail=steps_detail
        )
        
        # 调用支持多模态的LLM (包含截图)
        verdict_text = await self._call_llm_with_images(prompt, screenshots)
        
        # 解析判定结果
        try:
            verdict = json.loads(verdict_text)
            return verdict
        except json.JSONDecodeError:
            raise ValueError(f"LLM返回的判定结果不是有效JSON: {verdict_text}")
    
    async def _call_llm(self, prompt: str) -> str:
        """调用LLM"""
        
        if self.provider == "openai":
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        else:
            raise ValueError(f"不支持的LLM提供商: {self.provider}")
    
    async def _call_llm_with_images(self, prompt: str, image_paths: List[str]) -> str:
        """调用支持多模态的LLM (包含图片)"""
        
        if self.provider == "openai":
            # 构建消息内容
            content = [{"type": "text", "text": prompt}]
            
            # 添加图片 (base64编码)
            for image_path in image_paths:
                with open(image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode()
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_data}"
                    }
                })
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": content}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        else:
            raise ValueError(f"不支持的LLM提供商: {self.provider}")
```

#### 1.2.6 MCP Playwright 客户端 (services/mcp_client.py)

```python
import httpx
from typing import Dict, Optional

class MCPPlaywrightClient:
    """MCP Playwright 客户端封装"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session_id: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def initialize(self, browser_config: Dict):
        """初始化浏览器会话"""
        response = await self.client.post(
            f"{self.server_url}/sessions",
            json={
                "browser": browser_config.get("browser", "chromium"),
                "headless": browser_config.get("headless", True),
                "viewport": browser_config.get("viewport", {"width": 1920, "height": 1080}),
                "timeout": browser_config.get("timeout", 30000)
            }
        )
        response.raise_for_status()
        data = response.json()
        self.session_id = data["session_id"]
        return self.session_id
    
    async def navigate(self, url: str):
        """导航到URL"""
        return await self._execute_action("navigate", {"url": url})
    
    async def click(self, selector: str):
        """点击元素"""
        return await self._execute_action("click", {"selector": selector})
    
    async def fill(self, selector: str, value: str):
        """填充输入框"""
        return await self._execute_action("fill", {
            "selector": selector,
            "value": value
        })
    
    async def select(self, selector: str, value: str):
        """选择下拉框选项"""
        return await self._execute_action("select", {
            "selector": selector,
            "value": value
        })
    
    async def wait_for(self, selector: str, timeout: int = 5000):
        """等待元素"""
        return await self._execute_action("wait_for", {
            "selector": selector,
            "timeout": timeout
        })
    
    async def screenshot(self, path: str) -> str:
        """截图"""
        response = await self._execute_action("screenshot", {"path": path})
        return response.get("screenshot_path")
    
    async def save_har(self, path: str) -> str:
        """保存HAR文件"""
        response = await self._execute_action("save_har", {"path": path})
        return response.get("har_path")
    
    async def get_logs(self) -> list:
        """获取控制台日志"""
        response = await self._execute_action("get_logs", {})
        return response.get("logs", [])
    
    async def close(self):
        """关闭会话"""
        if self.session_id:
            await self.client.delete(f"{self.server_url}/sessions/{self.session_id}")
            self.session_id = None
    
    async def _execute_action(self, action: str, params: Dict) -> Dict:
        """执行动作"""
        if not self.session_id:
            raise ValueError("会话未初始化,请先调用initialize()")
        
        response = await self.client.post(
            f"{self.server_url}/sessions/{self.session_id}/actions",
            json={
                "action": action,
                "params": params
            }
        )
        response.raise_for_status()
        return response.json()
```

#### 1.2.7 测试执行服务 (services/executor_service.py)

```python
from typing import Dict, List
from pathlib import Path
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.execution import TestExecution, ExecutionStep
from app.models.test_case import TestCase
from app.services.mcp_client import MCPPlaywrightClient
from app.services.llm_service import LLMService
from app.core.config import settings

class TestExecutor:
    """测试执行器"""
    
    def __init__(
        self,
        db: AsyncSession,
        test_case_id: int,
        executor_id: int,
        browser_config: Dict = None
    ):
        self.db = db
        self.test_case_id = test_case_id
        self.executor_id = executor_id
        self.browser_config = browser_config or {}
        self.execution: Optional[TestExecution] = None
        self.artifacts_path: Optional[Path] = None
        self.mcp_client: Optional[MCPPlaywrightClient] = None
        
    async def execute(self) -> TestExecution:
        """执行测试"""
        
        try:
            # 1. 加载测试用例
            test_case = await self._load_test_case()
            
            # 2. 创建执行记录
            self.execution = await self._create_execution_record(test_case)
            
            # 3. 准备工件存储目录
            self.artifacts_path = self._prepare_artifacts_dir()
            
            # 4. 更新状态为running
            await self._update_execution_status("running")
            
            # 5. 初始化MCP客户端
            self.mcp_client = MCPPlaywrightClient(settings.MCP_SERVER_URL)
            await self.mcp_client.initialize(self.browser_config)
            
            # 6. 解析测试步骤
            steps = test_case.std_testcase.get("steps", [])
            
            # 7. 逐步执行
            for step in steps:
                await self._execute_step(step)
            
            # 8. 收集所有截图
            screenshots = self._collect_screenshots()
            
            # 9. LLM判定结果
            llm_service = LLMService(test_case.project.llm_config)
            verdict = await llm_service.judge_test_result(
                test_name=test_case.name,
                expected_result=test_case.expected_result or "",
                steps=[{
                    "step_number": s.step_number,
                    "action": s.action,
                    "status": s.status
                } for s in self.execution.steps],
                screenshots=screenshots
            )
            
            # 10. 更新最终状态
            final_status = verdict["overall_result"]
            await self._update_execution_status(
                final_status,
                llm_verdict=verdict
            )
            
            return self.execution
            
        except Exception as e:
            await self._handle_error(str(e))
            raise
            
        finally:
            if self.mcp_client:
                await self.mcp_client.close()
    
    async def _execute_step(self, step_def: Dict):
        """执行单个测试步骤"""
        
        # 创建步骤记录
        step_record = await self._create_step_record(step_def)
        
        try:
            # 更新为running
            step_record.status = "running"
            await self.db.commit()
            
            # 根据action类型执行
            action = step_def["action"]
            target = step_def.get("target", "")
            
            if action == "navigate":
                await self.mcp_client.navigate(target)
            elif action == "click":
                await self.mcp_client.click(target)
            elif action == "input":
                input_value = step_def.get("input_value", "")
                await self.mcp_client.fill(target, input_value)
            elif action == "select":
                value = step_def.get("input_value", "")
                await self.mcp_client.select(target, value)
            elif action == "wait":
                timeout = step_def.get("timeout", 5000)
                await self.mcp_client.wait_for(target, timeout)
            
            # 执行后截图
            screenshot_filename = f"step_{step_record.step_number}_screenshot.png"
            screenshot_path = str(self.artifacts_path / screenshot_filename)
            await self.mcp_client.screenshot(screenshot_path)
            step_record.screenshot_path = screenshot_path
            
            # 保存HAR
            har_filename = f"step_{step_record.step_number}.har"
            har_path = str(self.artifacts_path / har_filename)
            await self.mcp_client.save_har(har_path)
            step_record.har_path = har_path
            
            # 获取日志
            logs = await self.mcp_client.get_logs()
            step_record.log_content = json.dumps(logs, ensure_ascii=False)
            
            # 更新为success
            step_record.status = "success"
            await self.db.commit()
            
        except Exception as e:
            # 错误截图
            error_screenshot = str(self.artifacts_path / f"step_{step_record.step_number}_error.png")
            try:
                await self.mcp_client.screenshot(error_screenshot)
                step_record.screenshot_path = error_screenshot
            except:
                pass
            
            step_record.status = "failed"
            step_record.error_message = str(e)
            await self.db.commit()
            
            raise
    
    async def _load_test_case(self) -> TestCase:
        """加载测试用例"""
        result = await self.db.execute(
            select(TestCase).where(TestCase.id == self.test_case_id)
        )
        test_case = result.scalar_one_or_none()
        if not test_case:
            raise ValueError(f"测试用例不存在: {self.test_case_id}")
        return test_case
    
    async def _create_execution_record(self, test_case: TestCase) -> TestExecution:
        """创建执行记录"""
        
        # 获取执行序号
        result = await self.db.execute(
            select(TestExecution)
            .where(TestExecution.test_case_id == self.test_case_id)
            .order_by(TestExecution.execution_number.desc())
            .limit(1)
        )
        last_execution = result.scalar_one_or_none()
        next_number = (last_execution.execution_number + 1) if last_execution else 1
        
        execution = TestExecution(
            test_case_id=self.test_case_id,
            execution_number=next_number,
            status="pending",
            executor_id=self.executor_id,
            start_time=datetime.utcnow()
        )
        
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        
        return execution
    
    async def _create_step_record(self, step_def: Dict) -> ExecutionStep:
        """创建步骤记录"""
        step = ExecutionStep(
            execution_id=self.execution.id,
            step_number=step_def["step_no"],
            action=step_def["description"],
            status="pending"
        )
        
        self.db.add(step)
        await self.db.commit()
        await self.db.refresh(step)
        
        return step
    
    def _prepare_artifacts_dir(self) -> Path:
        """准备工件存储目录"""
        artifacts_path = Path(settings.ARTIFACTS_BASE_PATH) / "executions" / str(self.execution.id)
        artifacts_path.mkdir(parents=True, exist_ok=True)
        
        # 更新执行记录的artifacts_path
        self.execution.artifacts_path = str(artifacts_path)
        
        return artifacts_path
    
    async def _update_execution_status(
        self,
        status: str,
        llm_verdict: Dict = None
    ):
        """更新执行状态"""
        self.execution.status = status
        
        if status in ["passed", "failed", "error", "cancelled"]:
            self.execution.end_time = datetime.utcnow()
            if self.execution.start_time:
                duration = (self.execution.end_time - self.execution.start_time).total_seconds()
                self.execution.duration = int(duration)
        
        if llm_verdict:
            self.execution.llm_verdict = llm_verdict
        
        await self.db.commit()
    
    def _collect_screenshots(self) -> List[str]:
        """收集所有截图路径"""
        screenshots = []
        for step in self.execution.steps:
            if step.screenshot_path and Path(step.screenshot_path).exists():
                screenshots.append(step.screenshot_path)
        return screenshots
    
    async def _handle_error(self, error_message: str):
        """处理执行错误"""
        if self.execution:
            self.execution.status = "error"
            self.execution.error_message = error_message
            self.execution.end_time = datetime.utcnow()
            await self.db.commit()
```

#### 1.2.8 API 路由示例 (api/v1/test_cases.py)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.test_case import TestCase
from app.models.project import Project
from app.schemas.test_case import TestCaseCreate, TestCaseResponse
from app.services.llm_service import LLMService

router = APIRouter()

@router.post("/projects/{project_id}/test-cases", response_model=TestCaseResponse)
async def create_test_case(
    project_id: int,
    test_case_in: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建测试用例"""
    
    # 1. 检查项目是否存在
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 2. 使用LLM生成标准化用例
    llm_service = LLMService(project.llm_config)
    std_testcase = await llm_service.generate_testcase(
        nl_input=test_case_in.nl_input,
        base_url=project.base_url
    )
    
    # 3. 生成Playwright脚本
    script = await llm_service.generate_script(
        std_testcase=std_testcase,
        base_url=project.base_url
    )
    
    # 4. 创建测试用例记录
    test_case = TestCase(
        project_id=project_id,
        name=test_case_in.name,
        nl_input=test_case_in.nl_input,
        std_testcase=std_testcase,
        script=script,
        expected_result=test_case_in.expected_result,
        priority=test_case_in.priority,
        tags=test_case_in.tags,
        created_by=current_user.id,
        status="draft"
    )
    
    db.add(test_case)
    await db.commit()
    await db.refresh(test_case)
    
    return test_case

@router.post("/test-cases/{case_id}/execute")
async def execute_test_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """执行测试用例"""
    
    from app.services.executor_service import TestExecutor
    
    # 创建执行器
    executor = TestExecutor(
        db=db,
        test_case_id=case_id,
        executor_id=current_user.id
    )
    
    # 异步执行(实际应该放到后台任务)
    execution = await executor.execute()
    
    return {
        "code": 0,
        "message": "执行完成",
        "data": {
            "execution_id": execution.id,
            "status": execution.status
        }
    }
```

### 1.3 依赖项 (requirements.txt)

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
aiomysql==0.2.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
celery==5.3.4
redis==5.0.1
python-socketio==5.10.0
httpx==0.25.2
openai==1.3.7
langchain==0.1.0
loguru==0.7.2
```

---

## 2. 前端实现方案

### 2.1 项目结构

```
frontend/
├── public/
├── src/
│   ├── main.ts                    # 应用入口
│   ├── App.vue                    # 根组件
│   ├── router/                    # 路由配置
│   │   └── index.ts
│   ├── stores/                    # Pinia状态管理
│   │   ├── auth.ts
│   │   ├── project.ts
│   │   └── execution.ts
│   ├── api/                       # API调用
│   │   ├── request.ts             # axios配置
│   │   ├── auth.ts
│   │   ├── project.ts
│   │   ├── testCase.ts
│   │   └── execution.ts
│   ├── views/                     # 页面组件
│   │   ├── Login.vue
│   │   ├── Dashboard.vue
│   │   ├── ProjectList.vue
│   │   ├── TestCaseList.vue
│   │   ├── TestCaseEditor.vue
│   │   ├── ExecutionDetail.vue
│   │   └── UserManagement.vue
│   ├── components/                # 通用组件
│   │   ├── Layout/
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppSidebar.vue
│   │   │   └── AppLayout.vue
│   │   ├── TestCase/
│   │   │   ├── NLInputForm.vue
│   │   │   ├── TestCaseViewer.vue
│   │   │   └── ScriptEditor.vue
│   │   └── Execution/
│   │       ├── StepList.vue
│   │       ├── ScreenshotViewer.vue
│   │       └── ExecutionStatus.vue
│   ├── types/                     # TypeScript类型定义
│   │   └── index.ts
│   └── utils/                     # 工具函数
│       ├── websocket.ts
│       └── helpers.ts
├── package.json
├── vite.config.ts
└── tsconfig.json
```

### 2.2 核心代码示例

#### 2.2.1 API请求配置 (api/request.ts)

```typescript
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 60000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 0) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res.data
  },
  error => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default request
```

#### 2.2.2 测试用例API (api/testCase.ts)

```typescript
import request from './request'

export interface TestCaseCreate {
  name: string
  nl_input: string
  expected_result?: string
  priority?: string
  tags?: string[]
}

export interface TestCase {
  id: number
  project_id: number
  name: string
  nl_input: string
  std_testcase: any
  script: string
  status: string
  created_at: string
}

export const testCaseApi = {
  // 创建测试用例
  create(projectId: number, data: TestCaseCreate) {
    return request.post<TestCase>(`/projects/${projectId}/test-cases`, data)
  },
  
  // 获取用例列表
  list(projectId: number, params?: any) {
    return request.get(`/projects/${projectId}/test-cases`, { params })
  },
  
  // 获取用例详情
  get(caseId: number) {
    return request.get<TestCase>(`/test-cases/${caseId}`)
  },
  
  // 执行用例
  execute(caseId: number) {
    return request.post(`/test-cases/${caseId}/execute`)
  }
}
```

#### 2.2.3 测试用例编辑器组件 (views/TestCaseEditor.vue)

```vue
<template>
  <div class="test-case-editor">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>创建测试用例</span>
        </div>
      </template>
      
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入用例名称" />
        </el-form-item>
        
        <el-form-item label="自然语言描述" prop="nl_input">
          <el-input
            v-model="form.nl_input"
            type="textarea"
            :rows="6"
            placeholder="例如: 打开登录页面,输入用户名admin,输入密码admin,点击登录按钮,验证是否跳转到首页"
          />
        </el-form-item>
        
        <el-form-item label="预期结果" prop="expected_result">
          <el-input v-model="form.expected_result" type="textarea" :rows="3" />
        </el-form-item>
        
        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="form.priority">
            <el-radio label="low">低</el-radio>
            <el-radio label="medium">中</el-radio>
            <el-radio label="high">高</el-radio>
            <el-radio label="critical">紧急</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submitForm">
            生成测试用例
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 生成的用例预览 -->
    <el-card v-if="generatedCase" class="mt-4">
      <template #header>
        <div class="card-header">
          <span>生成的标准化测试用例</span>
          <el-button type="primary" size="small" @click="executeCase">
            执行测试
          </el-button>
        </div>
      </template>
      
      <el-tabs>
        <el-tab-pane label="测试步骤">
          <el-table :data="generatedCase.std_testcase.steps" border>
            <el-table-column prop="step_no" label="步骤" width="80" />
            <el-table-column prop="action" label="操作" width="120" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="target" label="目标元素" />
            <el-table-column prop="expected" label="预期结果" />
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="Playwright脚本">
          <MonacoEditor
            v-model="generatedCase.script"
            language="python"
            :readonly="true"
            height="400px"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { testCaseApi } from '@/api/testCase'
import MonacoEditor from '@/components/MonacoEditor.vue'

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.projectId)

const formRef = ref()
const loading = ref(false)
const generatedCase = ref(null)

const form = reactive({
  name: '',
  nl_input: '',
  expected_result: '',
  priority: 'medium'
})

const rules = {
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  nl_input: [{ required: true, message: '请输入自然语言描述', trigger: 'blur' }]
}

const submitForm = async () => {
  await formRef.value.validate()
  
  loading.value = true
  try {
    const result = await testCaseApi.create(projectId, form)
    generatedCase.value = result
    ElMessage.success('测试用例生成成功')
  } catch (error) {
    console.error('生成失败:', error)
  } finally {
    loading.value = false
  }
}

const executeCase = async () => {
  try {
    const result = await testCaseApi.execute(generatedCase.value.id)
    ElMessage.success('测试开始执行')
    router.push(`/executions/${result.execution_id}`)
  } catch (error) {
    console.error('执行失败:', error)
  }
}

const resetForm = () => {
  formRef.value.resetFields()
  generatedCase.value = null
}
</script>
```

---

## 3. 部署方案

### 3.1 Docker Compose 部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: urs_mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: urs_db
      MYSQL_USER: urs_user
      MYSQL_PASSWORD: urs_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - urs_network

  redis:
    image: redis:7-alpine
    container_name: urs_redis
    ports:
      - "6379:6379"
    networks:
      - urs_network

  backend:
    build: ./backend
    container_name: urs_backend
    environment:
      MYSQL_HOST: mysql
      MYSQL_PORT: 3306
      MYSQL_USER: urs_user
      MYSQL_PASSWORD: urs_password
      MYSQL_DATABASE: urs_db
      REDIS_HOST: redis
      REDIS_PORT: 6379
    ports:
      - "8000:8000"
    depends_on:
      - mysql
      - redis
    volumes:
      - ./artifacts:/app/artifacts
    networks:
      - urs_network

  frontend:
    build: ./frontend
    container_name: urs_frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - urs_network

volumes:
  mysql_data:

networks:
  urs_network:
    driver: bridge
```

### 3.2 环境变量配置

```bash
# backend/.env
APP_NAME=URS Platform
DEBUG=False

MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=urs_user
MYSQL_PASSWORD=urs_password
MYSQL_DATABASE=urs_db

SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60

REDIS_HOST=redis
REDIS_PORT=6379

MCP_SERVER_URL=http://localhost:3000
ARTIFACTS_BASE_PATH=./artifacts
```

---

## 4. 开发计划

### 阶段1: 基础框架搭建 (2周)
- 数据库设计与初始化
- 后端基础框架搭建
- 前端基础框架搭建
- 用户认证系统

### 阶段2: 核心功能开发 (4周)
- 项目管理功能
- LLM集成与测试用例生成
- Playwright脚本生成
- MCP客户端集成

### 阶段3: 测试执行引擎 (3周)
- 测试执行流程开发
- 实时通信(WebSocket)
- 工件存储管理
- LLM结果判定

### 阶段4: 前端完善 (2周)
- 测试用例编辑器
- 执行结果展示
- 截图查看器
- 数据可视化

### 阶段5: 测试与优化 (2周)
- 系统测试
- 性能优化
- Bug修复
- 文档编写

**总计: 13周**
