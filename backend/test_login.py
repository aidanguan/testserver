"""
测试登录功能
"""
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import verify_password, get_password_hash
import bcrypt

def test_login():
    """测试登录流程"""
    db = SessionLocal()
    
    try:
        # 1. 检查管理员账户是否存在
        print("=" * 50)
        print("1. 检查管理员账户...")
        admin = db.query(User).filter(User.username == "admin").first()
        
        if not admin:
            print("❌ 管理员账户不存在！")
            return
        
        print(f"✅ 找到管理员账户")
        print(f"   - ID: {admin.id}")
        print(f"   - 用户名: {admin.username}")
        print(f"   - 角色: {admin.role}")
        print(f"   - 激活状态: {admin.is_active}")
        print(f"   - 密码哈希: {admin.password_hash[:50]}...")
        
        # 2. 测试密码验证
        print("\n" + "=" * 50)
        print("2. 测试密码验证...")
        test_password = "admin"
        
        # 方法1: 使用 passlib
        print(f"\n方法1: 使用 passlib verify_password()")
        try:
            result1 = verify_password(test_password, admin.password_hash)
            print(f"   结果: {'✅ 验证成功' if result1 else '❌ 验证失败'}")
        except Exception as e:
            print(f"   ❌ 验证出错: {e}")
        
        # 方法2: 直接使用 bcrypt
        print(f"\n方法2: 直接使用 bcrypt.checkpw()")
        try:
            result2 = bcrypt.checkpw(
                test_password.encode('utf-8'),
                admin.password_hash.encode('utf-8')
            )
            print(f"   结果: {'✅ 验证成功' if result2 else '❌ 验证失败'}")
        except Exception as e:
            print(f"   ❌ 验证出错: {e}")
        
        # 3. 测试生成新密码哈希
        print("\n" + "=" * 50)
        print("3. 测试生成新密码哈希...")
        try:
            new_hash = get_password_hash(test_password)
            print(f"✅ 新哈希生成成功")
            print(f"   新哈希: {new_hash[:50]}...")
            
            # 验证新哈希
            result3 = verify_password(test_password, new_hash)
            print(f"   验证新哈希: {'✅ 成功' if result3 else '❌ 失败'}")
        except Exception as e:
            print(f"❌ 生成失败: {e}")
        
        # 4. 查看所有用户
        print("\n" + "=" * 50)
        print("4. 数据库中所有用户:")
        users = db.query(User).all()
        for user in users:
            print(f"   - {user.username} ({user.role}) - 激活: {user.is_active}")
        
    finally:
        db.close()
    
    print("\n" + "=" * 50)
    print("测试完成！")

if __name__ == "__main__":
    test_login()
