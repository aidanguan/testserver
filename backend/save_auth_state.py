"""
手动保存Playwright登录状态的工具脚本
用法: python save_auth_state.py --project-id <项目ID> --url <登录页面URL>
"""
import argparse
import os
from playwright.sync_api import sync_playwright
from app.services.auth_state_manager import AuthStateManager


def save_login_state(project_id: int, login_url: str):
    """
    手动保存登录状态
    
    Args:
        project_id: 项目ID
        login_url: 登录页面URL
    """
    print(f"\n==========  保存登录状态 ==========")
    print(f"项目ID: {project_id}")
    print(f"登录URL: {login_url}")
    print(f"==================================\n")
    
    # 初始化认证状态管理器
    auth_manager = AuthStateManager()
    
    # 启动浏览器
    print("🚀 启动浏览器...")
    with sync_playwright() as p:
        # 使用有头模式，让用户手动登录
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"📖 打开登录页面: {login_url}")
        page.goto(login_url)
        
        print("\n" + "="*60)
        print("请在浏览器中完成登录操作")
        print("登录成功后，按 Enter 键继续...")
        print("="*60 + "\n")
        
        # 等待用户确认
        input()
        
        # 保存认证状态
        print("\n💾 保存认证状态...")
        result = auth_manager.save_auth_state(project_id, context)
        
        if result["success"]:
            print(f"✅ {result['message']}")
            print(f"📁 文件路径: {result['file_path']}")
            print(f"🍪 Cookies 数量: {result['cookies_count']}")
            print(f"🌐 域名数量: {result['origins_count']}")
        else:
            print(f"❌ 保存失败: {result['message']}")
        
        # 关闭浏览器
        browser.close()
    
    print("\n✨ 完成！下次执行测试时会自动使用这个登录状态。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="保存Playwright登录状态")
    parser.add_argument("--project-id", type=int, required=True, help="项目ID")
    parser.add_argument("--url", type=str, required=True, help="登录页面URL")
    
    args = parser.parse_args()
    
    save_login_state(args.project_id, args.url)
