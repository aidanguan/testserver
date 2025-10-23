"""
创建管理员账户
"""
import bcrypt
from app.database import SessionLocal
from app.models.user import User

def create_admin():
    """创建管理员账户"""
    db = SessionLocal()
    
    try:
        # 检查是否已存在管理员账户
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("⚠️  管理员账户已存在")
            return
        
        # 直接使用 bcrypt 生成密码哈希
        password = "admin"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        admin = User(
            username="admin",
            password_hash=password_hash,
            role="Admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        
        print("✅ 管理员账户创建成功！")
        print("   用户名: admin")
        print("   密码: admin")
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
