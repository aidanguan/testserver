"""检查数据库路径"""
import os

# 模拟 test_runs.py 中的路径构建
current_file = os.path.abspath(__file__)
print(f"当前文件: {current_file}")

# test_runs.py 的位置
test_runs_file = os.path.join(os.path.dirname(current_file), "app", "api", "endpoints", "test_runs.py")
print(f"test_runs.py 位置: {test_runs_file}")

# 从 test_runs.py 往上找
# os.path.dirname(__file__) -> app/api/endpoints/
# os.path.dirname(os.path.dirname(__file__)) -> app/api/
# os.path.dirname(os.path.dirname(os.path.dirname(__file__))) -> app/
dir1 = os.path.dirname(test_runs_file)
print(f"第1层 dirname: {dir1}")

dir2 = os.path.dirname(dir1)
print(f"第2层 dirname: {dir2}")

dir3 = os.path.dirname(dir2)
print(f"第3层 dirname: {dir3}")

db_path_wrong = os.path.join(dir3, "ui_test_platform.db")
print(f"\n错误的DB路径: {db_path_wrong}")
print(f"文件存在: {os.path.exists(db_path_wrong)}")

# 正确的应该是 backend/ui_test_platform.db
backend_dir = os.path.dirname(current_file)
db_path_correct = os.path.join(backend_dir, "ui_test_platform.db")
print(f"\n正确的DB路径: {db_path_correct}")
print(f"文件存在: {os.path.exists(db_path_correct)}")
