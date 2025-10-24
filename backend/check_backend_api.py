"""
检查后端 API 服务状态
"""

import requests
import json


def check_backend_api():
    """检查后端 API 是否可访问"""
    print("\n🔍 检查后端 API 服务状态...\n")
    
    base_url = "http://127.0.0.1:8000"
    
    tests = [
        {
            "name": "健康检查",
            "url": f"{base_url}/",
            "method": "GET"
        },
        {
            "name": "API 文档",
            "url": f"{base_url}/docs",
            "method": "GET"
        }
    ]
    
    for test in tests:
        try:
            print(f"📡 {test['name']}: {test['url']}")
            
            response = None
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=5)
            
            if response and response.status_code == 200:
                print(f"   ✅ 状态码: {response.status_code}")
            elif response:
                print(f"   ⚠️  状态码: {response.status_code}")
            
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 连接失败 - 后端服务可能未启动")
            print(f"\n请先启动后端服务：")
            print(f"   cd c:\\AI\\testserver\\backend")
            print(f"   python -m uvicorn main:app --reload\n")
            return False
        
        except Exception as e:
            print(f"   ❌ 错误: {str(e)}")
    
    print("\n✅ 后端服务运行正常\n")
    return True


if __name__ == "__main__":
    check_backend_api()
