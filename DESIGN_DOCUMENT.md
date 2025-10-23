# 基于 Web 的自然语言驱动 UI 测试平台 URS - 系统设计文档

## 版本信息
- **版本**: v1.2
- **日期**: 2025-10-22
- **项目名称**: URS (UI Test Recording System)

---

## 目录
1. [系统架构设计](#1-系统架构设计)
2. [技术栈选型](#2-技术栈选型)
3. [数据库设计](#3-数据库设计)
4. [API 接口设计](#4-api-接口设计)
5. [核心功能模块设计](#5-核心功能模块设计)

---

## 1. 系统架构设计

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Vue 3)                        │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │用户管理  │项目管理  │用例管理  │测试执行  │结果查询  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ HTTP/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    后端层 (Python FastAPI)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              认证与授权模块 (JWT)                     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │用户服务  │项目服务  │用例服务  │执行服务  │日志服务  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
            │                 │                 │
            ▼                 ▼                 ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│   MySQL 数据库    │ │  LLM 服务层   │ │  MCP Playwright  │
│                  │ │  (OpenAI/等)  │ │   执行引擎       │
└──────────────────┘ └──────────────┘ └──────────────────┘
```

### 1.2 核心组件说明

#### 前端层
- **技术**: Vue 3 + Vue Router + Pinia + Element Plus
- **职责**: 用户交互界面、实时测试执行状态展示、测试结果可视化

#### 后端层
- **技术**: Python 3.11+ + FastAPI + SQLAlchemy
- **职责**: RESTful API 服务、业务逻辑处理、数据持久化

#### LLM 服务层
- **技术**: LangChain + OpenAI SDK
- **职责**: 自然语言解析、测试用例生成、Playwright 脚本生成、测试结果智能判定

#### 执行引擎层
- **技术**: Playwright (通过 MCP 协议)
- **职责**: 浏览器自动化、分步骤执行、截图采集、HAR 数据收集

---

## 2. 技术栈选型

### 2.1 后端技术栈

| 组件 | 技术选型 | 版本 | 说明 |
|------|---------|------|------|
| Web 框架 | FastAPI | 0.104+ | 高性能异步框架 |
| ORM | SQLAlchemy | 2.0+ | 异步 ORM 支持 |
| 数据验证 | Pydantic | 2.0+ | 数据验证和序列化 |
| 数据库驱动 | aiomysql | 0.2.0+ | 异步 MySQL 驱动 |
| 认证 | python-jose | 3.3+ | JWT token 生成与验证 |
| 密码加密 | passlib | 1.7+ | 密码哈希处理 |
| 任务队列 | Celery | 5.3+ | 异步任务处理 |
| 消息队列 | Redis | 7.0+ | Celery broker 和缓存 |
| WebSocket | python-socketio | 5.10+ | 实时通信 |
| LLM 集成 | langchain | 0.1+ | LLM 调用封装 |

### 2.2 前端技术栈

| 组件 | 技术选型 | 版本 | 说明 |
|------|---------|------|------|
| 框架 | Vue | 3.3+ | 渐进式 JavaScript 框架 |
| 路由 | Vue Router | 4.2+ | 官方路由管理器 |
| 状态管理 | Pinia | 2.1+ | 轻量级状态管理 |
| UI 组件库 | Element Plus | 2.4+ | 企业级 UI 组件库 |
| HTTP 客户端 | Axios | 1.6+ | Promise based HTTP 客户端 |
| WebSocket | Socket.io-client | 4.6+ | 实时通信客户端 |
| 代码编辑器 | Monaco Editor | 0.44+ | 脚本编辑器 |

---

## 3. 数据库设计

### 3.1 核心表结构

#### 3.1.1 users (用户表)

```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    role ENUM('admin', 'member') NOT NULL DEFAULT 'member' COMMENT '角色',
    email VARCHAR(100) COMMENT '邮箱',
    full_name VARCHAR(100) COMMENT '全名',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否激活',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    last_login TIMESTAMP NULL COMMENT '最后登录时间',
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
```

#### 3.1.2 projects (项目表)

```sql
CREATE TABLE projects (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '项目ID',
    name VARCHAR(100) NOT NULL COMMENT '项目名称',
    code VARCHAR(50) NOT NULL UNIQUE COMMENT '项目编码',
    base_url VARCHAR(500) NOT NULL COMMENT '目标站点URL',
    description TEXT COMMENT '项目描述',
    llm_config JSON COMMENT 'LLM配置参数',
    browser_config JSON COMMENT '浏览器配置',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否激活',
    created_by BIGINT NOT NULL COMMENT '创建人ID',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目表';
```

#### 3.1.3 test_cases (测试用例表)

```sql
CREATE TABLE test_cases (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '用例ID',
    project_id BIGINT NOT NULL COMMENT '所属项目ID',
    name VARCHAR(200) NOT NULL COMMENT '用例名称',
    nl_input TEXT NOT NULL COMMENT '自然语言输入',
    std_testcase JSON COMMENT '标准化测试用例',
    script TEXT COMMENT 'Playwright脚本',
    expected_result TEXT COMMENT '预期结果描述',
    status ENUM('draft', 'ready', 'archived') NOT NULL DEFAULT 'draft' COMMENT '状态',
    tags JSON COMMENT '标签',
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium' COMMENT '优先级',
    created_by BIGINT NOT NULL COMMENT '创建人ID',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_project_id (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试用例表';
```

#### 3.1.4 test_executions (测试执行记录表)

```sql
CREATE TABLE test_executions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '执行记录ID',
    test_case_id BIGINT NOT NULL COMMENT '测试用例ID',
    execution_number INT NOT NULL COMMENT '执行序号',
    status ENUM('pending', 'running', 'passed', 'failed', 'error', 'cancelled') NOT NULL DEFAULT 'pending',
    start_time TIMESTAMP NULL COMMENT '开始时间',
    end_time TIMESTAMP NULL COMMENT '结束时间',
    duration INT COMMENT '执行时长(秒)',
    executor_id BIGINT NOT NULL COMMENT '执行人ID',
    llm_verdict JSON COMMENT 'LLM判定结果',
    error_message TEXT COMMENT '错误信息',
    artifacts_path VARCHAR(500) COMMENT '工件存储路径',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (executor_id) REFERENCES users(id),
    INDEX idx_test_case_id (test_case_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试执行记录表';
```

#### 3.1.5 execution_steps (执行步骤表)

```sql
CREATE TABLE execution_steps (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '步骤ID',
    execution_id BIGINT NOT NULL COMMENT '执行记录ID',
    step_number INT NOT NULL COMMENT '步骤序号',
    action VARCHAR(200) NOT NULL COMMENT '执行动作',
    screenshot_path VARCHAR(500) COMMENT '截图路径',
    har_path VARCHAR(500) COMMENT 'HAR文件路径',
    log_content TEXT COMMENT '日志内容',
    status ENUM('pending', 'running', 'success', 'failed') NOT NULL DEFAULT 'pending',
    error_message TEXT COMMENT '错误信息',
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES test_executions(id) ON DELETE CASCADE,
    INDEX idx_execution_id (execution_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='执行步骤表';
```

### 3.2 初始化数据

```sql
-- 插入默认管理员账户 (密码: admin, 使用 bcrypt 加密)
INSERT INTO users (username, password_hash, role, email, full_name) 
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJbL3JQRS', 
        'admin', 'admin@urs.local', '系统管理员');
```

---

## 4. API 接口设计

### 4.1 接口规范

#### 基础信息
- **基础路径**: `/api/v1`
- **认证方式**: Bearer Token (JWT)
- **内容类型**: `application/json`

#### 通用响应格式

成功响应:
```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

错误响应:
```json
{
  "code": 1001,
  "message": "错误描述",
  "detail": "详细错误信息"
}
```

### 4.2 认证模块

#### POST /api/v1/auth/login
用户登录

**请求**:
```json
{
  "username": "admin",
  "password": "admin"
}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin"
    }
  }
}
```

### 4.3 项目管理

#### GET /api/v1/projects
获取项目列表

#### POST /api/v1/projects
创建项目

**请求**:
```json
{
  "name": "电商平台测试",
  "code": "ECOM001",
  "base_url": "https://example.com",
  "description": "电商平台UI自动化测试",
  "llm_config": {
    "provider": "openai",
    "model": "gpt-4-turbo-preview",
    "api_key": "sk-xxx",
    "temperature": 0.7
  }
}
```

### 4.4 测试用例管理

#### POST /api/v1/projects/{project_id}/test-cases
创建测试用例（自然语言输入）

**请求**:
```json
{
  "name": "用户登录测试",
  "nl_input": "打开登录页面,输入用户名admin,输入密码admin,点击登录按钮,验证是否跳转到首页",
  "expected_result": "成功登录并跳转到首页",
  "priority": "high"
}
```

### 4.5 测试执行

#### POST /api/v1/test-cases/{case_id}/execute
执行测试用例

**响应**:
```json
{
  "code": 0,
  "data": {
    "execution_id": 100,
    "status": "pending",
    "websocket_room": "execution_100"
  }
}
```

#### GET /api/v1/executions/{execution_id}
获取执行详情

---

## 5. 核心功能模块设计

### 5.1 自然语言处理模块

#### 5.1.1 NL to 标准化用例转换

**LLM Prompt 模板**:
```python
TESTCASE_GENERATION_PROMPT = """
你是一个专业的测试用例设计专家。请根据用户提供的自然语言描述,生成一个标准化的测试用例。

测试用例应包含以下JSON结构:
{
  "test_id": "唯一测试ID",
  "test_name": "测试用例名称",
  "steps": [
    {
      "step_no": 1,
      "action": "navigate/click/input/verify",
      "description": "步骤描述",
      "target": "目标元素CSS选择器",
      "input_value": "输入值(可选)",
      "expected": "预期结果"
    }
  ]
}

用户输入: {nl_input}
目标网站: {base_url}
"""
```

#### 5.1.2 标准化用例 to Playwright 脚本转换

**生成的脚本示例**:
```python
async def test_user_login(page):
    """用户登录测试"""
    
    # Step 1: 打开登录页面
    await page.goto("https://example.com/login")
    await page.screenshot(path="step_1.png")
    
    # Step 2: 输入用户名
    await page.locator("#username").fill("admin")
    await page.screenshot(path="step_2.png")
    
    # Step 3: 输入密码
    await page.locator("#password").fill("admin")
    await page.screenshot(path="step_3.png")
    
    # Step 4: 点击登录
    await page.locator("#login-btn").click()
    await page.screenshot(path="step_4.png")
```

### 5.2 测试执行引擎

```python
class TestExecutor:
    """测试执行器"""
    
    async def execute(self):
        """执行测试"""
        # 1. 初始化浏览器
        await self.setup_browser()
        
        # 2. 逐步执行测试
        for step in self.test_steps:
            await self.execute_step(step)
            
        # 3. LLM 判定结果
        verdict = await self.llm_verdict()
        
        # 4. 更新状态
        await self.update_status(verdict)
```

### 5.3 LLM 结果判定模块

**判定 Prompt**:
```python
VERDICT_PROMPT = """
你是UI测试结果分析专家。根据测试执行截图和日志,判定测试是否通过。

测试信息:
- 名称: {test_name}
- 预期结果: {expected_result}

执行步骤:
{steps_detail}

请输出JSON格式判定:
{
  "overall_result": "passed/failed",
  "confidence": 0.95,
  "analysis": "详细分析"
}
"""
```

### 5.4 WebSocket 实时通信

```python
@app.websocket("/ws/execution/{execution_id}")
async def websocket_endpoint(websocket: WebSocket, execution_id: int):
    await websocket.accept()
    
    # 发送步骤完成通知
    await websocket.send_json({
        "type": "step_completed",
        "data": {
            "step_number": 3,
            "status": "success",
            "screenshot_url": "/api/artifacts/step_3.png"
        }
    })
```

### 5.5 工件存储模块

**存储结构**:
```
artifacts/
└── executions/
    └── {execution_id}/
        ├── step_1_screenshot.png
        ├── step_1.har
        ├── step_2_screenshot.png
        └── execution.log
```

---

## 附录: 项目目录结构

```
urs-platform/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── api/               # API 路由
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   ├── core/              # 核心配置
│   │   └── utils/             # 工具函数
│   ├── tests/                 # 测试代码
│   ├── requirements.txt
│   └── main.py
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   ├── components/        # 通用组件
│   │   ├── stores/            # Pinia 状态
│   │   └── router/            # 路由配置
│   └── package.json
├── database/                   # 数据库脚本
│   └── init.sql
└── docker-compose.yml         # Docker 编排
```
