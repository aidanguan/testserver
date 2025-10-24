"""
测试 Midscene 集成
"""
import sys
import os

# 添加 backend 到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.midscene_executor import MidsceneExecutor

def test_installation():
    """测试 Midscene 是否正确安装"""
    print("=" * 60)
    print("测试 Midscene 安装状态")
    print("=" * 60)
    
    executor = MidsceneExecutor("./artifacts")
    status = executor.check_installation()
    
    print(f"\n安装状态: {'✅ 已安装' if status['installed'] else '❌ 未安装'}")
    print(f"Node modules: {'✅ 存在' if status['node_modules_exists'] else '❌ 不存在'}")
    print(f"Midscene 目录: {status['midscene_dir']}")
    print(f"执行器脚本: {status['executor_script']}")
    
    if status.get('error'):
        print(f"错误: {status['error']}")
        return False
    
    return status['installed']

def test_simple_execution():
    """测试简单的 Midscene 执行"""
    print("\n" + "=" * 60)
    print("测试 Midscene 执行 (简单示例)")
    print("=" * 60)
    
    # 创建一个简单的测试脚本
    test_script = {
        "browser": "chromium",
        "viewport": {"width": 1280, "height": 720},
        "steps": [
            {
                "index": 1,
                "action": "goto",
                "value": "https://www.example.com",
                "description": "打开示例网站",
                "screenshot": True
            },
            {
                "index": 2,
                "action": "aiAssert",
                "description": "页面标题包含 Example Domain",
                "screenshot": True
            }
        ]
    }
    
    print("\n测试脚本:")
    print(f"  - 访问: https://www.example.com")
    print(f"  - 验证: 页面标题包含 'Example Domain'")
    
    # 注意: 这需要配置 LLM API 密钥
    print("\n⚠️ 注意: 实际执行需要在 backend/midscene/.env 中配置 LLM API 密钥")
    print("   例如: OPENAI_API_KEY=sk-...")
    
    # 如果想实际执行，取消下面的注释:
    # executor = MidsceneExecutor("./artifacts")
    # env_vars = {
    #     "OPENAI_API_KEY": "your-api-key-here",
    #     "OPENAI_BASE_URL": "https://api.openai.com/v1"
    # }
    # result = executor.execute_script(test_script, run_id=999, env_vars=env_vars)
    # print(f"\n执行结果: {result}")
    
    return True

def main():
    """主测试函数"""
    print("\n🚀 Midscene 集成测试")
    print("=" * 60)
    
    # 测试安装
    if not test_installation():
        print("\n❌ Midscene 未正确安装")
        print("   请运行: cd backend/midscene && npm install")
        return
    
    # 测试执行
    test_simple_execution()
    
    print("\n" + "=" * 60)
    print("✅ 集成测试完成！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 配置 LLM API 密钥: backend/midscene/.env")
    print("2. 在项目中选择 executor_type='midscene'")
    print("3. 创建测试用例并执行")
    print("\n详细文档:")
    print("- 快速开始: MIDSCENE_QUICKSTART.md")
    print("- 完整指南: MIDSCENE_INTEGRATION.md")

if __name__ == "__main__":
    main()
