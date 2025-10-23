# 录制脚本功能实现总结

## 功能说明

为测试用例添加了"录制脚本"功能，通过 Playwright Codegen 工具录制浏览器操作，生成测试脚本。

## 实现内容

### 后端实现

#### 1. 新增 API 端点

**文件**: `backend/app/api/endpoints/recorder.py`

- `GET /api/record/guide` - 获取录制指南
- 提供录制步骤说明、命令示例、最佳实践

#### 2. 路由注册

**文件**: `backend/main.py`

```python
from app.api.endpoints import recorder
app.include_router(recorder.router, prefix="/api")
```

### 前端实现

#### 修改文件

**文件**: `frontend/src/views/TestCaseDetail.vue`

#### 新增功能

1. **录制按钮**
   - 在测试用例详情页添加 "🎥 录制脚本" 按钮
   - 位置：编辑按钮和执行按钮之间

2. **录制指南对话框**
   - 分步骤展示录制流程
   - 提供可复制的录制命令
   - JSON 格式示例
   - 使用技巧和注意事项

3. **核心功能**
   - 自动生成录制命令（根据测试用例的目标URL）
   - 一键复制命令到剪贴板
   - 直接打开编辑框以粘贴生成的脚本

## 使用流程

```
用户点击"录制脚本"
    ↓
显示录制指南对话框
    ↓
用户复制录制命令
    ↓
在终端执行命令
    ↓
Playwright 打开浏览器 + Inspector
    ↓
用户在浏览器中操作
    ↓
Inspector 自动生成代码
    ↓
用户复制代码
    ↓
停止录制 (Ctrl+C)
    ↓
手动转换为 JSON 格式
    ↓
点击"打开编辑框"
    ↓
粘贴 JSON 到编辑框
    ↓
保存
```

## 技术要点

### Playwright Codegen 命令

```bash
python -m playwright codegen <URL>
```

**参数说明**:
- `<URL>` - 目标网站地址
- `--target python-async` - 生成 Python 异步代码
- `-o <file>` - 输出到文件

### 转换映射

| Playwright 操作 | JSON 格式 |
|----------------|-----------|
| `page.goto(url)` | `{"action": "goto", "value": url}` |
| `page.fill(selector, value)` | `{"action": "fill", "selector": selector, "value": value}` |
| `page.click(selector)` | `{"action": "click", "selector": selector}` |
| `page.select_option(selector, value)` | `{"action": "select", "selector": selector, "value": value}` |
| `page.wait_for_selector(selector)` | `{"action": "waitForSelector", "selector": selector}` |

## 界面展示

### 录制指南对话框

```
┌─────────────────────────────────────────┐
│ 🎥 Playwright 录制脚本指南               │
├─────────────────────────────────────────┤
│ ⚠️ 录制功能需要在服务器终端手动执行      │
├─────────────────────────────────────────┤
│                                         │
│ [执行录制命令] → [操作浏览器] → [复制代码] → [粘贴到编辑框] │
│                                         │
│ 📝 步骤说明:                             │
│  1. 在服务器终端执行以下命令：            │
│     ┌──────────────────────────┬──────┐  │
│     │python -m playwright...   │复制  │  │
│     └──────────────────────────┴──────┘  │
│                                         │
│  2. 浏览器和Inspector窗口会自动打开      │
│  3. 在浏览器中进行操作...                │
│  ... 更多步骤 ...                       │
│                                         │
│ 💡 提示:                                │
│  • 使用稳定的选择器                      │
│  • 可以手动修改选择器                    │
│                                         │
│ 📝 JSON 格式示例:                        │
│  {...示例代码...}                        │
│                                         │
├─────────────────────────────────────────┤
│           [关闭]    [打开编辑框]          │
└─────────────────────────────────────────┘
```

## 优势

✅ **降低门槛** - 不需要手写 Playwright 代码  
✅ **精确选择器** - 自动生成元素选择器  
✅ **快速生成** - 几分钟即可完成录制  
✅ **可视化** - 直接看到操作效果  
✅ **可编辑** - 生成后可以手动调整

## 限制

⚠️ **需要手动转换** - 生成的是 Python 代码，需要转为 JSON  
⚠️ **需要桌面环境** - 服务器需要支持显示浏览器  
⚠️ **选择器可能不稳定** - 需要手动优化选择器  
⚠️ **无自动断言** - 断言需要手动添加

## 未来改进

📋 **计划中的功能**:

1. **自动转换器** - Python 代码自动转 JSON
2. **录制会话管理** - 在系统中管理录制会话
3. **远程录制** - 通过 VNC 或远程桌面录制
4. **智能选择器** - 自动优化选择器
5. **录制回放** - 直接在系统中回放录制

## 相关文档

- [`PLAYWRIGHT_RECORD_GUIDE.md`](./PLAYWRIGHT_RECORD_GUIDE.md) - 详细使用指南
- [Playwright Codegen 官方文档](https://playwright.dev/docs/codegen)

## 修改文件清单

### 后端
- ✅ `backend/app/api/endpoints/recorder.py` - 录制API（新建）
- ✅ `backend/main.py` - 注册路由

### 前端
- ✅ `frontend/src/views/TestCaseDetail.vue` - 添加录制功能

### 文档
- ✅ `PLAYWRIGHT_RECORD_GUIDE.md` - 使用指南（新建）
- ✅ `RECORD_FEATURE_SUMMARY.md` - 功能总结（新建）

## 日期

2025-10-23
