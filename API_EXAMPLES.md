# API 使用示例

本文档提供了平台API的实际使用示例。

## 基础URL

- 开发环境: `http://localhost:8000`
- API前缀: `/api`

## 认证

所有需要认证的API都需要在请求头中携带JWT Token:

```
Authorization: Bearer <your_token>
```

## 1. 用户认证

### 登录

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }'
```

**响应:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "Admin",
    "is_active": true,
    "created_at": "2025-10-23T00:00:00",
    "updated_at": "2025-10-23T00:00:00"
  }
}
```

### 获取当前用户信息

```bash
curl -X GET http://localhost:8000/api/auth/current \
  -H "Authorization: Bearer <token>"
```

## 2. 项目管理

### 创建项目

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "示例项目",
    "description": "这是一个测试项目",
    "base_url": "https://example.com",
    "llm_provider": "openai",
    "llm_model": "gpt-4",
    "llm_api_key": "sk-...",
    "llm_config": {
      "temperature": 0.7,
      "max_tokens": 2000
    }
  }'
```

**响应:**
```json
{
  "id": 1,
  "name": "示例项目",
  "description": "这是一个测试项目",
  "base_url": "https://example.com",
  "llm_provider": "openai",
  "llm_model": "gpt-4",
  "llm_api_key": "***",
  "llm_config": {
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "created_by": 1,
  "created_at": "2025-10-23T08:00:00",
  "updated_at": "2025-10-23T08:00:00"
}
```

### 获取项目列表

```bash
curl -X GET http://localhost:8000/api/projects \
  -H "Authorization: Bearer <token>"
```

### 获取项目详情

```bash
curl -X GET http://localhost:8000/api/projects/1 \
  -H "Authorization: Bearer <token>"
```

## 3. 测试用例

### 从自然语言生成测试用例

```bash
curl -X POST http://localhost:8000/api/cases/generate-from-nl \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "natural_language": "访问登录页面，输入用户名admin和密码admin，点击登录按钮，验证成功跳转到主页"
  }'
```

**响应:**
```json
{
  "name": "用户登录测试",
  "description": "测试用户使用正确的用户名和密码登录系统",
  "standard_steps": [
    {
      "index": 1,
      "action": "goto",
      "description": "打开登录页面",
      "selector": null,
      "value": "/login",
      "expected": null
    },
    {
      "index": 2,
      "action": "fill",
      "description": "输入用户名",
      "selector": "#username",
      "value": "admin",
      "expected": null
    },
    {
      "index": 3,
      "action": "fill",
      "description": "输入密码",
      "selector": "#password",
      "value": "admin",
      "expected": null
    },
    {
      "index": 4,
      "action": "click",
      "description": "点击登录按钮",
      "selector": "#login-button",
      "value": null,
      "expected": null
    },
    {
      "index": 5,
      "action": "assertVisible",
      "description": "验证进入主页",
      "selector": ".dashboard",
      "value": null,
      "expected": "显示用户仪表板"
    }
  ],
  "expected_result": "用户成功登录并跳转到主页"
}
```

### 创建测试用例

```bash
curl -X POST http://localhost:8000/api/projects/1/cases \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "name": "用户登录测试",
    "description": "测试用户登录功能",
    "natural_language": "访问登录页面，输入用户名admin和密码admin，点击登录按钮",
    "standard_steps": [...],
    "playwright_script": {...},
    "expected_result": "用户成功登录"
  }'
```

### 生成Playwright脚本

```bash
curl -X POST http://localhost:8000/api/cases/generate-script \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "test_case_id": 1
  }'
```

**响应:**
```json
{
  "playwright_script": {
    "browser": "chromium",
    "viewport": {
      "width": 1280,
      "height": 720
    },
    "steps": [
      {
        "index": 1,
        "action": "goto",
        "selector": null,
        "value": "https://example.com/login",
        "description": "打开登录页面",
        "screenshot": true
      },
      {
        "index": 2,
        "action": "fill",
        "selector": "#username",
        "value": "admin",
        "description": "输入用户名",
        "screenshot": true
      }
    ]
  }
}
```

### 获取项目的测试用例列表

```bash
curl -X GET http://localhost:8000/api/projects/1/cases \
  -H "Authorization: Bearer <token>"
```

## 4. 测试执行

### 执行测试用例

```bash
curl -X POST http://localhost:8000/api/cases/1/execute \
  -H "Authorization: Bearer <token>"
```

**响应:**
```json
{
  "id": 1,
  "test_case_id": 1,
  "status": "running",
  "trigger_by": 1,
  "start_time": "2025-10-23T08:30:00",
  "end_time": null,
  "llm_verdict": null,
  "llm_reason": null,
  "error_message": null,
  "artifacts_path": null,
  "created_at": "2025-10-23T08:30:00"
}
```

### 获取运行详情

```bash
curl -X GET http://localhost:8000/api/runs/1 \
  -H "Authorization: Bearer <token>"
