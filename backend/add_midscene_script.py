"""
添加 midscene_script 字段到 test_case 表
"""
import sqlite3
import os

def add_midscene_script_column():
    """添加 midscene_script 字段"""
    try:
        # SQLite 数据库路径
        db_path = os.path.join(os.path.dirname(__file__), "ui_test_platform.db")
        
        if not os.path.exists(db_path):
            print(f"错误: 数据库文件不存在: {db_path}")
            return
        
        # 连接数据库
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # 检查 test_case 表是否已有 midscene_script 字段
        cursor.execute("PRAGMA table_info(test_case)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'midscene_script' not in columns:
            print("为 test_case 表添加 midscene_script 字段...")
            cursor.execute("""
                ALTER TABLE test_case 
                ADD COLUMN midscene_script JSON
            """)
            print("✓ test_case 表添加 midscene_script 字段成功")
        else:
            print("✓ test_case 表已有 midscene_script 字段")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n字段添加完成！")
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    add_midscene_script_column()
