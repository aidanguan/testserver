"""
测试保存登录状态功能
用于诊断保存失败的问题
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright
from app.services.auth_state_manager import AuthStateManager
import json


def test_playwright_storage_state():
    """测试 Playwright storage_state 功能"""
    print("\n" + "="*60)
    print("🧪 测试 Playwright Storage State 功能")
    print("="*60)
    
    try:
        print("\n1️⃣ 启动 Playwright...")
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        print("   ✅ Playwright 启动成功")
        
        print("\n2️⃣ 访问测试页面...")
        page.goto("https://www.baidu.com")
        print("   ✅ 页面加载成功")
        
        print("\n3️⃣ 等待 3 秒（模拟用户登录）...")
        page.wait_for_timeout(3000)
        
        print("\n4️⃣ 测试保存 storage_state...")
        test_file = "auth_states/test_storage_state.json"
        
        # 确保目录存在
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        # 保存状态
        print(f"   - 保存到: {test_file}")
        context.storage_state(path=test_file)
        print("   ✅ storage_state() 调用成功")
        
        print("\n5️⃣ 验证保存的文件...")
        if os.path.exists(test_file):
            print(f"   ✅ 文件已创建")
            
            with open(test_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cookies_count = len(data.get('cookies', []))
            origins_count = len(data.get('origins', []))
            file_size = os.path.getsize(test_file)
            
            print(f"   - Cookies 数量: {cookies_count}")
            print(f"   - Origins 数量: {origins_count}")
            print(f"   - 文件大小: {file_size} bytes")
            
            print("\n   ✅ 文件验证成功")
        else:
            print("   ❌ 文件未创建")
            return False
        
        print("\n6️⃣ 关闭浏览器...")
        browser.close()
        playwright.stop()
        print("   ✅ 浏览器已关闭")
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！Playwright storage_state 功能正常")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60 + "\n")
        return False


def test_auth_state_manager():
    """测试 AuthStateManager"""
    print("\n" + "="*60)
    print("🧪 测试 AuthStateManager")
    print("="*60)
    
    try:
        print("\n1️⃣ 创建 AuthStateManager...")
        manager = AuthStateManager()
        print("   ✅ AuthStateManager 创建成功")
        
        print("\n2️⃣ 启动浏览器会话...")
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.baidu.com")
        page.wait_for_timeout(2000)
        print("   ✅ 浏览器会话已启动")
        
        print("\n3️⃣ 使用 AuthStateManager 保存状态...")
        test_project_id = 999
        result = manager.save_auth_state(test_project_id, context)
        
        print(f"\n   保存结果:")
        print(f"   - Success: {result.get('success')}")
        print(f"   - Message: {result.get('message')}")
        print(f"   - File Path: {result.get('file_path')}")
        print(f"   - Cookies Count: {result.get('cookies_count')}")
        
        if result.get('success'):
            print("\n   ✅ AuthStateManager 保存成功")
        else:
            print("\n   ❌ AuthStateManager 保存失败")
        
        print("\n4️⃣ 关闭浏览器...")
        browser.close()
        playwright.stop()
        print("   ✅ 浏览器已关闭")
        
        print("\n" + "="*60)
        if result.get('success'):
            print("✅ AuthStateManager 测试通过")
        else:
            print("❌ AuthStateManager 测试失败")
        print("="*60 + "\n")
        
        return result.get('success')
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60 + "\n")
        return False


if __name__ == "__main__":
    print("\n🔍 开始诊断登录状态保存功能...\n")
    
    # 测试 Playwright storage_state 基本功能
    playwright_ok = test_playwright_storage_state()
    
    # 测试 AuthStateManager
    manager_ok = test_auth_state_manager()
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"Playwright storage_state: {'✅ 通过' if playwright_ok else '❌ 失败'}")
    print(f"AuthStateManager: {'✅ 通过' if manager_ok else '❌ 失败'}")
    print("="*60 + "\n")
    
    if playwright_ok and manager_ok:
        print("✅ 所有测试通过！功能正常。")
        print("\n如果 UI 界面仍然报错，请：")
        print("1. 打开浏览器控制台（F12）查看错误信息")
        print("2. 检查后端服务是否正常运行")
        print("3. 提供具体的错误消息\n")
    else:
        print("❌ 发现问题！请查看上面的错误信息。\n")
