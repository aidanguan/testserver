"""
添加vision_observation字段到step_execution表的数据库迁移脚本
执行命令: python add_vision_observation_column.py
"""
import sys
import os

# 添加 backend 目录到路径
backend_dir = os.path.dirname(__file__)
sys.path.insert(0, backend_dir)

from sqlalchemy import text
from app.database import engine

def migrate():
    """执行数据库迁移"""
    print("开始数据库迁移...")
    
    try:
        with engine.connect() as conn:
            # 检查列是否已存在
            if engine.dialect.name == 'sqlite':
                result = conn.execute(text("PRAGMA table_info(step_execution)"))
                columns = [row[1] for row in result]
                
                if 'vision_observation' not in columns:
                    print("添加 vision_observation 列到 step_execution 表...")
                    conn.execute(text("ALTER TABLE step_execution ADD COLUMN vision_observation TEXT"))
                    conn.commit()
                    print("✅ vision_observation 列添加成功")
                else:
                    print("⚠️ vision_observation 列已存在，跳过")
            
            elif engine.dialect.name == 'mysql':
                # 检查列是否存在
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'step_execution' 
                    AND COLUMN_NAME = 'vision_observation'
                """))
                exists = result.scalar() > 0
                
                if not exists:
                    print("添加 vision_observation 列到 step_execution 表...")
                    conn.execute(text("ALTER TABLE step_execution ADD COLUMN vision_observation TEXT"))
                    conn.commit()
                    print("✅ vision_observation 列添加成功")
                else:
                    print("⚠️ vision_observation 列已存在，跳过")
        
        print("✅ 数据库迁移完成！")
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        raise

if __name__ == "__main__":
    migrate()
