# 认证API

<cite>
**Referenced Files in This Document**   
- [auth.py](file://backend/app/api/endpoints/auth.py)
- [security.py](file://backend/app/utils/security.py)
- [config.py](file://backend/app/config.py)
- [user.py](file://backend/app/schemas/user.py)
- [dependencies.py](file://backend/app/api/dependencies.py)
</cite>

## 目录
1. [简介](#简介)
2. [核心端点](#核心端点)
3. [请求与响应结构](#请求与响应结构)
4. [认证流程详解](#认证流程详解)
5. [JWT令牌机制](#jwt令牌机制)
6. [使用示例](#使用示例)
7. [错误处理](#错误处理)
8. [安全配置](#安全配置)

## 简介
本文档详细说明了testserver系统的认证API，涵盖用户登录和令牌管理功能。系统采用基于JWT（JSON Web Token）的无状态认证机制，确保API调用的安全性。认证流程结合了密码验证和令牌生成，为前端应用提供安全的用户身份验证服务。

## 核心端点
认证API提供以下两个核心端点：

### 用户登录 (/api/auth/login)
- **方法**: POST
- **功能**: 验证用户凭据并颁发访问令牌
- **认证**: 无需认证
- **用途**: 用户通过用户名和密码进行身份验证

### 获取当前用户信息 (/api/auth/current)
- **方法**: GET
- **功能**: 获取当前登录用户的信息
- **认证**: 需要Bearer Token
- **用途**: 前端在用户登录后获取用户详细信息

**Section sources**
- [auth.py](file://backend/app/api/endpoints/auth.py#L15-L41)

## 请求与响应结构

### 登录请求 (POST /api/auth/login)
请求体为JSON格式，包含以下字段：

| 字段名 | 类型 | 必需 | 描述 |
|-------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

### 登录响应
成功认证后返回的响应体结构：

| 字段名 | 类型 | 描述 |
|-------|------|------|
| access_token | string | JWT访问令牌 |
| token_type | string | 令牌类型，固定为"bearer" |
| user | object | 用户信息对象 |

用户信息对象(user)包含：
- id: 用户ID
- username: 用户名
- role: 用户角色
- is_active: 账户是否激活
- created_at: 创建时间
- updated_at: 更新时间

```mermaid
classDiagram
class UserLogin {
+string username
+string password
}
class Token {
+string access_token
+string token_type
+UserResponse user
}
class UserResponse {
+int id
+string username
+UserRole role
+bool is_active
+datetime created_at
+datetime updated_at
}
Token --> UserResponse : "包含"
```

**Diagram sources**
- [user.py](file://backend/app/schemas/user.py#L38-L48)

## 认证流程详解
用户登录认证流程包含以下步骤：

```mermaid
sequenceDiagram
participant Client as "客户端"
participant AuthAPI as "认证API"
participant DB as "数据库"
participant Security as "安全模块"
Client->>AuthAPI : POST /api/auth/login
AuthAPI->>DB : 查询用户(username)
DB-->>AuthAPI : 用户数据
AuthAPI->>Security : verify_password(password, hash)
Security-->>AuthAPI : 验证结果
alt 验证失败
AuthAPI-->>Client : 401 Unauthorized
else 验证成功
AuthAPI->>Security : create_access_token(sub=username)
Security-->>AuthAPI : JWT令牌
AuthAPI-->>Client : 200 OK + Token
end
```

**Diagram sources**
- [auth.py](file://backend/app/api/endpoints/auth.py#L15-L41)
- [security.py](file://backend/app/utils/security.py#L13-L33)

### 密码验证流程
1. 用户提交用户名和密码
2. 系统根据用户名查询用户记录
3. 使用`verify_password`函数验证密码哈希
4. 如果验证成功，继续令牌生成流程

### 令牌创建流程
1. 调用`create_access_token`函数
2. 设置令牌载荷(payload)，包含用户名(sub)和过期时间(exp)
3. 使用JWT_SECRET_KEY和指定算法进行签名
4. 返回生成的JWT令牌

**Section sources**
- [auth.py](file://backend/app/api/endpoints/auth.py#L15-L41)
- [security.py](file://backend/app/utils/security.py#L13-L33)

## JWT令牌机制
系统使用JWT标准实现无状态认证，具体配置如下：

### 令牌生成
- **密钥**: 使用`JWT_SECRET_KEY`环境变量配置的密钥
- **算法**: HS256对称加密算法
- **载荷**: 包含用户名(sub)和过期时间(exp)
- **过期时间**: 默认24小时(1440分钟)

### 令牌验证
- **头信息**: 请求必须包含`Authorization: Bearer <token>`头
- **验证流程**: 解码令牌，验证签名和过期时间
- **用户获取**: 从令牌载荷中提取用户名，查询用户信息

```mermaid
flowchart TD
A[客户端请求] --> B{包含Authorization头?}
B --> |否| C[返回401]
B --> |是| D[提取Bearer Token]
D --> E[调用decode_access_token]
E --> F{令牌有效?}
F --> |否| G[返回401]
F --> |是| H[获取用户名]
H --> I[查询用户信息]
I --> J{用户存在且激活?}
J --> |否| K[返回401/403]
J --> |是| L[返回用户数据]
```

**Diagram sources**
- [security.py](file://backend/app/utils/security.py#L35-L43)
- [dependencies.py](file://backend/app/api/dependencies.py#L14-L51)

## 使用示例
### 登录请求示例
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

### 成功响应示例
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "ADMIN",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### 后续请求示例
```bash
curl -X GET "http://localhost:8000/api/auth/current" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx"
```

**Section sources**
- [auth.py](file://backend/app/api/endpoints/auth.py#L15-L41)

## 错误处理
系统定义了以下常见错误码：

| 状态码 | 错误类型 | 原因 | 解决方案 |
|-------|---------|------|---------|
| 401 Unauthorized | 未授权 | 用户名或密码错误 | 检查凭据是否正确 |
| 401 Unauthorized | 未授权 | 令牌无效或过期 | 重新登录获取新令牌 |
| 403 Forbidden | 禁止访问 | 用户被禁用 | 联系管理员激活账户 |
| 422 Unprocessable Entity | 参数错误 | 请求体格式不正确 | 检查JSON格式和必填字段 |

**Section sources**
- [auth.py](file://backend/app/api/endpoints/auth.py#L20-L30)
- [dependencies.py](file://backend/app/api/dependencies.py#L14-L51)

## 安全配置
系统安全配置定义在`config.py`文件中，关键参数如下：

| 配置项 | 默认值 | 说明 |
|-------|-------|------|
| JWT_SECRET_KEY | your-secret-key-change-in-production | JWT签名密钥，生产环境必须修改 |
| JWT_ALGORITHM | HS256 | JWT签名算法 |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | 1440 | 访问令牌有效期(分钟) |

**Section sources**
- [config.py](file://backend/app/config.py#L15-L20)
- [security.py](file://backend/app/utils/security.py#L23-L33)