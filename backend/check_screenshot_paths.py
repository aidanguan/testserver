"""检查数据库中的截图路径格式"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "ui_test_platform.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查询步骤执行记录
cursor.execute("SELECT id, test_run_id, step_index, screenshot_path FROM step_execution ORDER BY id DESC LIMIT 10")
rows = cursor.fetchall()

print("最近的步骤执行记录:")
print("-" * 100)
for row in rows:
    print(f"ID: {row[0]}, Run ID: {row[1]}, Step: {row[2]}")
    print(f"Screenshot: {row[3]}")
    print()

conn.close()
