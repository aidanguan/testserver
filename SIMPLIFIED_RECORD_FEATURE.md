# 简化版录制功能

## 改进说明

根据用户反馈，将复杂的录制流程简化为更直观的操作方式。

### 改进前（复杂）

```
用户点击"录制脚本"
  ↓
显示复杂的指南（步骤说明、命令等）
  ↓
用户复制命令
  ↓
切换到终端窗口
  ↓
粘贴并执行命令
  ↓
在浏览器中操作
  ↓
回到Inspector复制代码
  ↓
手动转换为JSON
  ↓
切换到网页
  ↓
粘贴到编辑框
```

### 改进后（简化）

```
用户点击"录制脚本"
  ↓
输入目标网址
  ↓
点击"开始录制"
  ↓
在浏览器中操作
  ↓
点击"停止录制"
  ↓
系统自动转换并填充脚本
  ↓
完成！
```

## 功能特点

### 1. **一键启动** ⚡
- 不需要手动复制命令
- 不需要切换到终端
- 点击按钮即可开始

### 2. **自动转换** 🤖
- 自动将Python代码转换为JSON格式
- 自动填充到编辑框
- 无需手动操作

### 3. **智能填充** 💡
- 自动从测试用例描述中提取URL
- 预填充目标网址
- 减少输入工作

## 使用流程

### 步骤1：点击"录制脚本"

在测试用例详情页，点击 **🎥 录制脚本** 按钮。

### 步骤2：输入目标网址

对话框会自动填充网址（从用例描述中提取），或手动输入：

```
目标网址: [ai.42lab.cn        ]
```

支持以下格式：
- `ai.42lab.cn` - 自动添加 https://
- `https://ai.42lab.cn`
- `http://example.com`

### 步骤3：开始录制

点击 **开始录制** 按钮，系统会：
- 在服务器上启动 Playwright
- 打开浏览器窗口
- 打开 Inspector 窗口

### 步骤4：进行操作

在浏览器中进行你的测试操作：
- ✅ 点击按钮
- ✅ 输入文本
- ✅ 选择下拉菜单
- ✅ 导航页面

### 步骤5：停止录制

操作完成后，在对话框中点击 **停止录制** 按钮。

### 步骤6：自动完成

系统会自动：
1. ✅ 停止录制进程
2. ✅ 读取生成的代码
3. ✅ 转换为JSON格式
4. ✅ 打开编辑框
5. ✅ 填充到 Playwright 脚本字段

你只需要点击 **保存** 即可！

## 界面展示

### 录制对话框（开始前）

```
┌──────────────────────────────────┐
│ 🎥 录制脚本                       │
├──────────────────────────────────┤
│ ℹ️ 点击'开始录制'后，系统会打开  │
│    浏览器窗口                     │
├──────────────────────────────────┤
│                                  │
│ 目标网址: [ai.42lab.cn        ]  │
│                                  │
│ ⚠️ 提示：                        │
│  • 录制会在服务器上打开浏览器窗口 │
│  • 如果是远程服务器，需要有桌面环境│
│  • 建议在本地环境使用此功能      │
│                                  │
├──────────────────────────────────┤
│        [取消]    [开始录制]       │
└──────────────────────────────────┘
```

### 录制对话框（录制中）

```
┌──────────────────────────────────┐
│ 🎥 录制脚本                       │
├──────────────────────────────────┤
│                                  │
│       ✓  正在录制                │
│                                  │
│   请在弹出的浏览器窗口中进行操作   │
│                                  │
│        [停止录制]                │
│                                  │
│ ℹ️ 操作步骤：                    │
│  1. 在浏览器中进行你的测试操作    │
│  2. Playwright Inspector会自动记录 │
│  3. 操作完成后点击上面的"停止录制" │
│  4. 系统会自动转换并填充脚本      │
│                                  │
├──────────────────────────────────┤
│            [取消录制]             │
└──────────────────────────────────┘
```

## 自动转换功能

### 支持的转换

