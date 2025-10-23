# Playwright 录制脚本功能

## 功能概述

通过 Playwright Codegen 工具录制浏览器操作，自动生成测试脚本，然后手动转换为系统所需的 JSON 格式。

## 🎯 使用场景

- ✅ 不确定如何编写 Playwright 脚本
- ✅ 需要快速生成测试步骤
- ✅ 想要精确获取元素选择器
- ✅ LLM 生成的脚本不够准确，需要手动调整

## 📋 使用步骤

### 1. 点击"录制脚本"按钮

在测试用例详情页面，点击 **🎥 录制脚本** 按钮，打开录制指南对话框。

### 2. 复制并执行录制命令

对话框中会显示录制命令，例如：

```bash
python -m playwright codegen https://ai.42lab.cn/
```

**复制命令并在服务器终端执行**（或本地终端执行）

### 3. 在 Playwright Inspector 中录制操作

命令执行后会自动打开：
- **浏览器窗口** - 用于操作
- **Playwright Inspector 窗口** - 显示生成的代码

**在浏览器中进行操作**：
1. 导航到目标页面
2. 点击按钮
3. 填写表单
4. 选择下拉菜单
5. 等待元素出现
6. 等等...

**Inspector 会实时显示生成的代码**，例如：

```python
page.goto("https://ai.42lab.cn/")
page.fill("#username", "Aidan")
page.fill("#password", "Deep2025")
page.click("button:has-text('登录')")
```

### 4. 优化选择器（可选）

在 Inspector 中，你可以：
- 点击元素旁边的选择器
- 手动修改为更稳定的选择器
- 推荐使用：`id`、`data-testid`、`aria-label` 等

### 5. 复制生成的代码

操作完成后，从 Inspector 复制生成的代码。

### 6. 停止录制

在终端按 `Ctrl+C` 停止录制。

### 7. 转换为 JSON 格式

将 Playwright 代码转换为系统所需的 JSON 格式。

#### 转换对照表

| Playwright 代码 | JSON 格式 |
|----------------|-----------|
| `page.goto("URL")` | `{"action": "goto", "value": "URL", "description": "打开页面"}` |
| `page.fill("selector", "value")` | `{"action": "fill", "selector": "selector", "value": "value", "description": "输入内容"}` |
| `page.click("selector")` | `{"action": "click", "selector": "selector", "description": "点击按钮"}` |
| `page.select_option("selector", "value")` | `{"action": "select", "selector": "selector", "value": "value", "description": "选择选项"}` |
| `page.wait_for_selector("selector")` | `{"action": "waitForSelector", "selector": "selector", "description": "等待元素"}` |

