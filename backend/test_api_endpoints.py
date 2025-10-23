"""
测试API端点
"""
import asyncio
from app.database import SessionLocal
from app.models.user import User
from app.api.endpoints.projects import get_dashboard_stats

async def test_dashboard_stats():
    db = SessionLocal()
    try:
        # 创建一个模拟的当前用户
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            print("❌ 找不到admin用户")
            return
        
        print(f"✅ 找到用户: {user.username}")
        
        # 调用API函数
        result = await get_dashboard_stats(db=db, current_user=user)
        print(f"\n统计数据结果:")
        print(f"  - 项目总数: {result['projects']}")
        print(f"  - 测试用例: {result['testCases']}")
        print(f"  - 执行次数: {result['totalRuns']}")
        print(f"  - 通过率: {result['passRate']}%")
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_dashboard_stats())
