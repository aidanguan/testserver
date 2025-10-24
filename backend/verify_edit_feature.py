"""
验证测试用例编辑功能
"""
import sqlite3
import os
import json

def verify_edit_feature():
    """验证编辑功能"""
    try:
        # SQLite 数据库路径
        db_path = os.path.join(os.path.dirname(__file__), "ui_test_platform.db")
        
        if not os.path.exists(db_path):
            print(f"❌ 错误: 数据库文件不存在: {db_path}")
            return False
        
        # 连接数据库
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        print("=" * 60)
        print("测试用例编辑功能验证")
        print("=" * 60)
        
        # 1. 检查 midscene_script 字段是否存在
        print("\n1. 检查数据库字段...")
        cursor.execute("PRAGMA table_info(test_case)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'midscene_script' in columns:
            print("   ✅ midscene_script 字段存在")
        else:
            print("   ❌ midscene_script 字段不存在")
            return False
        
        # 2. 检查 Midscene 测试用例
        print("\n2. 检查 Midscene 测试用例...")
        cursor.execute("""
            SELECT id, name, executor_type, 
                   CASE WHEN midscene_script IS NULL OR midscene_script = '' 
                        THEN 'EMPTY' 
                        ELSE 'OK' 
                   END as midscene_status,
                   CASE WHEN playwright_script IS NULL OR playwright_script = '' 
                        THEN 'EMPTY' 
                        ELSE 'OK' 
                   END as playwright_status
            FROM test_case 
            WHERE executor_type = 'midscene'
        """)
        
        midscene_cases = cursor.fetchall()
        
        if not midscene_cases:
            print("   ⚠️  没有找到 Midscene 测试用例")
        else:
            print(f"   找到 {len(midscene_cases)} 个 Midscene 测试用例")
            for case_id, name, executor_type, midscene_status, playwright_status in midscene_cases:
                print(f"\n   用例 ID={case_id}, Name={name}")
                print(f"     - executor_type: {executor_type}")
                print(f"     - midscene_script: {midscene_status}")
                print(f"     - playwright_script: {playwright_status}")
                
                if midscene_status == 'OK':
                    print("     ✅ midscene_script 已设置")
                else:
                    print("     ❌ midscene_script 为空（需要迁移）")
        
        # 3. 检查 Playwright 测试用例
        print("\n3. 检查 Playwright 测试用例...")
        cursor.execute("""
            SELECT id, name, executor_type, 
                   CASE WHEN playwright_script IS NULL OR playwright_script = '' 
                        THEN 'EMPTY' 
                        ELSE 'OK' 
                   END as playwright_status
            FROM test_case 
            WHERE executor_type = 'playwright'
        """)
        
        playwright_cases = cursor.fetchall()
        
        if not playwright_cases:
            print("   ⚠️  没有找到 Playwright 测试用例")
        else:
            print(f"   找到 {len(playwright_cases)} 个 Playwright 测试用例")
            for case_id, name, executor_type, playwright_status in playwright_cases:
                print(f"\n   用例 ID={case_id}, Name={name}")
                print(f"     - executor_type: {executor_type}")
                print(f"     - playwright_script: {playwright_status}")
                
                if playwright_status == 'OK':
                    print("     ✅ playwright_script 已设置")
                else:
                    print("     ❌ playwright_script 为空")
        
        # 4. 验证 JSON 格式
        print("\n4. 验证脚本 JSON 格式...")
        cursor.execute("""
            SELECT id, name, executor_type, midscene_script, playwright_script
            FROM test_case
        """)
        
        all_cases = cursor.fetchall()
        json_errors = []
        
        for case_id, name, executor_type, midscene_script, playwright_script in all_cases:
            # 验证 midscene_script
            if midscene_script:
                try:
                    json.loads(midscene_script)
                except json.JSONDecodeError as e:
                    json_errors.append(f"用例 ID={case_id}: midscene_script JSON 格式错误 - {str(e)}")
            
            # 验证 playwright_script
            if playwright_script:
                try:
                    json.loads(playwright_script)
                except json.JSONDecodeError as e:
                    json_errors.append(f"用例 ID={case_id}: playwright_script JSON 格式错误 - {str(e)}")
        
        if json_errors:
            print("   ❌ 发现 JSON 格式错误:")
            for error in json_errors:
                print(f"     - {error}")
        else:
            print("   ✅ 所有脚本 JSON 格式正确")
        
        # 5. 总结
        print("\n" + "=" * 60)
        print("验证总结")
        print("=" * 60)
        
        total_cases = len(all_cases)
        midscene_count = len(midscene_cases)
        playwright_count = len(playwright_cases)
        
        print(f"总测试用例数: {total_cases}")
        print(f"  - Midscene: {midscene_count}")
        print(f"  - Playwright: {playwright_count}")
        
        if json_errors:
            print("\n❌ 验证失败：存在 JSON 格式错误")
            return False
        
        # 检查是否所有 Midscene 用例都有 midscene_script
        empty_midscene = [c for c in midscene_cases if c[3] == 'EMPTY']
        if empty_midscene:
            print(f"\n⚠️  发现 {len(empty_midscene)} 个 Midscene 用例的 midscene_script 为空")
            print("   建议运行 migrate_midscene_scripts.py 进行数据迁移")
        else:
            print("\n✅ 所有功能验证通过！")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ 验证过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verify_edit_feature()