#### 完整 JSON 示例

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
      "value": "https://ai.42lab.cn/",
      "description": "打开登录页面",
      "screenshot": true
    },
    {
      "index": 2,
      "action": "fill",
      "selector": "#username",
      "value": "Aidan",
      "description": "输入用户名",
      "screenshot": true
    },
    {
      "index": 3,
      "action": "fill",
      "selector": "#password",
      "value": "Deep2025",
      "description": "输入密码",
      "screenshot": true
    },
    {
      "index": 4,
      "action": "click",
      "selector": "button:has-text('登录')",
      "description": "点击登录按钮",
      "screenshot": true
    },
    {
      "index": 5,
      "action": "waitTime",
      "duration": 2000,
      "description": "等待2秒",
      "screenshot": true
    }
  ]
}
```

### 8. 粘贴到编辑框

1. 点击对话框底部的 **打开编辑框** 按钮
2. 在 **Playwright 脚本** 编辑框中粘贴转换好的 JSON
3. 点击 **保存** 按钮

## 💡 高级技巧

### 使用稳定的选择器

❌ **不推荐**（容易变化）：
```python
page.click("div > div > button:nth-child(3)")
page.fill("input[type='text']")
```

✅ **推荐**（稳定可靠）：
```python
page.click("#login-button")
page.fill("[data-testid='username-input']")
page.click("button[aria-label='提交']")
```

### 在 Inspector 中修改选择器

1. 点击代码中的选择器
2. 在弹出窗口中输入新的选择器
3. 测试是否能正确选中元素
4. 确认后更新

### 添加断言

录制不会自动生成断言，需要手动添加：

```json
{
  "index": 6,
  "action": "assertVisible",
  "selector": ".dashboard",
  "description": "验证进入主页",
  "screenshot": true
}
```

### 添加等待

有时需要手动添加等待：

```json
{
  "index": 5,
  "action": "waitTime",
  "duration": 2000,
  "description": "等待页面加载",
  "screenshot": false
}
```

## 🔧 常见问题

### Q1: 为什么录制命令执行后没有反应？

**A**: 确保已安装 Playwright 浏览器：
```bash
python -m playwright install chromium
```

### Q2: 录制的选择器太复杂怎么办？

**A**: 在 Inspector 中手动修改为更简单的选择器，或者在页面元素上添加 `data-testid` 属性。

### Q3: 如何录制文件上传？

**A**: Playwright Codegen 会自动生成文件上传代码：
```python
page.set_input_files("input[type='file']", "path/to/file.png")
```

转换为 JSON 后需要手动处理文件路径。

### Q4: 录制的代码太长怎么办？

**A**: 
1. 只录制关键步骤
2. 删除不必要的操作
3. 合并相似的步骤

### Q5: 可以在 Windows 上录制吗？

**A**: 可以！Playwright 支持 Windows、Mac、Linux。

## 📝 注意事项

⚠️ **重要提示**:

1. **本地 vs 服务器**:
   - 建议在本地执行录制命令
   - 服务器需要有桌面环境才能显示浏览器

2. **手动转换**:
   - 录制生成的是 Python 代码
   - 需要手动转换为 JSON 格式
   - 未来可能会提供自动转换工具

3. **选择器稳定性**:
   - 优先使用 `id`、`data-testid`
   - 避免使用 `nth-child`、复杂的 CSS 选择器

4. **截图设置**:
   - 每个步骤默认 `screenshot: true`
   - 可以根据需要调整

5. **步骤索引**:
   - 必须从 1 开始
   - 必须连续递增

## 🚀 快速示例

### 示例：录制登录流程

**1. 执行录制命令**:
```bash
python -m playwright codegen https://ai.42lab.cn/
```

**2. 在浏览器中操作**:
- 输入用户名
- 输入密码
- 点击登录

**3. 生成的代码**:
```python
page.goto("https://ai.42lab.cn/")
page.fill("#username", "Aidan")
page.fill("#password", "Deep2025")
page.click("button:has-text('登录')")
```

**4. 转换为 JSON**:
```json
{
  "browser": "chromium",
  "viewport": {"width": 1280, "height": 720},
  "steps": [
    {
      "index": 1,
      "action": "goto",
      "value": "https://ai.42lab.cn/",
      "description": "打开页面",
      "screenshot": true
    },
    {
      "index": 2,
      "action": "fill",
      "selector": "#username",
      "value": "Aidan",
      "description": "输入用户名",
      "screenshot": true
    },
    {
      "index": 3,
      "action": "fill",
      "selector": "#password",
      "value": "Deep2025",
      "description": "输入密码",
      "screenshot": true
    },
    {
      "index": 4,
      "action": "click",
      "selector": "button:has-text('登录')",
      "description": "点击登录",
      "screenshot": true
    }
  ]
}
```

**5. 粘贴到编辑框并保存**

## 🔗 相关资源

- [Playwright Codegen 官方文档](https://playwright.dev/docs/codegen)
- [Playwright 选择器文档](https://playwright.dev/docs/selectors)
- [Playwright 最佳实践](https://playwright.dev/docs/best-practices)

## 📅 更新日期

2025-10-23
