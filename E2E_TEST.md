# 端到端功能测试脚本

## 测试环境准备

1. 确保MySQL服务已启动
2. 确保数据库已初始化
3. 确保后端服务已启动 (http://localhost:8000)
4. 确保前端服务已启动 (http://localhost:5173)

## 手动测试步骤

### 1. 用户认证测试

**测试用例 1.1**: 登录功能
- [ ] 访问 http://localhost:5173
- [ ] 输入用户名: admin
- [ ] 输入密码: admin
- [ ] 点击登录
- [ ] 验证: 成功进入仪表板页面

**测试用例 1.2**: 登出功能
- [ ] 点击右上角用户下拉菜单
- [ ] 点击"退出登录"
- [ ] 验证: 返回登录页面

**测试用例 1.3**: 未登录访问保护页面
- [ ] 登出后直接访问 http://localhost:5173/projects
- [ ] 验证: 自动跳转到登录页

### 2. 项目管理测试

**测试用例 2.1**: 创建项目
- [ ] 登录后点击左侧"项目管理"
- [ ] 点击"创建项目"按钮
- [ ] 填写项目信息:
  - 项目名称: 测试项目1
  - 描述: 这是一个测试项目
  - 测试站点: https://example.com
  - LLM提供商: openai
  - 模型: gpt-4 (或 gpt-3.5-turbo)
  - API密钥: sk-... (需要真实的OpenAI API Key)
- [ ] 点击"创建"
- [ ] 验证: 项目列表中显示新创建的项目

**测试用例 2.2**: 查看项目详情
- [ ] 在项目列表中点击"查看"按钮
- [ ] 验证: 显示项目详情页面
- [ ] 验证: 显示"测试用例"和"项目配置"两个标签页

**测试用例 2.3**: 删除项目 (仅管理员)
- [ ] 在项目列表中点击"删除"按钮
- [ ] 确认删除对话框
- [ ] 验证: 项目从列表中移除

### 3. 用户管理测试 (仅管理员)

**测试用例 3.1**: 创建用户
- [ ] 点击左侧"用户管理"
- [ ] 点击"创建用户"按钮
- [ ] 填写用户信息:
  - 用户名: testuser
  - 密码: testpass123
  - 角色: 成员
- [ ] 点击"创建"
- [ ] 验证: 用户列表中显示新用户

**测试用例 3.2**: 编辑用户
- [ ] 点击用户行的"编辑"按钮
- [ ] 修改角色或状态
- [ ] 点击"保存"
- [ ] 验证: 用户信息更新

**测试用例 3.3**: 删除用户
- [ ] 点击用户行的"删除"按钮
- [ ] 确认删除
- [ ] 验证: 用户从列表移除

### 4. 测试用例管理测试

**测试用例 4.1**: 使用自然语言创建测试用例
- [ ] 进入项目详情页
- [ ] 点击"创建测试用例"
- [ ] 在自然语言输入框输入:
  ```
  访问example.com首页，验证页面标题包含"Example Domain"，
  检查页面中是否显示了"This domain is for use in illustrative examples"文本
  ```
- [ ] 点击"下一步:生成用例"
- [ ] 验证: AI生成了结构化的测试步骤
- [ ] 点击"下一步:生成脚本"
- [ ] 验证: 生成了Playwright脚本
- [ ] 点击"保存用例"
- [ ] 验证: 用例创建成功

**测试用例 4.2**: 查看测试用例列表
- [ ] 在项目详情页查看"测试用例"标签页
- [ ] 验证: 显示已创建的用例

### 5. 测试执行测试

**测试用例 5.1**: 执行测试用例
- [ ] 在测试用例列表点击"执行"按钮
- [ ] 验证: 跳转到运行详情页
- [ ] 验证: 显示"运行中"状态
- [ ] 等待执行完成
- [ ] 验证: 状态更新为"成功"或"失败"
- [ ] 验证: 显示LLM判定结果
- [ ] 验证: 显示判定理由

**测试用例 5.2**: 查看执行步骤
- [ ] 在运行详情页查看步骤时间线
- [ ] 验证: 每个步骤都有截图
- [ ] 验证: 显示步骤耗时
- [ ] 验证: 失败步骤显示错误信息

### 6. API 测试

**测试用例 6.1**: API 文档访问
- [ ] 访问 http://localhost:8000/docs
- [ ] 验证: 显示Swagger API文档
- [ ] 验证: 可以查看所有API端点

**测试用例 6.2**: 健康检查
- [ ] 访问 http://localhost:8000/health
- [ ] 验证: 返回 {"status": "healthy"}

## 自动化测试脚本

### Python测试脚本

```python
import requests
import time

BASE_URL = "http://localhost:8000/api"

def test_login():
    """测试登录"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "admin"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    print("✓ 登录测试通过")
    return data["access_token"]

def test_create_project(token):
    """测试创建项目"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/projects", headers=headers, json={
        "name": f"测试项目_{int(time.time())}",
        "description": "自动化测试项目",
        "base_url": "https://example.com",
        "llm_provider": "openai",
        "llm_model": "gpt-3.5-turbo",
        "llm_api_key": "sk-test-key"
    })
    assert response.status_code == 201
    project = response.json()
    assert "id" in project
    print(f"✓ 创建项目测试通过, 项目ID: {project['id']}")
    return project["id"]

def test_list_projects(token):
    """测试获取项目列表"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/projects", headers=headers)
    assert response.status_code == 200
    projects = response.json()
    assert isinstance(projects, list)
    print(f"✓ 获取项目列表测试通过, 共{len(projects)}个项目")

def run_tests():
    """运行所有测试"""
    print("开始运行端到端测试...")
    print()
    
    try:
        # 测试登录
        token = test_login()
        
        # 测试项目管理
        project_id = test_create_project(token)
        test_list_projects(token)
        
        print()
        print("=" * 50)
        print("所有测试通过! ✓")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n测试出错: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
```

### 使用方法

```bash
# 保存上面的Python脚本为 test_e2e.py
# 运行测试
cd testserver
python test_e2e.py
```

## 测试结果记录

### 测试环境
- 操作系统: Windows/Linux/macOS
- Python版本: 
- Node.js版本: 
- MySQL版本: 

### 测试结果

| 测试用例 | 状态 | 备注 |
|---------|------|------|
| 1.1 登录功能 | ⬜ | |
| 1.2 登出功能 | ⬜ | |
| 1.3 未登录访问保护 | ⬜ | |
| 2.1 创建项目 | ⬜ | |
| 2.2 查看项目详情 | ⬜ | |
| 2.3 删除项目 | ⬜ | |
| 3.1 创建用户 | ⬜ | |
| 3.2 编辑用户 | ⬜ | |
| 3.3 删除用户 | ⬜ | |
| 4.1 创建测试用例 | ⬜ | |
| 4.2 查看测试用例列表 | ⬜ | |
| 5.1 执行测试用例 | ⬜ | |
| 5.2 查看执行步骤 | ⬜ | |
| 6.1 API文档访问 | ⬜ | |
| 6.2 健康检查 | ⬜ | |

**图例**: ✅ 通过 | ❌ 失败 | ⬜ 未测试

## 常见问题排查

### 问题1: 无法连接数据库
- 检查MySQL服务是否启动
- 检查.env中的数据库配置
- 检查数据库是否已创建

### 问题2: LLM API调用失败
- 检查API密钥是否正确
- 检查网络连接
- 检查API配额是否充足

### 问题3: 前端无法连接后端
- 检查后端服务是否启动
- 检查端口是否被占用
- 检查CORS配置

### 问题4: Playwright执行失败
- 确保Playwright浏览器已安装
- 检查被测网站是否可访问
- 查看详细错误日志

---

**测试完成日期**: __________
**测试人员**: __________
**测试结果**: ⬜ 通过 | ⬜ 部分通过 | ⬜ 失败