| Playwright 代码 | 自动转换为 |
|----------------|-----------|
| `page.goto("url")` | `{"action": "goto", "value": "url"}` |
| `page.fill("#id", "text")` | `{"action": "fill", "selector": "#id", "value": "text"}` |
| `page.click("button")` | `{"action": "click", "selector": "button"}` |
| `page.select_option("#id", "value")` | `{"action": "select", "selector": "#id", "value": "value"}` |
| `page.wait_for_selector("#id")` | `{"action": "waitForSelector", "selector": "#id"}` |
| `page.wait_for_timeout(2000)` | `{"action": "waitTime", "duration": 2000}` |

### 自动添加的字段

- `index` - 步骤编号（自动递增）
- `screenshot` - 截图标志（默认 true）
- `description` - 步骤描述（自动生成）

### 转换示例

**录制生成的Python代码**:
```python
page.goto("https://ai.42lab.cn/")
page.fill("#username", "Aidan")
page.fill("#password", "Deep2025")
page.click("button:has-text('登录')")
```

**自动转换为JSON**:
```json
{
  "browser": "chromium",
  "viewport": {"width": 1280, "height": 720},
  "steps": [
    {
      "index": 1,
      "action": "goto",
      "selector": null,
      "value": "https://ai.42lab.cn/",
      "description": "打开页面 https://ai.42lab.cn/",
      "screenshot": true
    },
    {
      "index": 2,
      "action": "fill",
      "selector": "#username",
      "value": "Aidan",
      "description": "输入: Aidan",
      "screenshot": true
    },
    {
      "index": 3,
      "action": "fill",
      "selector": "#password",
      "value": "Deep2025",
      "description": "输入: Deep2025",
      "screenshot": true
    },
    {
      "index": 4,
      "action": "click",
      "selector": "button:has-text('登录')",
      "value": null,
      "description": "点击元素",
      "screenshot": true
    }
  ]
}
```

## 后端实现

### 新增API端点

**文件**: `backend/app/api/endpoints/recorder.py`

#### 1. POST /api/record/start
启动录制会话

**请求**:
```json
{
  "target_url": "https://ai.42lab.cn/",
  "project_id": 1
}
```

**响应**:
```json
{
  "session_id": "uuid",
  "status": "recording",
  "message": "录制已启动"
}
```

#### 2. POST /api/record/{session_id}/stop
停止录制会话

**响应**:
```json
{
  "status": "stopped",
  "playwright_code": "page.goto(...)",
  "playwright_script": {
    "browser": "chromium",
    "steps": [...]
  }
}
```

### 转换器实现

```python
def convert_playwright_to_json(playwright_code: str) -> Dict[str, Any]:
    """
    将Playwright Python代码转换为JSON格式
    """
    steps = []
    step_index = 1
    
    for line in playwright_code.split('\n'):
        # 解析不同的操作类型
        if 'page.goto(' in line:
            # 提取URL并生成JSON步骤
            ...
        elif 'page.fill(' in line:
            # 提取selector和value并生成JSON步骤
            ...
        # ... 更多操作类型
    
    return {
        "browser": "chromium",
        "viewport": {"width": 1280, "height": 720},
        "steps": steps
    }
```

## 注意事项

⚠️ **环境要求**:
- 服务器需要有桌面环境（或本地运行）
- 已安装 Playwright 浏览器

⚠️ **转换限制**:
- 目前支持常见的操作类型
- 复杂的操作可能需要手动调整
- 建议录制后检查生成的JSON

⚠️ **最佳实践**:
- 在本地环境使用此功能
- 录制简单清晰的操作流程
- 使用稳定的选择器（id、data-testid）

## 优势对比

### 改进前
❌ 需要7-8个步骤
❌ 需要在多个窗口间切换
❌ 需要手动转换JSON
❌ 容易出错

### 改进后
✅ 只需要3-4个点击
✅ 全程在Web界面操作
✅ 自动转换JSON
✅ 流程简单清晰

## 相关文档

- [`RECORD_FEATURE_SUMMARY.md`](./RECORD_FEATURE_SUMMARY.md) - 原始录制功能
- [Playwright Codegen 文档](https://playwright.dev/docs/codegen)

## 更新日期

2025-10-23
