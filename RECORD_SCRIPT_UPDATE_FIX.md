# 录制脚本更新修复

## 问题描述

在测试用例详情页使用录制功能后，发现：
- ✅ 标准化步骤的脚本可以正常更新
- ❌ Playwright 脚本没有更新到数据库

## 问题根因

### 原始流程问题
```
用户点击"录制脚本" 
    ↓
录制完成，更新 playwrightScriptJson 
    ↓
调用 handleEdit() 打开编辑框
    ↓
❌ handleEdit() 从 testCase.value 重新读取数据
    ↓
❌ 录制的新脚本被旧数据覆盖
```

### 代码问题
```javascript
// 录制完成后
const stopRecording = async () => {
  // ...
  const data = await response.json()
  
  // 更新了编辑框的值
  playwrightScriptJson.value = JSON.stringify(data.playwright_script, null, 2)
  
  // 打开编辑对话框
  handleEdit()  // ❌ 这里会重新读取 testCase.value，覆盖掉上面的更新
}

// 编辑函数
const handleEdit = () => {
  // ...
  // ❌ 从旧数据重新加载，覆盖录制的新脚本
  playwrightScriptJson.value = JSON.stringify(testCase.value.playwright_script, null, 2)
  
  showEditDialog.value = true
}
```

## 解决方案

### 1. 修改 handleEdit 函数

添加一个可选参数 `skipScriptReload`，用于控制是否重新加载 Playwright 脚本：

```javascript
const handleEdit = (skipScriptReload = false) => {
  editForm.value = {
    name: testCase.value.name,
    description: testCase.value.description,
    natural_language: testCase.value.natural_language,
    expected_result: testCase.value.expected_result
  }
  
  // 将标准化步骤和 Playwright 脚本转为 JSON 字符串以便编辑
  standardStepsJson.value = JSON.stringify(testCase.value.standard_steps, null, 2)
  
  // ✅ 如果 skipScriptReload 为 true，不要重新读取 playwright_script（用于录制后保留新脚本）
  if (!skipScriptReload) {
    playwrightScriptJson.value = JSON.stringify(testCase.value.playwright_script, null, 2)
  }
  
  showEditDialog.value = true
}
```

### 2. 修改 stopRecording 函数

在录制完成后，调用 `handleEdit(true)` 跳过脚本重新加载：

```javascript
const stopRecording = async () => {
  stoppingRecord.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/record/${recordingSessionId.value}/stop`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error('停止录制失败')
    }
    
    const data = await response.json()
    
    // 自动填充到编辑框
    playwrightScriptJson.value = JSON.stringify(data.playwright_script, null, 2)
    
    ElMessage.success('录制完成，脚本已自动生成，请检查后保存')
    
    // 关闭录制对话框
    showRecordDialog.value = false
    recordingSessionId.value = null
    
    // ✅ 自动打开编辑对话框，但不重新加载 playwright_script（保留录制的新脚本）
    handleEdit(true)
  } catch (error) {
    ElMessage.error('停止录制失败: ' + error.message)
  } finally {
    stoppingRecord.value = false
  }
}
```

## 修复后的流程

```
用户点击"录制脚本" 
    ↓
录制完成，更新 playwrightScriptJson 
    ↓
调用 handleEdit(true) 打开编辑框
    ↓
✅ handleEdit(true) 跳过重新加载 Playwright 脚本
    ↓
✅ 保留录制的新脚本
    ↓
用户检查后点击保存
    ↓
✅ 新脚本成功保存到数据库
```

## 对比：TestCaseForm.vue 的实现

在测试用例创建流程（TestCaseForm.vue）中，使用了不同的实现方式，但没有这个问题：

```javascript
// TestCaseForm.vue 使用 reactive 对象
const generatedScript = reactive({
  browser: 'chromium',
  viewport: { width: 1280, height: 720 },
  steps: []
})

// 录制完成后直接更新 reactive 对象
const stopRecording = async () => {
  // ...
  const data = await response.json()
  
  // ✅ 直接更新 reactive 对象，不会被覆盖
  Object.assign(generatedScript, data.playwright_script)
  scriptGenerated.value = true
  // ...
}
```

**为什么没问题？**
- 使用 `Object.assign()` 直接修改 reactive 对象
- 没有"打开编辑框重新加载"的步骤
- `generatedScript` 是唯一的数据源

## 技术要点

### 1. Vue 响应式数据管理
```javascript
// 方式1: ref + JSON 字符串（TestCaseDetail.vue）
const playwrightScriptJson = ref('')  // 用于编辑

// 方式2: reactive 对象（TestCaseForm.vue）
const generatedScript = reactive({})  // 直接操作
```

### 2. 数据流控制
- **TestCaseDetail.vue**: 需要同步 `testCase.value` 和编辑框数据
- **TestCaseForm.vue**: 只有一份数据源，无需同步

### 3. 参数传递控制行为
```javascript
// 使用可选参数控制函数行为
const handleEdit = (skipScriptReload = false) => {
  // 根据参数决定是否重新加载
}

// 不同场景调用
handleEdit()      // 正常编辑，重新加载所有数据
handleEdit(true)  // 录制后编辑，保留新脚本
```

## 测试验证

### 测试步骤
1. 打开一个已存在的测试用例详情页
2. 点击"录制脚本"按钮
3. 输入目标网址并开始录制
4. 在浏览器中进行操作
5. 点击"停止录制"
6. 验证：
   - ✅ 编辑对话框自动打开
   - ✅ Playwright 脚本编辑框显示录制的新脚本
   - ✅ 点击保存后，新脚本成功更新到数据库
   - ✅ 刷新页面，脚本仍然是新的

### 预期结果
- 录制的脚本能正确保存
- 不会被旧数据覆盖
- 用户体验流畅

## 相关文件

- **主要修改**: `frontend/src/views/TestCaseDetail.vue`
  - `handleEdit()` 函数：添加 `skipScriptReload` 参数
  - `stopRecording()` 函数：调用 `handleEdit(true)`

- **参考实现**: `frontend/src/views/TestCaseForm.vue`
  - 使用 reactive 对象的方式

## 最佳实践

### 1. 数据同步模式选择
- **单一数据源**：优先使用 reactive 对象，避免同步问题
- **需要序列化**：使用 ref + JSON，但要注意数据同步

### 2. 函数参数设计
- 使用可选参数控制函数行为
- 默认值保持原有逻辑
- 特殊场景传递 true/false 控制

### 3. 用户体验
- 录制完成后自动打开编辑框
- 提示用户"请检查后保存"
- 保持数据一致性

## 总结

通过添加 `skipScriptReload` 参数，成功解决了录制后脚本被覆盖的问题：

- ✅ 录制的脚本能正确保存到数据库
- ✅ 用户体验更流畅（自动打开编辑框）
- ✅ 代码逻辑清晰，易于维护
- ✅ 向后兼容（默认行为不变）

这个修复确保了录制功能的完整性，让用户可以放心地使用录制方式生成测试脚本！🎉