```

**响应:**
```json
{
  "id": 1,
  "test_case_id": 1,
  "status": "success",
  "trigger_by": 1,
  "start_time": "2025-10-23T08:30:00",
  "end_time": "2025-10-23T08:31:30",
  "llm_verdict": "passed",
  "llm_reason": "所有步骤成功执行，页面元素正确显示，符合预期结果",
  "error_message": null,
  "artifacts_path": "../artifacts/runs/1",
  "created_at": "2025-10-23T08:30:00",
  "steps": [
    {
      "id": 1,
      "test_run_id": 1,
      "step_index": 1,
      "step_description": "打开登录页面",
      "status": "success",
      "screenshot_path": "../artifacts/runs/1/screenshots/step_1.png",
      "start_time": "2025-10-23T08:30:05",
      "end_time": "2025-10-23T08:30:08",
      "error_message": null
    }
  ],
  "test_case": {
    "id": 1,
    "name": "用户登录测试",
    "description": "测试用户登录功能",
    "project_id": 1
  }
}
```

### 获取步骤执行记录

```bash
curl -X GET http://localhost:8000/api/runs/1/steps \
  -H "Authorization: Bearer <token>"
```

### 查询运行记录列表

```bash
# 按用例查询
curl -X GET "http://localhost:8000/api/runs?case_id=1&limit=10" \
  -H "Authorization: Bearer <token>"

# 按项目查询
curl -X GET "http://localhost:8000/api/runs?project_id=1&limit=10" \
  -H "Authorization: Bearer <token>"
```

## 5. 用户管理 (仅管理员)

### 创建用户

```bash
curl -X POST http://localhost:8000/api/users \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123",
    "role": "Member"
  }'
```

### 获取用户列表

```bash
curl -X GET http://localhost:8000/api/users \
  -H "Authorization: Bearer <token>"
```

### 更新用户

```bash
curl -X PUT http://localhost:8000/api/users/2 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

## 完整工作流示例

### 1. 登录获取Token

```python
import requests

# 登录
login_response = requests.post(
    'http://localhost:8000/api/auth/login',
    json={'username': 'admin', 'password': 'admin'}
)
token = login_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
```

### 2. 创建项目

```python
project_response = requests.post(
    'http://localhost:8000/api/projects',
    headers=headers,
    json={
        'name': '我的测试项目',
        'base_url': 'https://example.com',
        'llm_provider': 'openai',
        'llm_model': 'gpt-4',
        'llm_api_key': 'sk-xxx'
    }
)
project_id = project_response.json()['id']
```

### 3. 生成测试用例

```python
# 使用自然语言生成
case_response = requests.post(
    'http://localhost:8000/api/cases/generate-from-nl',
    headers=headers,
    json={
        'project_id': project_id,
        'natural_language': '访问首页，点击登录按钮，输入用户名和密码，提交表单'
    }
)
case_data = case_response.json()
```

### 4. 生成脚本并创建用例

```python
# 先创建用例（需要先有playwright_script）
# 这里需要先调用generate-script生成脚本

# 创建完整用例
create_response = requests.post(
    f'http://localhost:8000/api/projects/{project_id}/cases',
    headers=headers,
    json={
        'project_id': project_id,
        'name': case_data['name'],
        'description': case_data['description'],
        'natural_language': '...',
        'standard_steps': case_data['standard_steps'],
        'playwright_script': {...},  # 从generate-script获取
        'expected_result': case_data['expected_result']
    }
)
case_id = create_response.json()['id']
```

### 5. 执行测试

```python
# 执行
run_response = requests.post(
    f'http://localhost:8000/api/cases/{case_id}/execute',
    headers=headers
)
run_id = run_response.json()['id']

# 轮询查询结果
import time
while True:
    result = requests.get(
        f'http://localhost:8000/api/runs/{run_id}',
        headers=headers
    ).json()
    
    if result['status'] in ['success', 'failed', 'error']:
        print(f"测试完成: {result['status']}")
        print(f"LLM判定: {result['llm_verdict']}")
        print(f"判定理由: {result['llm_reason']}")
        break
    
    time.sleep(2)
```

## 错误处理

### 常见错误响应

```json
{
  "detail": "错误描述信息"
}
```

### HTTP状态码

- `200`: 成功
- `201`: 创建成功
- `204`: 删除成功
- `400`: 请求参数错误
- `401`: 未授权（token无效或过期）
- `403`: 无权限
- `404`: 资源不存在
- `500`: 服务器内部错误

## 更多信息

访问 http://localhost:8000/docs 查看完整的交互式API文档（Swagger UI）
