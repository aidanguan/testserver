"""
快速诊断工具 - 检查登录状态保存功能
"""
import os
import sys

def check_environment():
    """检查环境配置"""
    print("\n" + "="*60)
    print("环境检查")
    print("="*60)
    
    # 1. 检查 Python 版本
    print(f"\n✓ Python 版本: {sys.version}")
    
    # 2. 检查 Playwright 安装
    try:
        import playwright
        print(f"✓ Playwright 已安装: {playwright.__version__}")
    except ImportError:
        print("✗ Playwright 未安装")
        return False
    
    # 3. 检查 auth_states 目录
    auth_states_dir = os.path.join(os.path.dirname(__file__), "auth_states")
    if os.path.exists(auth_states_dir):
        print(f"✓ auth_states 目录存在: {auth_states_dir}")
        
        # 检查写入权限
        test_file = os.path.join(auth_states_dir, "_test_write.tmp")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print(f"✓ auth_states 目录可写")
        except Exception as e:
            print(f"✗ auth_states 目录不可写: {e}")
            return False
    else:
        print(f"✗ auth_states 目录不存在: {auth_states_dir}")
        try:
            os.makedirs(auth_states_dir)
            print(f"✓ 已创建 auth_states 目录")
        except Exception as e:
            print(f"✗ 无法创建 auth_states 目录: {e}")
            return False
    
    # 4. 检查已保存的认证状态文件
    auth_files = [f for f in os.listdir(auth_states_dir) if f.endswith('_auth.json')]
    if auth_files:
        print(f"\n已保存的认证状态文件:")
        for f in auth_files:
            file_path = os.path.join(auth_states_dir, f)
            file_size = os.path.getsize(file_path)
            print(f"  - {f} ({file_size} bytes)")
    else:
        print(f"\n暂无已保存的认证状态文件")
    
    return True


def test_playwright():
    """测试 Playwright 基本功能"""
    print("\n" + "="*60)
    print("Playwright 功能测试")
    print("="*60)
    
    try:
        from playwright.sync_api import sync_playwright
        
        print("\n正在启动 Playwright...")
        with sync_playwright() as p:
            print("✓ Playwright 启动成功")
            
            print("正在启动浏览器...")
            browser = p.chromium.launch(headless=True)
            print("✓ 浏览器启动成功")
            
            print("正在创建上下文...")
            context = browser.new_context()
            print("✓ 上下文创建成功")
            
            print("正在创建页面...")
            page = context.new_page()
            print("✓ 页面创建成功")
            
            # 测试 storage_state
            print("\n正在测试 storage_state 功能...")
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                temp_file = f.name
            
            try:
                context.storage_state(path=temp_file)
                print(f"✓ storage_state 保存成功: {temp_file}")
                
                # 检查文件
                import json
                with open(temp_file, 'r') as f:
                    state_data = json.load(f)
                
                print(f"  - Cookies: {len(state_data.get('cookies', []))}")
                print(f"  - Origins: {len(state_data.get('origins', []))}")
                
                # 删除临时文件
                os.remove(temp_file)
                print(f"✓ 临时文件已清理")
                
            except Exception as e:
                print(f"✗ storage_state 失败: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            browser.close()
            print("✓ 浏览器已关闭")
        
        print("\n✅ Playwright 功能测试通过!")
        return True
        
    except Exception as e:
        print(f"\n✗ Playwright 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_backend_service():
    """检查后端服务"""
    print("\n" + "="*60)
    print("后端服务检查")
    print("="*60)
    
    try:
        import requests
        
        # 检查健康状态
        print("\n正在检查后端服务...")
        response = requests.get('http://localhost:8000/health', timeout=5)
        
        if response.status_code == 200:
            print("✓ 后端服务运行正常")
            print(f"  响应: {response.json()}")
            return True
        else:
            print(f"✗ 后端服务异常: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到后端服务 (http://localhost:8000)")
        print("  请确保后端服务已启动: py main.py")
        return False
    except Exception as e:
        print(f"✗ 检查后端服务失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("登录状态保存功能 - 诊断工具")
    print("="*60)
    
    results = []
    
    # 1. 环境检查
    results.append(("环境配置", check_environment()))
    
    # 2. Playwright 测试
    results.append(("Playwright 功能", test_playwright()))
    
    # 3. 后端服务检查
    results.append(("后端服务", check_backend_service()))
    
    # 总结
    print("\n" + "="*60)
    print("诊断结果总结")
    print("="*60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 所有检查通过! 系统配置正常。")
        print("\n如果仍然无法保存登录状态，请:")
        print("1. 查看后端日志中的详细错误信息")
        print("2. 查看浏览器控制台的错误信息")
        print("3. 参考故障排查文档: docs/登录状态保存故障排查.md")
    else:
        print("\n⚠️  发现问题，请根据上述错误信息进行修复。")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
