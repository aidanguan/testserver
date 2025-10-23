# API端点

<cite>
**本文档中引用的文件**   
- [main.py](file://backend/main.py)
- [auth.py](file://backend/app/api/endpoints/auth.py)
- [users.py](file://backend/app/api/endpoints/users.py)
- [projects.py](file://backend/app/api/endpoints/projects.py)
- [test_cases.py](file://backend/app/api/endpoints/test_cases.py)
- [test_runs.py](file://backend/app/api/endpoints/test_runs.py)
- [dependencies.py](file://backend/app/api/dependencies.py)
- [user.py](file://backend/app/schemas/user.py)
- [project.py](file://backend/app/schemas/project.py)
- [test_case.py](file://backend/app/schemas/test_case.py)
- [test_run.py](file://backend/app/schemas/test_run.py)
</cite>

## 目录
1. [简介](#简介)
2. [项目结构与路由注册](#项目结构与路由注册)
3. [CORS策略配置](#cors策略配置)
4. [认证端点 (/auth)](#认证端点-auth)
5. [用户管理端点 (/users)](#用户管理端点-users)
6. [项目管理端点 (/projects)](#项目管理端点-projects)
7. [测试用例管理端点 (/test-cases)](#测试用例管理端点-test-cases)
8. [测试执行端点 (/test-runs)](#测试执行端点-test-runs)
9. [健康检查端点 (/health)](#健康检查端点-health)
10. [安全机制与依赖注入](#安全机制与依赖注入)
11. [输入验证与Pydantic模型](#输入验证与pydantic模型)
12. [错误处理模式](#错误处理模式)
13. [请求/响应示例](#请求响应示例)

## 简介
本API文档详细描述了“自然语言驱动UI测试平台”的后端RESTful接口设计。系统基于FastAPI构建，提供完整的用户认证、权限控制、项目管理、测试用例生成与执行功能。所有API端点均通过JWT进行身份验证，并采用Pydantic模型进行请求数据验证。文档涵盖各模块的HTTP方法、路径、参数、请求体结构、响应格式及状态码，并说明核心安全机制与错误处理策略。

## 项目结构与路由注册
系统采用模块化设计，各功能模块的API路由定义在`backend/app/api/endpoints/`目录下。主应用`main.py`通过`include_router`方法将各模块的路由器注册到应用中，并统一添加`/api`前缀。

```mermaid
graph TD
A[main.py] --> B[auth.router]
A --> C[users.router]
A --> D[projects.router]
A --> E[test_cases.router]
A --> F[test_runs.router]
B --> G[/api/auth]
C --> H[/api/users]
D --> I[/api/projects]
E --> J[/api/projects/{project_id}/cases]
F --> K[/api/cases/{case_id}/execute]
```

**图示来源**
- [main.py](file://backend/main.py#L1-L56)

**本节来源**
- [main.py](file://backend/main.py#L1-L56)

## CORS策略配置
为支持前端跨域请求，系统在`main.py`中配置了CORS中间件。允许的源、方法和头部均通过`app.config.settings`进行管理，确保配置集中化和环境适应性。

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

该配置允许所有HTTP方法和头部，支持凭据（如JWT Cookie），并从配置文件动态加载允许的源列表，保障了前后端分离架构下的安全通信。

**本节来源**
- [main.py](file://backend/main.py#L1-L56)

## 认证端点 /auth
认证模块提供用户登录、登出和获取当前用户信息的功能，所有端点均位于`/api/auth`路径下。

### 登录 (/login)
- **HTTP方法**: `POST`
- **URL路径**: `/api/auth/login`
- **请求体**: `UserLogin` 模型（包含`username`和`password`）
- **响应**: `Token` 模型（包含`access_token`、`token_type`和`user`信息）
- **成功状态码**: `200 OK`
- **错误状态码**:
  - `401 Unauthorized`: 用户名或密码错误
  - `403 Forbidden`: 用户被禁用

### 登出 (/logout)
- **HTTP方法**: `POST`
- **URL路径**: `/api/auth/logout`
- **认证**: 需要有效的JWT Bearer Token
- **响应**: `{ "message": "登出成功" }`
- **状态码**: `200 OK`
- **说明**: JWT为无状态令牌，登出操作由客户端负责清除本地存储的Token。

### 获取当前用户信息 (/current)
- **HTTP方法**: `GET`
- **URL路径**: `/api/auth/current`
- **认证**: 需要有效的JWT Bearer Token
- **响应**: `UserResponse` 模型
- **状态码**: `200 OK`

**本节来源**
- [auth.py](file://backend/app/api/endpoints/auth.py#L1-L55)
- [user.py](file://backend/app/schemas/user.py#L1-L49)

## 用户管理端点 /users
用户管理模块提供用户列表、创建、读取、更新和删除（CRUD）功能，仅管理员可访问，路径为`/api/users`。

### 获取用户列表 (GET /)
- **响应**: `List[UserResponse]`
- **权限**: 管理员

### 创建用户 (POST /)
- **请求体**: `UserCreate` 模型
- **响应**: `UserResponse`
- **状态码**: `201 Created`
- **验证**: 检查用户名是否已存在

### 获取用户详情 (GET /{user_id})
- **响应**: `UserResponse`
- **错误**: `404 Not Found`（用户不存在）

### 更新用户 (PUT /{user_id})
- **请求体**: `UserUpdate` 模型（可选字段）
- **响应**: `UserResponse`
- **特殊逻辑**: 管理员不能删除自己

### 删除用户 (DELETE /{user_id})
- **响应**: 无内容
- **状态码**: `204 No Content`
- **权限**: 管理员，且不能删除自己

**本节来源**
- [users.py](file://backend/app/api/endpoints/users.py#L1-L123)
- [user.py](file://backend/app/schemas/user.py#L1-L49)

## 项目管理端点 /projects
项目管理模块提供项目CRUD操作，路径为`/api/projects`。

### 获取项目列表 (GET /)
- **响应**: `List[ProjectResponse]`
- **权限**: 所有登录用户

### 创建项目 (POST /)
- **请求体**: `ProjectCreate` 模型
- **响应**: `ProjectResponse`
- **状态码**: `201 Created`
- **安全**: `llm_api_key`在存储前会被加密

### 获取项目详情 (GET /{project_id})
- **响应**: `ProjectResponse`
- **错误**: `404 Not Found`

### 更新项目 (PUT /{project_id})
- **请求体**: `ProjectUpdate` 模型
- **响应**: `ProjectResponse`
- **验证**: 检查项目名是否冲突

### 删除项目 (DELETE /{project_id})
- **响应**: 无内容
- **状态码**: `204 No Content`
- **级联**: 删除项目会同时删除其所有测试用例

**本节来源**
- [projects.py](file://backend/app/api/endpoints/projects.py#L1-L142)
- [project.py](file://backend/app/schemas/project.py#L1-L52)

## 测试用例管理端点 /test-cases
测试用例管理模块提供测试用例的CRUD及AI生成功能，路径基于项目ID，如`/api/projects/{project_id}/cases`。

### 获取项目测试用例列表 (GET /projects/{project_id}/cases)
- **响应**: `List[TestCaseResponse]`

### 创建测试用例 (POST /projects/{project_id}/cases)
- **请求体**: `TestCaseCreate` 模型
- **验证**: `project_id`必须匹配路径参数

### 获取测试用例详情 (GET /cases/{case_id})
- **响应**: `TestCaseResponse`

### 更新测试用例 (PUT /cases/{case_id})
- **请求体**: `TestCaseUpdate` 模型

### 删除测试用例 (DELETE /cases/{case_id})
- **权限**: 管理员或创建者本人

### 从自然语言生成测试用例 (POST /cases/generate-from-nl)
- **请求体**: `NaturalLanguageRequest`（包含`project_id`和`natural_language`）
- **响应**: `StandardCaseResponse`（标准化步骤）
- **流程**: 调用LLM服务，根据项目配置生成用例

### 生成Playwright脚本 (POST /cases/generate-script)
- **请求体**: `ScriptGenerationRequest`（包含`test_case_id`）
- **响应**: `ScriptGenerationResponse`（包含`playwright_script`）
- **流程**: 调用LLM服务，将标准化步骤转换为Playwright代码

**本节来源**
- [test_cases.py](file://backend/app/api/endpoints/test_cases.py#L1-L246)
- [test_case.py](file://backend/app/schemas/test_case.py#L1-L89)

## 测试执行端点 /test-runs
测试执行模块提供测试用例的执行和结果查询功能，路径为`/api/cases/{case_id}/execute`。

### 执行测试用例 (POST /cases/{case_id}/execute)
- **响应**: `TestRunResponse`（包含运行ID和初始状态）
- **异步**: 使用`BackgroundTasks`在后台执行，立即返回运行记录
- **流程**: 启动Playwright执行器运行脚本，并调用LLM进行结果判定

### 获取测试运行详情 (GET /runs/{run_id})
- **响应**: `TestRunDetailResponse`（包含步骤详情和测试用例信息）

### 获取运行记录列表 (GET /runs)
- **查询参数**: `project_id`, `case_id`, `limit`
- **响应**: `List[TestRunResponse]`

### 获取运行步骤记录 (GET /runs/{run_id}/steps)
- **响应**: `List[StepExecutionResponse]`

**本节来源**
- [test_runs.py](file://backend/app/api/endpoints/test_runs.py#L1-L259)
- [test_run.py](file://backend/app/schemas/test_run.py#L1-L53)

## 健康检查端点 /health
- **HTTP方法**: `GET`
- **URL路径**: `/health`
- **响应**: `{ "status": "healthy" }`
- **状态码**: `200 OK`
- **用途**: 用于Kubernetes、Docker等容器编排系统的存活探针（liveness probe）和就绪探针（readiness probe），确保服务正常运行。

**本节来源**
- [main.py](file://backend/main.py#L1-L56)

## 安全机制与依赖注入
系统采用依赖注入（Dependency Injection）实现安全控制，核心函数位于`dependencies.py`。

### 当前用户获取
- **函数**: `get_current_user`
- **依赖**: `HTTPBearer`安全方案和数据库会话
- **流程**:
  1. 从请求头提取JWT Token
  2. 解码并验证Token有效性
  3. 查询数据库获取用户信息
  4. 检查用户是否存在且处于激活状态
- **错误处理**: 返回`401 Unauthorized`或`403 Forbidden`

### 管理员权限检查
- **函数**: `get_current_admin_user`
- **逻辑**: 在`get_current_user`基础上，额外检查用户角色是否为`ADMIN`。

**本节来源**
- [dependencies.py](file://backend/app/api/dependencies.py#L14-L51)
- [auth.py](file://backend/app/api/endpoints/auth.py#L1-L55)

## 输入验证与Pydantic模型
所有API端点均使用Pydantic模型进行输入验证和响应序列化。

### 核心模型
- **UserCreate**: 验证用户名长度（3-50）、密码长度（≥8）
- **ProjectCreate**: 验证项目名、基础URL、LLM配置
- **TestCaseCreate**: 验证自然语言描述和预期结果非空
- **LLMConfig**: 验证`temperature`、`max_tokens`等数值范围

### 验证机制
FastAPI自动对请求体进行验证，若数据不符合模型定义，将返回`422 Unprocessable Entity`错误，包含详细的验证失败信息。

**本节来源**
- [user.py](file://backend/app/schemas/user.py#L1-L49)
- [project.py](file://backend/app/schemas/project.py#L1-L52)
- [test_case.py](file://backend/app/schemas/test_case.py#L1-L89)

## 错误处理模式
系统采用统一的HTTP异常处理模式，确保客户端能获得清晰的错误信息。

### 常见错误码
- `400 Bad Request`: 请求参数错误（如用户名已存在）
- `401 Unauthorized`: 认证失败（Token无效或缺失）
- `403 Forbidden`: 权限不足（非管理员尝试操作）
- `404 Not Found`: 资源不存在（用户、项目、用例等）
- `422 Unprocessable Entity`: 请求体验证失败
- `500 Internal Server Error`: 服务器内部错误（如LLM调用失败）

### 错误响应结构
```json
{
  "detail": "错误描述信息"
}
```
对于`401`错误，还会包含`WWW-Authenticate`头，提示客户端使用Bearer Token。

**本节来源**
- [auth.py](file://backend/app/api/endpoints/auth.py#L1-L55)
- [users.py](file://backend/app/api/endpoints/users.py#L1-L123)

## 请求/响应示例
### 登录请求
```http
POST /api/auth/login HTTP/1.1
Content-Type: application/json

{
  "username": "admin",
  "password": "secret123"
}
```

### 登录响应
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "Admin",
    "is_active": true,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 带JWT的请求
```http
GET /api/users HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx
```

**本节来源**
- [auth.py](file://backend/app/api/endpoints/auth.py#L1-L55)
- [users.py](file://backend/app/api/endpoints/users.py#L1-L123)