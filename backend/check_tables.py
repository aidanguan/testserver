"""
检查数据库表
"""
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = [r[0] for r in result.fetchall()]
    
    print("\n数据库中的表:")
    for table in tables:
        print(f"  - {table}")
    
    print(f"\n总共 {len(tables)} 个表")
    
    # 检查是否有所需的表
    required_tables = ['user', 'project', 'test_case', 'test_run', 'step_execution']
    missing_tables = [t for t in required_tables if t not in tables]
    
    if missing_tables:
        print(f"\n❌ 缺少的表: {', '.join(missing_tables)}")
    else:
        print("\n✅ 所有必需的表都存在")
        
finally:
    db.close()
