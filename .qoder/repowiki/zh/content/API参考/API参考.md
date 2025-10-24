# API参考

<cite>
**本文档中引用的文件**   
- [auth.py](file://backend/app/api/endpoints/auth.py)
- [projects.py](file://backend/app/api/endpoints/projects.py)
- [test_cases.py](file://backend/app/api/endpoints/test_cases.py)
- [test_runs.py](file://backend/app/api/endpoints/test_runs.py)
- [users.py](file://backend/app/api/endpoints/users.py)
- [user.py](file://backend/app/schemas/user.py)
- [project.py](file://backend/app/schemas/project.py)
- [test_case.py](file://backend/app/schemas/test_case.py)
- [test_run.py](file://backend/app/schemas/test_run.py)
</cite>

## 更新摘要
**已更新内容**
- 更新了**项目管理API (/projects)** 和 **测试用例API (/test-cases)** 的响应体结构，以反映新增的统计字段
- 为 `/projects` 和 `/projects/{project_id}/cases` 端点添加了详细的响应体示例
- 更新了受影响的章节来源，以包含最新的文件和行号信息

## 目录
1. [简介](#简介)
2. [认证API (/auth)](#认证api-auth)
3. [用户管理API (/users)](#用户管理api-users)
4. [项目管理API (/projects)](#项目管理api-projects)
5. [测试用例API (/test-cases)](#测试用例api-test-cases)
6. [测试执行API (/test-runs)](#测试执行api-test-runs)
7. [错误处理策略](#错误处理策略)

## 简介
本API参考文档详细描述了testserver平台的RESTful接口。平台采用JWT认证机制，所有需要认证的API请求必须在HTTP头中包含`Authorization: Bearer <token>`。API基础URL为`http://localhost:8000/api`。系统实现了基于角色的访问控制（RBAC），主要角色包括管理员（Admin）和成员（Member），不同角色具有不同的操作权限。

## 认证API (/auth)

### POST /auth/login - 用户登录
**功能说明**  
用户登录接口，验证用户名和密码后返回JWT访问令牌和用户信息。

**请求头**  
- `Content-Type: application/json`

**请求体 (JSON Schema: UserLogin)**  
```json
{
  "username": "string",
  "password": "string"
}
```

**响应体 (200 OK)**  
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": 0,
    "username": "string",
    "role": "Admin|Member",
    "is_active": true,
    "created_at": "string",
    "updated_at": "string"
  }
}
```

**HTTP状态码**  
- `200`: 登录成功
- `401`: 用户名或密码错误
- `403`: 用户已被禁用

**curl示例**  
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }'
```

**Section sources**
- [auth.py](file://backend/app/api/endpoints/auth.py#L15-L35)
- [user.py](file://backend/app/schemas/user.py#L35-L49)

### GET /auth/current - 获取当前用户信息
**功能说明**  
获取当前已认证用户的信息。

**请求头**  
- `Authorization: Bearer <token>`

**响应体 (200 OK)**  
```json
{
  "id": 0,
  "username": "string",
  "role": "Admin|Member",
  "is_active": true,
  "created_at": "string",
  "updated_at": "string"
}
```

**HTTP状态码**  
- `200`: 获取成功
- `401`: 未授权，令牌无效或过期

**curl示例**  
```bash
curl -X GET http://localhost:8000/api/auth/current \
  -H "Authorization: Bearer <your_token>"
```

**Section sources**
- [auth.py](file://backend/app/api/endpoints/auth.py#L50-L55)

## 用户管理API (/users)

### GET /users - 获取用户列表
**功能说明**  
获取所有用户列表。仅管理员可访问。

**请求头**  
- `Authorization: Bearer <token>`

**响应体 (200 OK)**  
```json
[
  {
    "id": 0,
    "username": "string",
    "role": "Admin|Member",
    "is_active": true,
    "created_at": "string",
    "updated_at": "string"
  }
]
```

**HTTP状态码**  
- `200`: 获取成功
- `401`: 未授权
- `403`: 无权限

**Section sources**
- [users.py](file://backend/app/api/endpoints/users.py#L15-L25)

### POST /users - 创建用户
**功能说明**  
创建新用户。仅管理员可操作。

**请求头**  
- `Authorization: Bearer <token>`
- `Content-Type: application/json`

**请求体 (JSON Schema: UserCreate)**  
```json
{
  "username": "string",
  "password": "string",
  "role": "Admin|Member"
}
```

**响应体 (201 Created)**  
```json
{
  "id": 0,
  "username": "string",
  "role": "Admin|Member",
  "is_active": true,
  "created_at": "string",
  "updated_at": "string"
}
```

**HTTP状态码**  
- `201`: 创建成功
- `400`: 用户名已存在
- `401`: 未授权
- `403`: 无权限

**Section sources**
- [users.py](file://backend/app/api/endpoints/users.py#L30-L50)
- [user.py](file://backend/app/schemas/user.py#L20-L24)

### GET /users/{user_id} - 获取用户详情
**功能说明**  
根据ID获取用户详情。仅管理员可访问。

**HTTP状态码**  
- `200`: 获取成功
- `404`: 用户不存在
- `401`: 未授权
- `403`: 无权限

**Section sources**
- [users.py](file://backend/app/api/endpoints/users.py#L55-L65)

### PUT /users/{user_id} - 更新用户
**功能说明**  
更新用户信息（密码、角色、状态）。仅管理员可操作。

**请求体 (JSON Schema: UserUpdate)**  
```json
{
  "password": "string",
  "role": "Admin|Member",
  "is_active": true
}
```

**HTTP状态码**  
- `200`: 更新成功
- `404`: 用户不存在
- `401`: 未授权
- `403`: 无权限

**Section sources**
- [users.py](file://backend/app/api/endpoints/users.py#L70-L90)
- [user.py](file://backend/app/schemas/user.py#L25-L29)

### DELETE /users/{user_id} - 删除用户
**功能说明**  
删除指定用户。仅管理员可操作，且不能删除自己。

**HTTP状态码**  
- `204`: 删除成功
- `404`: 用户不存在
- `400`: 不能删除自己
- `401`: 未授权
- `403`: 无权限

**Section sources**
- [users.py](file://backend/app/api/endpoints/users.py#L95-L115)

## 项目管理API (/projects)

### GET /projects - 获取项目列表
**功能说明**  
获取所有项目列表，并包含每个项目的统计数据，如测试用例数量、执行次数和通过率。

**请求头**  
- `Authorization: Bearer <token>`

**响应体 (200 OK)**  
```json
[
  {
    "id": 0,
    "name": "string",
    "description": "string",
    "base_url": "string",
    "llm_provider": "string",
    "llm_model": "string",
    "llm_api_key": "***",
    "llm_config": {},
    "llm_base_url": "string",
    "created_by": 0,
    "created_at": "string",
    "updated_at": "string",
    "test_case_count": 0,
    "execution_count": 0,
    "pass_rate": 0.0
  }
]
```

**HTTP状态码**  
- `200`: 获取成功
- `401`: 未授权

**Section sources**
- [projects.py](file://backend/app/api/endpoints/projects.py#L15-L40)
- [project.py](file://backend/app/schemas/project.py#L56-L60)

### POST /projects - 创建项目
**功能说明**  
创建新项目。仅管理员可操作。

**请求体 (JSON Schema: ProjectCreate)**  
```json
{
  "name": "string",
  "description": "string",
  "base_url": "string",
  "llm_provider": "string",
  "llm_model": "string",
  "llm_api_key": "string",
  "llm_config": {}
}
```

**响应体 (201 Created)**  
```json
{
  "id": 0,
  "name": "string",
  "description": "string",
  "base_url": "string",
  "llm_provider": "string",
  "llm_model": "string",
  "llm_api_key": "***",
  "llm_config": {},
  "created_by": 0,
  "created_at": "string",
  "updated_at": "string"
}
```

**HTTP状态码**  
- `201`: 创建成功
- `400`: 项目名已存在
- `401`: 未授权
- `403`: 无权限

**Section sources**
- [projects.py](file://backend/app/api/endpoints/projects.py#L45-L85)
- [project.py](file://backend/app/schemas/project.py#L15-L25)

### GET /projects/{project_id} - 获取项目详情
**功能说明**  
根据ID获取项目详情。

**HTTP状态码**  
- `200`: 获取成功
- `404`: 项目不存在
- `401`: 未授权

**Section sources**
- [projects.py](file://backend/app/api/endpoints/projects.py#L90-L100)

### PUT /projects/{project_id} - 更新项目
**功能说明**  
更新项目信息。仅管理员可操作。

**请求体 (JSON Schema: ProjectUpdate)**  
```json
{
  "name": "string",
  "description": "string",
  "base_url": "string",
  "llm_provider": "string",
  "llm_model": "string",
  "llm_api_key": "string",
  "llm_config": {}
}
```

**HTTP状态码**  
- `200`: 更新成功
- `404`: 项目不存在
- `400`: 项目名已存在
- `401`: 未授权
- `403`: 无权限

**Section sources**
- [projects.py](file://backend/app/api/endpoints/projects.py#L105-L155)
- [project.py](file://backend/app/schemas/project.py#L26-L35)

### DELETE /projects/{project_id} - 删除项目
**功能说明**  
删除指定项目。仅管理员可操作。

**HTTP状态码**  
- `204`: 删除成功
- `404`: 项目不存在
- `401`: 未授权
- `403`: 无权限

**Section sources**
- [projects.py](file://backend/app/api/endpoints/projects.py#L160-L177)

## 测试用例API (/test-cases)

### GET /projects/{project_id}/cases - 获取项目测试用例列表
**功能说明**  
获取指定项目的测试用例列表，并包含每个测试用例的执行统计数据，如执行次数和通过率。

**请求头**  
- `Authorization: Bearer <token>`

**响应体 (200 OK)**  
```json
[
  {
    "id": 0,
    "project_id": 0,
    "name": "string",
    "description": "string",
    "natural_language": "string",
    "standard_steps": [],
    "playwright_script": {},
    "expected_result": "string",
    "created_by": 0,
    "created_at": "string",
    "updated_at": "string",
    "execution_count": 0,
    "pass_rate": 0.0
  }
]
```

**HTTP状态码**  
- `200`: 获取成功
- `404`: 项目不存在
- `401`: 未授权

**Section sources**
- [test_cases.py](file://backend/app/api/endpoints/test_cases.py#L15-L40)
- [test_case.py](file://backend/app/schemas/test_case.py#L67-L70)

### POST /projects/{project_id}/cases - 创建测试用例
**功能说明**  
在指定项目中创建测试用例。

**请求体 (JSON Schema: TestCaseCreate)**  
```json
{
  "project_id": 0,
  "name": "string",
  "description": "string",
  "natural_language": "string",
  "standard_steps": [],
  "playwright_script": {},
  "expected_result": "string"
}
```

**HTTP状态码**  
- `201`: 创建成功
- `404`: 项目不存在
- `400`: 项目ID不匹配
- `401`: 未授权

**Section sources**
- [test_cases.py](file://backend/app/api/endpoints/test_cases.py#L45-L75)
- [test_case.py](file://backend/app/schemas/test_case.py#L35-L40)

### POST /cases/generate-from-nl - 从自然语言生成标准化用例
**功能说明**  
使用LLM将自然语言描述转换为标准化的测试用例。

**请求体 (JSON Schema: NaturalLanguageRequest)**  
```json
{
  "project_id": 0,
  "natural_language": "string"
}
```

**响应体 (200 OK)**  
```json
{
  "name": "string",
  "description": "string",
  "standard_steps": [
    {
      "index": 0,
      "action": "string",
      "description": "string",
      "selector": "string",
      "value": "string",
      "expected": "string"
    }
  ],
  "expected_result": "string"
}
```

**HTTP状态码**  
- `200`: 生成成功
- `404`: 项目不存在
- `500`: 生成失败
- `401`: 未授权

**Section sources**
- [test_cases.py](file://backend/app/api/endpoints/test_cases.py#L150-L180)
- [test_case.py](file://backend/app/schemas/test_case.py#L60-L65)

### POST /cases/generate-script - 生成Playwright脚本
**功能说明**  
根据标准化测试用例生成Playwright执行脚本。

**请求体 (JSON Schema: ScriptGenerationRequest)**  
```json
{
  "test_case_id": 0
}
```

**响应体 (200 OK)**  
```json
{
  "playwright_script": {}
}
```

**HTTP状态码**  
- `200`: 生成成功
- `404`: 测试用例不存在
- `500`: 生成失败
- `401`: 未授权

**Section sources**
- [test_cases.py](file://backend/app/api/endpoints/test_cases.py#L185-L215)
- [test_case.py](file://backend/app/schemas/test_case.py#L75-L80)

## 测试执行API (/test-runs)

### POST /cases/{case_id}/execute - 执行测试用例
**功能说明**  
触发指定测试用例的执行。

**响应体 (200 OK)**  
```json
{
  "id": 0,
  "test_case_id": 0,
  "status": "running",
  "trigger_by": 0,
  "start_time": "string",
  "end_time": null,
  "llm_verdict": null,
  "llm_reason": null,
  "error_message": null,
  "artifacts_path": null,
  "created_at": "string"
}
```

**HTTP状态码**  
- `200`: 执行已触发
- `404`: 测试用例不存在
- `401`: 未授权

**Section sources**
- [test_runs.py](file://backend/app/api/endpoints/test_runs.py#L100-L130)

### GET /runs/{run_id} - 获取测试运行详情
**功能说明**  
获取测试运行的详细信息，包括步骤执行记录和测试用例信息。

**响应体 (200 OK)**  
```json
{
  "id": 0,
  "test_case_id": 0,
  "status": "running|success|failed|error",
  "trigger_by": 0,
  "start_time": "string",
  "end_time": "string",
  "llm_verdict": "passed|failed|unknown",
  "llm_reason": "string",
  "error_message": "string",
  "artifacts_path": "string",
  "created_at": "string",
  "steps": [
    {
      "id": 0,
      "test_run_id": 0,
      "step_index": 0,
      "step_description": "string",
      "status": "success|failed",
      "screenshot_path": "string",
      "start_time": "string",
      "end_time": "string",
      "error_message": "string"
    }
  ],
  "test_case": {
    "id": 0,
    "name": "string",
    "description": "string",
    "project_id": 0
  }
}
```

**HTTP状态码**  
- `200`: 获取成功
- `404`: 运行记录不存在
- `401`: 未授权

**Section sources**
- [test_runs.py](file://backend/app/api/endpoints/test_runs.py#L135-L170)
- [test_run.py](file://backend/app/schemas/test_run.py#L30-L53)

### GET /runs - 获取运行记录列表
**功能说明**  
获取测试运行记录列表，支持按项目或测试用例过滤。

**查询参数**  
- `project_id`: 按项目ID过滤
- `case_id`: 按测试用例ID过滤
- `limit`: 限制返回数量，默认50

**HTTP状态码**  
- `200`: 获取成功
- `401`: 未授权

**Section sources**
- [test_runs.py](file://backend/app/api/endpoints/test_runs.py#L175-L195)

## 错误处理策略
平台采用标准的HTTP状态码进行错误报告。客户端应根据状态码采取相应措施：
- `401 Unauthorized`: 令牌无效或过期，应重新登录获取新令牌。
- `403 Forbidden`: 当前用户无权限执行此操作，应检查角色权限。
- `404 Not Found`: 请求的资源不存在，应验证ID是否正确。
- `400 Bad Request`: 请求参数错误，应检查请求体格式。
- `500 Internal Server Error`: 服务器内部错误，可重试或联系管理员。

所有错误响应均包含`detail`字段，提供具体的错误信息。

**Section sources**
- [API_EXAMPLES.md](file://API_EXAMPLES.md#L450-L483)