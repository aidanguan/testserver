# 数据库路径修复说明

## 问题描述

测试执行时一直显示"执行中"状态，没有显示步骤和截图。后台日志显示错误：
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: test_run
```

## 根本原因

后台任务中的数据库路径计算错误：

**错误代码**（3层 dirname）:
```python
db_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    "ui_test_platform.db"
)
```

这导致路径为：`backend/app/ui_test_platform.db`（空数据库）

**文件位置**：
- `test_runs.py` 位于：`backend/app/api/endpoints/test_runs.py`
- 需要往上 4 层才能到达 `backend/` 目录

## 修复方案

修改 `backend/app/api/endpoints/test_runs.py` 第 176-183 行：

**修复后的代码**（4层 dirname）:
```python
# 构建数据库URL用于后台任务
# 使用 SQLite - 需要从 app/api/endpoints/ 往上4层到 backend/
import os
# __file__ -> app/api/endpoints/test_runs.py
# 需要4个 dirname 到达 backend/
db_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
    "ui_test_platform.db"
)
db_url = f"sqlite:///{db_path}"
print(f"后台任务使用数据库路径: {db_path}")
```

## 路径层级说明

```
backend/app/api/endpoints/test_runs.py  <- __file__
         ↓ os.path.dirname(__file__)
backend/app/api/endpoints/               <- 第1层
         ↓ dirname
backend/app/api/                         <- 第2层
         ↓ dirname
backend/app/                             <- 第3层（错误的位置）
         ↓ dirname
backend/                                 <- 第4层（正确的位置）
```

## 修复步骤

1. **删除错误的数据库文件**:
   ```powershell
   Remove-Item "backend\app\ui_test_platform.db" -Force
   ```

2. **重启后端服务器**:
   - 停止当前服务器（Ctrl+C）
   - 重新运行：`py main.py`

3. **重新执行测试**:
   - 在前端点击"执行"按钮
   - 现在应该能看到步骤和截图了

## 验证

运行验证脚本确认路径正确：
```bash
py verify_db_path.py
```

输出应显示：
```
最终数据库路径: C:\AI\testserver\backend\ui_test_platform.db
文件存在: True

错误的路径: C:\AI\testserver\backend\app\ui_test_platform.db
文件存在: False
```

## 相关文件

- **修改**: `backend/app/api/endpoints/test_runs.py` (第 176-183 行)
- **删除**: `backend/app/ui_test_platform.db` (错误的空数据库)
- **使用**: `backend/ui_test_platform.db` (正确的数据库)

## 日期

2025-10-23
