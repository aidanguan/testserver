# LLM 录制脚本转换功能

## 功能概述

系统现在支持使用 LLM 将 Playwright Codegen 录制的 Python 代码智能转换为标准化的 JSON 格式测试脚本。这比简单的规则匹配更加准确和灵活。

## 工作流程

### 1. 启动录制
用户在测试用例详情页点击"录制脚本"按钮：
- 输入目标网站 URL
- 点击"开始录制"
- 系统在后台启动 Playwright Codegen，打开浏览器窗口

### 2. 录制操作
- 在浏览器中进行需要的操作（点击、输入、导航等）
- Playwright Codegen 自动记录所有操作并生成 Python 代码

### 3. 停止录制并转换
点击"停止录制"按钮时：
- 系统终止 Playwright Codegen 进程
- 读取录制生成的 Python 代码
- **使用 LLM 智能分析并转换代码**
- 自动填充到测试脚本编辑框

## LLM 转换优势

### 相比规则转换的优势
1. **更准确的理解**：LLM 能理解复杂的代码结构和语义
2. **更好的描述**：自动生成中文描述，说明每个步骤的作用
3. **更多操作支持**：除了基础操作，还能识别更多 Playwright API
4. **容错性强**：即使代码格式不标准，也能正确解析

### 支持的操作类型
LLM 转换能识别并转换以下操作：
- `goto` - 导航到URL
- `click` - 点击元素
- `fill` - 填充输入框
- `select` - 选择下拉选项
- `waitForSelector` - 等待元素出现
- `waitTime` - 等待固定时间
- `press` - 按键（如 Enter）
- `check` / `uncheck` - 复选框操作

## 技术实现

### 转换函数
```python
def convert_playwright_to_json(playwright_code: str, project: Project) -> Dict[str, Any]:
    """
    使用LLM将Playwright Python代码转换为JSON格式
    """
```

### 转换逻辑
1. **检查 LLM 配置**：如果项目配置了 LLM（provider、model、api_key）
2. **调用 LLM**：发送 prompt 让 LLM 分析录制代码
3. **解析响应**：提取 JSON 格式的脚本配置
4. **回退方案**：如果 LLM 转换失败，使用简单的规则转换

### Prompt 设计
LLM 接收的 prompt 包含：
- 录制的 Python 代码
- 期望的 JSON 格式说明
- 支持的操作类型列表
- 示例输出

## 配置要求

### 项目 LLM 配置
要使用 LLM 转换功能，项目需要配置：
- `llm_provider`: OpenAI、DashScope 等
- `llm_model`: 模型名称（建议使用 gpt-4、qwen-plus 等）
- `llm_api_key`: API 密钥
- `llm_base_url`: （可选）自定义 API 地址

### 推荐配置
```json
{
  "provider": "openai",
  "model": "gpt-4",
  "temperature": 0.3,
  "max_tokens": 2000
}
```

低 temperature (0.3) 确保转换结果稳定可靠。

## 使用示例

### 输入：Playwright 录制代码
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://ai.42lab.cn")
    page.fill("#username", "admin")
    page.fill("#password", "admin")
    page.click("#login-button")
    page.wait_for_selector(".dashboard")
    browser.close()
```

### 输出：JSON 格式脚本
```json
{
  "browser": "chromium",
  "viewport": {
    "width": 1280,
    "height": 720
  },
  "steps": [
    {
      "index": 1,
      "action": "goto",
      "selector": null,
      "value": "https://ai.42lab.cn",
      "description": "打开网站首页",
      "screenshot": true
    },
    {
      "index": 2,
      "action": "fill",
      "selector": "#username",
      "value": "admin",
      "description": "输入用户名",
      "screenshot": true
    },
    {
      "index": 3,
      "action": "fill",
      "selector": "#password",
      "value": "admin",
      "description": "输入密码",
      "screenshot": true
    },
    {
      "index": 4,
      "action": "click",
      "selector": "#login-button",
      "value": null,
      "description": "点击登录按钮",
      "screenshot": true
    },
    {
      "index": 5,
      "action": "waitForSelector",
      "selector": ".dashboard",
      "value": null,
      "description": "等待仪表板加载",
      "screenshot": true
    }
  ]
}
```

## 回退机制

如果 LLM 转换失败（网络问题、配置错误等），系统会自动回退到简单的规则转换：

```python
def _simple_convert(playwright_code: str) -> Dict[str, Any]:
    """简单的规则转换（回退方案）"""
```

这确保了即使在 LLM 不可用时，录制功能仍然可以正常工作。

## API 端点

### POST /api/record/{session_id}/stop
停止录制并转换脚本

**响应：**
```json
{
  "status": "stopped",
  "playwright_code": "原始 Python 代码",
  "playwright_script": {
    "browser": "chromium",
    "viewport": {...},
    "steps": [...]
  }
}
```

## 前端集成

前端在接收到转换后的脚本后：
1. 自动填充到 `playwrightScriptJson` 编辑框
2. 关闭录制对话框
3. 打开编辑对话框供用户审核和保存

```javascript
const data = await response.json()
playwrightScriptJson.value = JSON.stringify(data.playwright_script, null, 2)
showRecordDialog.value = false
handleEdit()
```

## 优化建议

### 1. 提高转换质量
- 使用更强大的模型（如 GPT-4）
- 调整 prompt 以适应特定场景
- 收集失败案例并改进 prompt

### 2. 用户体验
- 显示转换进度
- 提供转换预览
- 支持手动调整

### 3. 性能优化
- 缓存常见的转换结果
- 批量处理多个录制会话
- 异步转换避免阻塞

## 故障排查

### LLM 转换失败
1. **检查项目配置**：确保 LLM 配置正确
2. **查看日志**：后端会打印详细错误信息
3. **验证 API**：测试 LLM API 是否可访问
4. **检查 prompt**：确保 prompt 格式正确

### 转换结果不准确
1. **调整 temperature**：降低到 0.1-0.3
2. **更换模型**：尝试更强大的模型
3. **优化 prompt**：添加更多示例
4. **手动修正**：用户可以在编辑框中调整

## 总结

LLM 录制脚本转换功能大大提升了测试脚本的生成质量和效率：
- ✅ 智能理解录制代码
- ✅ 自动生成中文描述
- ✅ 支持更多操作类型
- ✅ 提供回退方案保证可用性
- ✅ 无缝集成到现有工作流

这使得非技术用户也能快速创建高质量的自动化测试脚本！
