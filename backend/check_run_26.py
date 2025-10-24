import sqlite3

conn = sqlite3.connect('c:/AI/testserver/backend/app/testcase.db')
cursor = conn.cursor()

# 获取所有表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print("所有表:", tables)

# 查询 test_runs 表
cursor.execute("SELECT id, artifacts_path FROM test_runs WHERE id = 26")
run = cursor.fetchone()
print(f"\nTest Run 26: ID={run[0]}, artifacts_path={run[1]}")

# 查询步骤执行记录
for table in tables:
    if 'step' in table.lower():
        print(f"\n检查表: {table}")
        try:
            cursor.execute(f"SELECT id, step_number, screenshot_path FROM {table} WHERE run_id = 26")
            steps = cursor.fetchall()
            for s in steps:
                print(f"  Step {s[1]}: {s[2]}")
        except Exception as e:
            print(f"  错误: {e}")

conn.close()
