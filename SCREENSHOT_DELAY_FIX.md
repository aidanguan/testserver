# Playwright 截图延迟优化

## 问题描述

在测试执行过程中，截图操作执行得太快，导致页面元素还未完全加载渲染就已经截图，影响了测试结果的准确性和可靠性。

## 解决方案

在每个步骤操作完成后，等待 3 秒让页面完全加载和渲染，然后再进行截图。

## 修改内容

### 1. Playwright 执行器 - 添加截图延迟

**文件**: `backend/app/services/playwright_executor.py`

**修改位置**: `_execute_step()` 方法中的截图逻辑

**修改前**:
```python
# 默认截屏（不再进行单步视觉分析，只保存截图供后续整体分析）
if step.get("screenshot", True) and action != "screenshot":
    screenshot_name = f"step_{step['index']}.png"
    screenshot_path = os.path.join(screenshots_path, screenshot_name)
    self.page.screenshot(path=screenshot_path, full_page=True)
    step_result["screenshot_path"] = screenshot_path
```

**修改后**:
```python
# 默认截屏（不再进行单步视觉分析，只保存截图供后续整体分析）
if step.get("screenshot", True) and action != "screenshot":
    # 等待3秒让页面完全加载后再截图
    self.page.wait_for_timeout(3000)
    screenshot_name = f"step_{step['index']}.png"
    screenshot_path = os.path.join(screenshots_path, screenshot_name)
    self.page.screenshot(path=screenshot_path, full_page=True)
    step_result["screenshot_path"] = screenshot_path
```

### 2. LLM 脚本生成提示词更新

**文件**: `backend/app/services/llm_service.py`

**修改位置**: `_build_case_to_script_prompt()` 方法

**添加说明**:
```
重要提示：
- 系统会在每个步骤执行后自动等待3秒再截图，确保页面完全加载
- 你不需要在每个步骤后手动添加waitTime，除非有特殊需要
```

### 3. 录制脚本转换提示词更新

**文件**: `backend/app/api/endpoints/recorder.py`

**修改位置**: `convert_playwright_to_json()` 函数中的 LLM 提示词

**添加说明**:
```
重要提示：
- 系统会在每个步骤执行后自动等待3秒再截图，确保页面完全加载
- 你不需要在每个步骤后手动添加waitTime，除非有特殊需要
```

## 影响范围

### 正面影响

1. **截图质量提升**: 页面元素完全加载后再截图，确保截图内容完整准确
2. **视觉分析准确性**: LLM 视觉分析可以获得更准确的页面状态
3. **测试稳定性**: 减少因页面加载不完全导致的测试失败
4. **用户体验**: 有头模式下用户可以清楚看到每个步骤的执行过程

### 时间开销

- 每个步骤增加 3 秒延迟（仅在需要截图时）
- 例如：5 个步骤的测试，增加约 15 秒执行时间
- 权衡：时间换准确性，这是值得的

## 使用说明

### 1. 自动生成的脚本

使用 LLM 从自然语言生成的脚本会自动遵循这个规则：
- LLM 不会在每个步骤后添加额外的 `waitTime` 动作
- 系统会在截图前自动等待 3 秒

### 2. 录制生成的脚本

通过 Playwright Codegen 录制的脚本转换时：
- LLM 会被告知系统的自动等待机制
- 不会生成冗余的等待步骤
- 除非用户在录制时手动添加了等待

### 3. 手动编辑的脚本

用户手动编辑脚本时：
- 不需要为每个步骤手动添加 `waitTime: 3000`
- 系统会自动处理
- 如果需要额外等待（超过 3 秒），可以手动添加 `waitTime` 步骤

## 特殊场景处理

### 场景1: 某个步骤需要更长等待时间

```json
{
  "index": 3,
  "action": "click",
  "selector": "#submit-button",
  "description": "点击提交按钮",
  "screenshot": true
},
{
  "index": 4,
  "action": "waitTime",
  "duration": 5000,
  "description": "等待5秒处理提交",
  "screenshot": false
}
```

在这种情况下：
- 第 3 步：点击 → 等待 3 秒 → 截图
- 第 4 步：等待 5 秒（不截图）
- 总等待时间：8 秒

### 场景2: 不需要截图的步骤

```json
{
  "index": 2,
  "action": "fill",
  "selector": "#username",
  "value": "admin",
  "description": "输入用户名",
  "screenshot": false
}
```

在这种情况下：
- 执行填充操作
- **不会等待 3 秒**（因为 `screenshot: false`）
- 立即执行下一步

## 技术细节

### wait_for_timeout() 方法

```python
self.page.wait_for_timeout(3000)  # 等待 3000 毫秒（3 秒）
```

- 这是 Playwright 的同步等待方法
- 阻塞执行直到时间到达
- 不依赖于任何页面状态，是固定延迟

### 为什么是 3 秒？

- **1 秒**：可能不够，某些动画或异步加载需要更多时间
- **3 秒**：经验值，足够大多数页面完成加载和渲染
- **5 秒及以上**：可能过长，影响测试效率

如果 3 秒不够，可以在配置中调整或使用 `waitForSelector` 等待特定元素出现。

## 测试验证

### 验证步骤

1. 创建一个包含多个步骤的测试用例
2. 执行测试并观察有头浏览器
3. 检查每个步骤是否：
   - 执行操作
   - 等待 3 秒
   - 截图
4. 检查截图质量，确保页面完全加载

### 预期结果

- ✅ 每个步骤执行后有明显的 3 秒暂停
- ✅ 截图中的页面元素完全加载渲染
- ✅ 视觉分析结果更准确
- ✅ 测试执行时间增加（每步约 3 秒）

## 后续优化建议

### 1. 可配置延迟时间

在项目或用例级别配置截图延迟：
```json
{
  "screenshot_delay": 3000,
  "steps": [...]
}
```

### 2. 智能等待

使用 Playwright 的智能等待机制：
- `page.wait_for_load_state('networkidle')` - 等待网络空闲
- `page.wait_for_selector()` - 等待特定元素出现
- 结合固定延迟和智能等待

### 3. 步骤级别延迟

允许每个步骤指定自己的延迟时间：
```json
{
  "index": 1,
  "action": "click",
  "selector": "#button",
  "description": "点击按钮",
  "screenshot": true,
  "screenshot_delay": 5000
}
```

## 总结

这次修改通过在截图前添加固定的 3 秒延迟，显著提升了：
1. 截图质量
2. 视觉分析准确性
3. 测试稳定性

虽然增加了测试执行时间，但这是值得的权衡，因为准确性比速度更重要。

---

**修改日期**: 2025-10-23  
**修改人**: Qoder AI Assistant  
**影响版本**: v1.0+
