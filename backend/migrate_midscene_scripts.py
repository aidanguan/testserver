"""
将 Midscene 测试用例的脚本从 playwright_script 迁移到 midscene_script
"""
import sqlite3
import os
import json

def migrate_midscene_scripts():
    """迁移 Midscene 脚本"""
    try:
        # SQLite 数据库路径
        db_path = os.path.join(os.path.dirname(__file__), "ui_test_platform.db")
        
        if not os.path.exists(db_path):
            print(f"错误: 数据库文件不存在: {db_path}")
            return
        
        # 连接数据库
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # 查找所有 executor_type 为 midscene 但 midscene_script 为空的测试用例
        cursor.execute("""
            SELECT id, name, playwright_script 
            FROM test_case 
            WHERE executor_type = 'midscene' AND (midscene_script IS NULL OR midscene_script = '')
        """)
        
        cases = cursor.fetchall()
        
        if not cases:
            print("✓ 没有需要迁移的测试用例")
            connection.close()
            return
        
        print(f"找到 {len(cases)} 个需要迁移的 Midscene 测试用例")
        
        for case_id, case_name, playwright_script in cases:
            print(f"\n迁移测试用例 ID={case_id}, Name={case_name}")
            
            if playwright_script:
                # 将 playwright_script 复制到 midscene_script
                cursor.execute("""
                    UPDATE test_case 
                    SET midscene_script = ? 
                    WHERE id = ?
                """, (playwright_script, case_id))
                
                print(f"  ✓ 已将脚本从 playwright_script 复制到 midscene_script")
            else:
                print(f"  ⚠ playwright_script 为空，跳过")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print(f"\n✓ 迁移完成！共处理 {len(cases)} 个测试用例")
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    migrate_midscene_scripts()
