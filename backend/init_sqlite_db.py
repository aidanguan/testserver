"""
SQLite 数据库初始化脚本
"""
from app.database import engine, Base
from app.models.user import User
from app.models.project import Project
from app.models.test_case import TestCase
from app.models.test_run import TestRun
from app.models.step_execution import StepExecution
from app.models.audit_log import AuditLog
from app.utils.security import get_password_hash

def init_db():
    """初始化数据库"""
    print("正在创建数据库表...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    print("数据库表创建成功！")
    
    # 创建默认管理员账户
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        # 检查是否已存在管理员账户
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("正在创建默认管理员账户...")
            admin = User(
                username="admin",
                password_hash=get_password_hash("admin"),
                role="Admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("✅ 默认管理员账户创建成功！")
            print("   用户名: admin")
            print("   密码: admin")
        else:
            print("⚠️  管理员账户已存在，跳过创建")
    except Exception as e:
        print(f"❌ 创建管理员账户失败: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n🎉 数据库初始化完成！")

if __name__ == "__main__":
    init_db()
