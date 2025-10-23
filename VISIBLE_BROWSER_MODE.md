# 可视化浏览器执行模式

## 功能说明

**改进前**：Playwright 在无头模式（headless）下执行，看不到浏览器窗口  
**改进后**：Playwright 在有头模式下执行，可以实时看到浏览器操作过程

## 修改内容

### 文件修改

**文件**: `backend/app/services/playwright_executor.py`

**修改前**:
```python
# 获取浏览器类型
browser_type = script.get("browser", "chromium")
if browser_type == "chromium":
    self.browser = self.playwright.chromium.launch(headless=True)  # 无头模式
elif browser_type == "firefox":
    self.browser = self.playwright.firefox.launch(headless=True)
elif browser_type == "webkit":
    self.browser = self.playwright.webkit.launch(headless=True)
else:
    self.browser = self.playwright.chromium.launch(headless=True)
```

**修改后**:
```python
# 获取浏览器类型
browser_type = script.get("browser", "chromium")
if browser_type == "chromium":
    self.browser = self.playwright.chromium.launch(headless=False)  # 有头模式，可以看到浏览器
elif browser_type == "firefox":
    self.browser = self.playwright.firefox.launch(headless=False)
elif browser_type == "webkit":
    self.browser = self.playwright.webkit.launch(headless=False)
else:
    self.browser = self.playwright.chromium.launch(headless=False)
```

## 使用效果

### 执行测试时

1. **点击执行测试按钮**
2. **后台服务器上会弹出浏览器窗口** 🌐
3. **可以实时看到测试执行过程**：
   - 页面导航
   - 表单填写
   - 按钮点击
   - 页面跳转
   - 等待过程
   - 截图时刻

### 优势

✅ **直观可视** - 实时观察测试执行过程  
✅ **易于调试** - 发现问题时可以看到实际页面状态  
✅ **验证准确性** - 确认测试步骤是否按预期执行  
✅ **演示效果** - 可以录屏展示测试过程

### 注意事项

⚠️ **服务器环境**:
- 如果后端运行在**本地**，浏览器会在本地电脑上弹出 ✅
- 如果后端运行在**远程服务器**（Linux无桌面环境），需要配置X11转发或保持无头模式 ❌

⚠️ **性能影响**:
- 有头模式比无头模式**稍慢**（渲染界面需要额外资源）
- 建议在**开发调试**时使用有头模式
- **生产环境**或**CI/CD**管道建议使用无头模式

⚠️ **并发执行**:
- 有头模式下同时执行多个测试会打开多个浏览器窗口
- 建议控制并发数量，避免资源占用过高

## 切换回无头模式

如果需要切回无头模式（不显示浏览器），将 `headless=False` 改回 `headless=True` 即可。

## 进阶配置

### 慢动作模式（可选）

如果想让操作更慢，便于观察，可以添加 `slow_mo` 参数：

```python
self.browser = self.playwright.chromium.launch(
    headless=False, 
    slow_mo=500  # 每个操作延迟500毫秒
)
```

### 保持浏览器打开（可选）

测试完成后自动关闭浏览器，如果想保持打开：

```python
# 在 _cleanup 方法中注释掉关闭浏览器的代码
def _cleanup(self):
    """清理资源"""
    try:
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        # if self.browser:
        #     self.browser.close()  # 注释掉这行，浏览器保持打开
        if self.playwright:
            self.playwright.stop()
    except Exception as e:
        print(f"清理资源时出错: {e}")
```

## 测试步骤

1. **后端已自动重载**，无需重启
2. **执行任意测试用例**
3. **观察浏览器窗口**：
   - 浏览器会自动弹出
   - 看到页面导航、输入、点击等操作
   - 每个步骤执行后会截图
   - 视觉分析在后台进行（不影响浏览器显示）
4. **测试完成后浏览器自动关闭**

## 截图示例

执行过程中你会看到：

```
1️⃣ 浏览器打开
2️⃣ 导航到 https://ai.42lab.cn/
3️⃣ 输入用户名 "Aidan"
4️⃣ 输入密码 "******"
5️⃣ 点击登录按钮
6️⃣ 页面跳转
7️⃣ 测试完成，浏览器关闭
```

## 修改日期

2025-10-23

## 相关文档

- [`REALTIME_VISION_ANALYSIS.md`](./REALTIME_VISION_ANALYSIS.md) - 实时视觉分析功能
- [`VISION_LLM_ANALYSIS.md`](./VISION_LLM_ANALYSIS.md) - 视觉大模型分析功能
