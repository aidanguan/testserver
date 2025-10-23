"""验证后台任务中的数据库路径是否正确"""
import os

# 模拟 test_runs.py 中的路径（位于 app/api/endpoints/test_runs.py）
test_runs_location = os.path.join(os.getcwd(), "app", "api", "endpoints", "test_runs.py")
print(f"test_runs.py 位置: {test_runs_location}")

# 从 __file__ 开始计算（假设在 app/api/endpoints/test_runs.py）
file_path = test_runs_location

# 4层 dirname
dir1 = os.path.dirname(file_path)  # app/api/endpoints
dir2 = os.path.dirname(dir1)       # app/api
dir3 = os.path.dirname(dir2)       # app
dir4 = os.path.dirname(dir3)       # backend

print(f"\n第1层: {dir1}")
print(f"第2层: {dir2}")
print(f"第3层: {dir3}")
print(f"第4层: {dir4}")

db_path = os.path.join(dir4, "ui_test_platform.db")
print(f"\n最终数据库路径: {db_path}")
print(f"文件存在: {os.path.exists(db_path)}")

# 检查是否还有错误的数据库文件
wrong_path = os.path.join(dir3, "ui_test_platform.db")
print(f"\n错误的路径: {wrong_path}")
print(f"文件存在: {os.path.exists(wrong_path)}")
