# URS 平台调试指南

## 🎉 项目已成功启动！

### 当前运行状态

✅ **后端服务**: 运行在 `http://localhost:8000`  
✅ **前端服务**: 运行在 `http://localhost:5173`  
✅ **Playwright Chromium**: 已安装  

---

## 访问应用

### 前端界面
- **URL**: http://localhost:5173
- **默认管理员账号**:
  - 用户名: `admin`
  - 密码: `admin`

### 后端 API
- **健康检查**: http://localhost:8000/health
- **API 文档**: http://localhost:8000/docs (FastAPI 自动生成的 Swagger UI)
- **API 基础路径**: http://localhost:8000/api

---

## 调试步骤

### 1. 测试后端 API

```powershell
# 健康检查
curl http://localhost:8000/health

# 查看 API 文档
# 在浏览器中打开: http://localhost:8000/docs
```

### 2. 测试用户登录

```powershell
# 使用 PowerShell 测试登录接口
$body = @{
    username = "admin"
    password = "admin"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

### 3. 前端功能测试清单

- [ ] 登录功能 (admin/admin)
- [ ] 项目列表页面
- [ ] 创建新项目 (配置 LLM 参数)
- [ ] 创建测试用例 (自然语言输入)
- [ ] 查看生成的标准化测试用例
- [ ] 执行测试用例
- [ ] 查看测试运行记录
- [ ] 查看测试步骤截图

---

## 常见问题排查

### 问题 1: 后端无法连接数据库

**症状**: 启动时出现数据库连接错误

**解决方案**:
```powershell
# 1. 确保 MySQL 服务正在运行
Get-Service -Name MySQL* | Start-Service

# 2. 检查数据库是否已初始化
# 在 MySQL 中执行:
mysql -u root -p < backend/init_db.sql

# 3. 检查 .env 配置
# 确保 backend/.env 中的数据库配置正确
```

### 问题 2: 前端无法访问后端 API

**症状**: 前端显示网络错误

**解决方案**:
```powershell
# 1. 检查后端是否运行
curl http://localhost:8000/health

# 2. 检查 CORS 配置
# 确认 backend/app/config.py 中 CORS_ORIGINS 包含前端地址
```

### 问题 3: Playwright 执行失败

**症状**: 测试执行时浏览器无法启动

**解决方案**:
```powershell
# 重新安装 Playwright 浏览器
cd backend
py -m playwright install chromium

# 检查 Playwright 是否正常
py -m playwright --version
```

---

## 开发工具

### 后端日志查看
后端服务运行在终端中，实时显示请求日志和错误信息。

### 前端热重载
前端使用 Vite，修改代码后会自动刷新浏览器。

### API 调试工具
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 停止服务

```powershell
# 停止后端 (在运行 main.py 的终端中按 Ctrl+C)

# 停止前端 (在运行 npm run dev 的终端中按 Ctrl+C)
```

---

## 下一步调试建议

### 1. 测试完整流程

1. **登录系统**
   - 访问 http://localhost:5173
   - 使用 admin/admin 登录

2. **创建测试项目**
   - 配置项目名称和目标 URL
   - 配置 LLM 参数 (需要有效的 OpenAI API Key)

3. **创建测试用例**
   - 输入自然语言描述，例如:
     ```
     打开登录页面,输入用户名admin,输入密码admin,点击登录按钮,验证是否跳转到首页
     ```
   - 系统会自动生成标准化测试用例和 Playwright 脚本

4. **执行测试**
   - 点击"执行测试"按钮
   - 查看实时执行状态
   - 查看每个步骤的截图

5. **查看测试结果**
   - 查看 LLM 判定结果
   - 下载截图和日志

### 2. 检查数据库数据

```sql
-- 查看用户表
SELECT * FROM user;

-- 查看项目表
SELECT * FROM project;

-- 查看测试用例表
SELECT * FROM test_case;

-- 查看测试运行记录
SELECT * FROM test_run;
```

### 3. 监控工件存储

```powershell
# 查看工件存储目录
ls ../artifacts -Recurse

# 查看某次执行的截图
ls ../artifacts/runs/<run_id>
```

---

## 开发建议

### 代码热重载
- **后端**: 已启用自动重载，修改代码后会自动重启
- **前端**: Vite 自动热重载，无需手动刷新

### 日志级别
修改 `backend/app/config.py` 中的日志级别以获取更详细的调试信息。

### 数据库迁移
如果修改了数据库模型，需要重新执行 `init_db.sql`。

---

## 性能监控

### 后端性能
- 查看 Uvicorn 日志中的请求响应时间
- 使用 FastAPI 的 `/docs` 接口测试各个 API 的性能

### 前端性能
- 使用浏览器开发者工具的 Network 面板
- 监控 API 请求时间和资源加载时间

---

## 联系与支持

如遇到问题，请检查:
1. 后端终端的错误日志
2. 前端浏览器控制台的错误信息
3. 数据库连接状态
4. LLM API Key 是否有效

祝调试顺利！🚀
