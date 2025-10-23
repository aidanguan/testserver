"""
添加 llm_base_url 字段到 project 表
"""
from app.database import SessionLocal, engine
from sqlalchemy import text

def add_llm_base_url_column():
    """添加 llm_base_url 列到 project 表"""
    db = SessionLocal()
    
    try:
        print("正在添加 llm_base_url 字段到 project 表...")
        
        # 检查列是否已存在
        result = db.execute(text("PRAGMA table_info(project)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'llm_base_url' in columns:
            print("⚠️  llm_base_url 字段已存在，跳过")
            return
        
        # 添加新列
        db.execute(text(
            "ALTER TABLE project ADD COLUMN llm_base_url VARCHAR(500)"
        ))
        db.commit()
        
        print("✅ llm_base_url 字段添加成功！")
        
    except Exception as e:
        print(f"❌ 添加字段失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_llm_base_url_column()
