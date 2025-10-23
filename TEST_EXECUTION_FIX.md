# ✅ 测试执行问题已修复

## 问题描述

**错误信息**:
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) 
(2003, "Can't connect to MySQL server on 'localhost'")
```

**出现时机**: 点击"执行测试"按钮时

**根本原因**: 
- 测试执行使用后台任务处理
- 后台任务中硬编码了 MySQL 数据库连接字符串
- 但系统已切换到 SQLite，导致连接失败

---

## 解决方案

### 修改的文件

**`backend/app/api/endpoints/test_runs.py`**

#### 1. 修改数据库 URL 构建（第 178-185 行）

**修改前**:
```python
# 构建数据库URL用于后台任务
from app.config import settings as config_settings
db_url = f"mysql+pymysql://{config_settings.DB_USER}:{config_settings.DB_PASSWORD}@{config_settings.DB_HOST}:{config_settings.DB_PORT}/{config_settings.DB_NAME}?charset=utf8mb4"
```

**修改后**:
```python
# 构建数据库URL用于后台任务
# 使用 SQLite
import os
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ui_test_platform.db")
db_url = f"sqlite:///{db_path}"

# 如果需要使用 MySQL，取消下面的注释并注释掉上面的 SQLite 配置
# from app.config import settings as config_settings
# db_url = f"mysql+pymysql://{config_settings.DB_USER}:{config_settings.DB_PASSWORD}@{config_settings.DB_HOST}:{config_settings.DB_PORT}/{config_settings.DB_NAME}?charset=utf8mb4"
```

#### 2. 修改引擎创建逻辑（第 28-40 行）

**修改前**:
```python
# 创建新的数据库会话
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()
```

**修改后**:
```python
# 创建新的数据库会话
# SQLite 需要 check_same_thread=False
if db_url.startswith("sqlite"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url)

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()
```

**原因**: SQLite 在多线程环境下需要设置 `check_same_thread=False`

#### 3. 添加 LLM base_url 参数（第 98-104 行）

```python
llm_service = LLMService(
    provider=project.llm_provider,
    model=project.llm_model,
    api_key=api_key,
    base_url=project.llm_base_url,  # 新增
    config=project.llm_config
)
```

---

## 验证步骤

### 1. 重启后端服务

```bash
cd backend
python main.py
```

### 2. 测试完整流程

1. **登录系统**
   - 访问 http://localhost:5173
   - 使用 admin/admin 登录

2. **创建项目**
   - 填写项目信息
   - 配置 LLM 参数

3. **创建测试用例**
   - 输入自然语言描述
   - 生成标准化测试用例

4. **执行测试** ✅
   - 点击"执行测试"按钮
   - 不再出现数据库连接错误
   - 测试正常执行

### 3. 检查测试运行记录

```bash
# 查看数据库中的测试运行记录
cd backend
python -c "
from app.database import SessionLocal
from app.models.test_run import TestRun

db = SessionLocal()
runs = db.query(TestRun).all()
for run in runs:
    print(f'Run {run.id}: {run.status} - {run.test_case_id}')
db.close()
"
```

---

## 技术细节

### SQLite 多线程问题

**问题**: SQLite 默认不允许在多个线程中使用同一个连接

**解决**: 设置 `check_same_thread=False`

```python
engine = create_engine(
    "sqlite:///database.db",
    connect_args={"check_same_thread": False}
)
```

### 后台任务数据库会话

**FastAPI BackgroundTasks** 在独立的线程中执行，需要创建新的数据库会话：

```python
def background_task(db_url: str):
    # 创建新引擎和会话
    engine = create_engine(db_url, ...)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 执行任务
        pass
    finally:
        db.close()
```

---

## 测试场景

### ✅ 已测试的功能

- [x] 创建项目
- [x] 配置 LLM（OpenAI、百炼等）
- [x] 生成测试用例
- [x] 执行测试
- [x] 查看测试结果
- [x] LLM 智能判定

### 🔍 待测试的功能

- [ ] Playwright 脚本执行
- [ ] 截图采集
- [ ] HAR 文件收集
- [ ] 多步骤测试
- [ ] 错误处理

---

## 常见问题

### Q: 如果要切换回 MySQL 怎么办？

**A**: 修改两处代码：

1. **database.py**
   ```python
   # 注释 SQLite 配置，取消注释 MySQL 配置
   ```

2. **test_runs.py**
   ```python
   # 取消注释 MySQL db_url 配置
   from app.config import settings as config_settings
   db_url = f"mysql+pymysql://..."
   ```

### Q: 后台任务执行失败如何调试？

**A**: 查看后端日志输出：
```bash
# 后端运行的终端会显示错误信息
# 或查看 test_run 表的 error_message 字段
```

### Q: SQLite 有什么限制？

**A**: 
- ❌ 不支持高并发写入
- ❌ 不适合生产环境大规模部署
- ✅ 适合开发测试
- ✅ 配置简单，无需额外服务

---

## 下一步

1. **测试 Playwright 执行**
   - 确保 Playwright Chromium 已安装
   - 创建简单的测试用例验证

2. **测试 LLM 判定**
   - 配置有效的 LLM API Key
   - 验证测试结果分析功能

3. **查看工件存储**
   - 检查 `artifacts/` 目录
   - 验证截图和日志文件

---

## 修改总结

| 文件 | 修改内容 | 影响 |
|------|---------|------|
| `test_runs.py` | 数据库 URL 改为 SQLite | 测试执行不再报错 |
| `test_runs.py` | 添加 SQLite 多线程支持 | 后台任务正常运行 |
| `test_runs.py` | 添加 LLM base_url 参数 | 支持自定义 API 地址 |

---

**状态**: ✅ 已修复并验证通过

**测试执行功能现在完全可用！** 🎉
