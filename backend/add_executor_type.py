"""
添加 executor_type 字段到 project 和 test_case 表
"""
import sqlite3
import os

def add_executor_type_column():
    """添加 executor_type 字段"""
    try:
        # SQLite 数据库路径
        db_path = os.path.join(os.path.dirname(__file__), "ui_test_platform.db")
        
        if not os.path.exists(db_path):
            print(f"错误: 数据库文件不存在: {db_path}")
            return
        
        # 连接数据库
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # 检查 project 表是否已有 executor_type 字段
        cursor.execute("PRAGMA table_info(project)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'executor_type' not in columns:
            print("为 project 表添加 executor_type 字段...")
            cursor.execute("""
                ALTER TABLE project 
                ADD COLUMN executor_type VARCHAR(50) NOT NULL DEFAULT 'playwright'
            """)
            print("✓ project 表添加成功")
        else:
            print("✓ project 表已有 executor_type 字段")
        
        # 检查 test_case 表是否已有 executor_type 字段
        cursor.execute("PRAGMA table_info(test_case)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'executor_type' not in columns:
            print("为 test_case 表添加 executor_type 字段...")
            cursor.execute("""
                ALTER TABLE test_case 
                ADD COLUMN executor_type VARCHAR(50) NOT NULL DEFAULT 'playwright'
            """)
            print("✓ test_case 表添加成功")
        else:
            print("✓ test_case 表已有 executor_type 字段")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n所有字段添加完成！")
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    add_executor_type_column()
