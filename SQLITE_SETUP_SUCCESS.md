# ✅ SQLite 数据库配置成功

## 问题解决

原始问题：**MySQL 服务未运行导致无法连接数据库**

解决方案：**切换到 SQLite 数据库**（快速测试方案）

---

## 已完成的配置

### 1. 数据库切换
✅ 已将 `backend/app/database.py` 从 MySQL 切换到 SQLite  
✅ 数据库文件位置：`backend/ui_test_platform.db`

### 2. 数据库初始化
✅ 已创建所有数据表  
✅ 已创建默认管理员账户

### 3. 服务状态
✅ 后端服务运行在 `http://localhost:8000`  
✅ 前端服务运行在 `http://localhost:5173`  
✅ API 文档可访问：`http://localhost:8000/docs`

---

## 登录信息

**管理员账户**
- 用户名: `admin`
- 密码: `admin`

---

## 如何使用

### 方式 1: 浏览器访问前端
```
访问: http://localhost:5173
登录: admin / admin
```

### 方式 2: API 测试（Swagger UI）
```
访问: http://localhost:8000/docs
在 Swagger UI 中测试各个 API 接口
```

### 方式 3: 命令行测试 API
```powershell
# 测试登录接口
$body = @{
    username = "admin"
    password = "admin"
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/auth/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

# 查看返回的 token
$response.access_token

# 使用 token 访问受保护的接口
$headers = @{
    Authorization = "Bearer $($response.access_token)"
}

Invoke-RestMethod `
    -Uri "http://localhost:8000/api/auth/current" `
    -Headers $headers
```

---

## 数据库管理

### 查看数据库
```powershell
# 如果安装了 SQLite 工具
sqlite3 backend/ui_test_platform.db

# 查看所有表
.tables

# 查看用户表
SELECT * FROM user;

# 退出
.exit
```

### 重新初始化数据库
```powershell
cd backend

# 删除现有数据库
Remove-Item ui_test_platform.db

# 重新初始化
py init_sqlite_db.py

# 创建管理员账户
py create_admin.py
```

---

## 切换回 MySQL（可选）

如果以后需要切换回 MySQL，请执行以下步骤：

### 1. 启动 MySQL 服务
```powershell
# 启动 MySQL 服务
Start-Service MySQL

# 或使用 XAMPP/WAMP 等工具启动
```

### 2. 初始化 MySQL 数据库
```powershell
# 执行初始化脚本
mysql -u root -p < backend/init_db.sql
```

### 3. 修改数据库配置
编辑 `backend/app/database.py`，注释 SQLite 配置，取消注释 MySQL 配置：

```python
# 注释掉 SQLite 配置
# import os
# db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui_test_platform.db")
# DATABASE_URL = f"sqlite:///{db_path}"
# engine = create_engine(
#     DATABASE_URL,
#     connect_args={"check_same_thread": False},
#     pool_pre_ping=True,
#     echo=False
# )

# 取消注释 MySQL 配置
DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)
```

### 4. 重启后端服务
```powershell
# 停止当前服务 (Ctrl+C)
# 重新启动
cd backend
py main.py
```

---

## 下一步测试建议

### 1. 测试完整的用户流程

**步骤 1: 登录系统**
- 访问 http://localhost:5173
- 输入 admin/admin

**步骤 2: 创建测试项目**
- 点击"创建项目"
- 填写项目信息：
  - 项目名称: "测试项目"
  - 目标 URL: "https://example.com"
  - LLM 配置: 需要有效的 OpenAI API Key

**步骤 3: 创建测试用例**
- 进入项目详情
- 点击"创建测试用例"
- 输入自然语言描述，例如：
  ```
  打开首页，点击登录按钮，输入用户名，输入密码，点击提交
  ```

**步骤 4: 执行测试**
- 点击"执行测试"
- 查看实时执行状态
- 查看每个步骤的截图

### 2. 功能测试清单

- [ ] 用户登录/登出
- [ ] 创建项目
- [ ] 编辑项目
- [ ] 删除项目
- [ ] 创建测试用例（自然语言）
- [ ] 查看生成的标准化测试用例
- [ ] 查看生成的 Playwright 脚本
- [ ] 执行测试用例
- [ ] 查看测试运行记录
- [ ] 查看测试步骤截图
- [ ] 下载测试工件

### 3. API 测试（使用 Swagger UI）

访问 http://localhost:8000/docs 测试以下 API：

- [ ] POST /api/auth/login - 登录
- [ ] GET /api/auth/current - 获取当前用户
- [ ] GET /api/projects - 获取项目列表
- [ ] POST /api/projects - 创建项目
- [ ] POST /api/test-cases - 创建测试用例
- [ ] POST /api/test-runs - 执行测试

---

## 常见问题

### Q: 前端无法连接后端？
**A:** 检查 CORS 配置，确保 `backend/app/config.py` 中的 `CORS_ORIGINS` 包含 `http://localhost:5173`

### Q: 登录失败？
**A:** 检查数据库中是否有管理员账户：
```powershell
cd backend
py -c "from app.database import SessionLocal; from app.models.user import User; db = SessionLocal(); print(db.query(User).filter(User.username == 'admin').first())"
```

### Q: 测试执行失败？
**A:** 确保已安装 Playwright 浏览器：
```powershell
py -m playwright install chromium
```

---

## 性能与安全建议

### SQLite 的优点
✅ 无需安装额外服务  
✅ 配置简单  
✅ 适合开发和测试  
✅ 数据文件便于备份

### SQLite 的限制
⚠️ 不支持高并发写入  
⚠️ 不适合生产环境大规模部署  
⚠️ 缺少一些高级特性（如存储过程）

**建议**: 开发测试使用 SQLite，生产环境切换到 MySQL

---

## 系统监控

### 查看后端日志
后端运行的终端会显示所有请求日志和错误信息

### 查看数据库大小
```powershell
Get-Item backend/ui_test_platform.db | Select-Object Name, Length
```

### 查看工件存储
```powershell
Get-ChildItem -Recurse artifacts/
```

---

🎉 **恭喜！系统已成功运行，可以开始测试了！**

如有任何问题，请查看：
- 后端日志（终端输出）
- 前端浏览器控制台
- API 文档：http://localhost:8000/docs
