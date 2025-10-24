# Midscene 集成指南

## 📖 概述

本项目已成功集成 [Midscene.js](https://github.com/web-infra-dev/midscene) - 一个强大的视觉驱动 AI 自动化测试框架。Midscene 使用视觉语言模型(VL)来理解和操作 UI，无需依赖脆弱的 CSS 选择器。

## 🎯 Midscene 的优势

### 相比传统 Playwright:
- **无需选择器**: 使用自然语言描述元素，AI 自动定位
- **更稳定**: 不受 DOM 结构变化影响
- **更智能**: 支持复杂的视觉判断和断言
- **更易维护**: 测试脚本更接近人类语言

### 核心能力:
- `aiTap`: AI 点击 - "点击登录按钮"
- `aiInput`: AI 输入 - "在搜索框中输入"
- `aiAssert`: AI 断言 - "页面显示用户仪表板"
- `aiWaitFor`: AI 等待 - "等待搜索结果加载完成"
- `aiQuery`: AI 查询 - 提取页面数据
- `aiAction`: 通用 AI 操作 - 描述复杂操作序列

## 📦 安装步骤

### 1. 安装 Node.js 依赖

进入 Midscene 执行器目录并安装依赖:

```powershell
cd backend\midscene
npm install
```

这将安装:
- `@midscene/web`: Midscene 核心库
- `playwright`: 浏览器自动化引擎
- `tsx`: TypeScript 执行器
- `dotenv`: 环境变量管理

### 2. 配置环境变量

复制环境变量模板:

```powershell
cd backend\midscene
copy .env.example .env
```

编辑 `.env` 文件，配置你的 LLM API 密钥:

```env
# 如果使用 OpenAI
OPENAI_API_KEY=sk-your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1

# 或使用其他提供商
# ANTHROPIC_API_KEY=your-key
# DASHSCOPE_API_KEY=your-key
```

### 3. 数据库迁移

添加 `executor_type` 字段到数据库:

```powershell
cd backend
python add_executor_type.py
```

### 4. 验证安装

检查 Midscene 是否正确安装:

```python
from app.services.midscene_executor import MidsceneExecutor

executor = MidsceneExecutor("./artifacts")
status = executor.check_installation()
print(status)
# 应该显示: {'installed': True, 'node_modules_exists': True, ...}
```

## 🚀 使用方法

### 创建 Midscene 测试用例

1. **在项目设置中选择执行器**:
   - 创建或编辑项目时，设置 `executor_type` 为 `"midscene"`

2. **使用自然语言创建测试**:
   ```json
   {
     "project_id": 1,
     "natural_language": "打开登录页面，输入用户名 admin，输入密码 123456，点击登录按钮，验证进入仪表板",
     "executor_type": "midscene"
   }
   ```

3. **生成的 Midscene 脚本示例**:
   ```json
   {
     "browser": "chromium",
     "viewport": {"width": 1280, "height": 720},
     "steps": [
       {
         "index": 1,
         "action": "goto",
         "value": "https://example.com/login",
         "description": "打开登录页面"
       },
       {
         "index": 2,
         "action": "aiInput",
         "value": "admin",
         "description": "在用户名输入框中输入"
       },
       {
         "index": 3,
         "action": "aiInput",
         "value": "123456",
         "description": "在密码输入框中输入"
       },
       {
         "index": 4,
         "action": "aiTap",
         "description": "点击登录按钮"
       },
       {
         "index": 5,
         "action": "aiAssert",
         "description": "页面显示用户仪表板"
       }
     ]
   }
   ```

### 双执行器模式

系统支持 Playwright 和 Midscene 双执行器并存:

- **Playwright 模式**: 适合需要精确控制的场景
- **Midscene 模式**: 适合需要灵活性和智能判断的场景

可以在项目级别或测试用例级别选择执行器类型。

## 🔧 架构说明

### 文件结构

```
backend/
├── midscene/                    # Midscene 执行器（Node.js）
│   ├── executor.ts             # 执行器脚本
│   ├── package.json            # Node.js 依赖
│   ├── tsconfig.json           # TypeScript 配置
│   └── .env                    # 环境变量
├── app/
│   ├── services/
│   │   ├── midscene_executor.py  # Python 集成层
│   │   ├── playwright_executor.py # 传统 Playwright 执行器
│   │   └── llm_service.py       # 更新支持 Midscene 脚本生成
│   ├── models/
│   │   ├── project.py          # 添加 executor_type 字段
│   │   └── test_case.py        # 添加 executor_type 字段
│   └── schemas/
│       ├── project.py          # 更新 Schema
│       └── test_case.py        # 更新 Schema
└── add_executor_type.py        # 数据库迁移脚本
```

### 执行流程

```
用户创建测试用例
    ↓
LLM 生成 Midscene 脚本 (generate_midscene_script)
    ↓
保存到数据库 (executor_type='midscene')
    ↓
执行测试时:
    ↓
MidsceneExecutor.execute_script()
    ↓
调用 Node.js executor.ts (通过子进程)
    ↓
Midscene PlaywrightAgent 执行测试
    ↓
返回结果给 Python 后端
    ↓
LLM 分析结果 (analyze_final_result)
```

## 📝 API 变化

### 项目相关

**创建/更新项目**:
```json
{
  "name": "测试项目",
  "base_url": "https://example.com",
  "executor_type": "midscene",  // 新增字段
  "llm_provider": "openai",
  "llm_model": "gpt-4o",
  "llm_api_key": "sk-..."
}
```

### 测试用例相关

**创建测试用例**:
```json
{
  "project_id": 1,
  "name": "登录测试",
  "natural_language": "...",
  "executor_type": "midscene",  // 新增字段
  "expected_result": "成功登录"
}
```

## 🎨 前端集成 (待实现)

需要更新前端界面:

1. **项目表单**: 添加执行器选择下拉框
2. **测试用例表单**: 添加执行器选择选项
3. **测试用例列表**: 显示执行器类型标签
4. **执行结果**: 支持 Midscene 特有的结果展示

## 🧪 测试

### 测试 Midscene 安装

```python
from app.services.midscene_executor import MidsceneExecutor

executor = MidsceneExecutor("./artifacts")

# 检查安装
status = executor.check_installation()
print("安装状态:", status)

# 如果未安装，自动安装
if not status['installed']:
    result = executor.install_dependencies()
    print("安装结果:", result)
```

### 测试执行

```python
# 测试脚本
test_script = {
    "browser": "chromium",
    "viewport": {"width": 1280, "height": 720},
    "steps": [
        {
            "index": 1,
            "action": "goto",
            "value": "https://www.example.com",
            "description": "打开网站"
        },
        {
            "index": 2,
            "action": "aiAssert",
            "description": "页面标题包含 Example Domain"
        }
    ]
}

# 执行
env_vars = {
    "OPENAI_API_KEY": "sk-...",
    "OPENAI_BASE_URL": "https://api.openai.com/v1"
}

result = executor.execute_script(test_script, run_id=999, env_vars=env_vars)
print("执行结果:", result)
```

## 🔍 故障排查

### 问题: npm install 失败

**解决方案**:
1. 确保已安装 Node.js (v16+)
2. 检查网络连接
3. 尝试使用国内镜像: `npm config set registry https://registry.npmmirror.com`

### 问题: Midscene 执行失败

**检查清单**:
1. 环境变量是否正确配置 (`.env` 文件)
2. LLM API 密钥是否有效
3. 查看日志输出确认错误信息
4. 确保 Playwright 浏览器已安装: `npx playwright install chromium`

### 问题: Python 无法调用 Node.js

**解决方案**:
1. 确保 `npx` 在系统 PATH 中
2. 在 PowerShell 中测试: `npx --version`
3. 检查 `midscene_executor.py` 中的路径配置

## 📚 参考资料

- [Midscene 官方文档](https://midscenejs.com)
- [Midscene GitHub](https://github.com/web-infra-dev/midscene)
- [Midscene Playwright 集成指南](https://midscenejs.com/integrate-with-playwright.html)
- [Midscene API 参考](https://midscenejs.com/api.html)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进 Midscene 集成！

## 📄 许可证

本项目与 Midscene 均采用 MIT 许可证。
