# 可编辑的测试脚本功能

## 功能概述

测试用例编辑功能现在支持直接编辑标准化步骤和 Playwright 脚本，同时保留使用 LLM 自动生成的选项。

## 核心特性

### 1. **手动编辑脚本** ✍️
- ✅ 可以直接编辑标准化测试步骤（JSON 格式）
- ✅ 可以直接编辑 Playwright 脚本（JSON 格式）
- ✅ JSON 格式验证，防止保存无效数据
- ✅ 格式化显示，易于阅读和编辑

### 2. **自动生成脚本** 🤖
- ✅ 点击"重新生成脚本"按钮使用 LLM 自动生成
- ✅ 生成后在表单中显示，可以检查和修改
- ✅ 不会立即保存，需要手动点击"保存"确认

### 3. **灵活的工作流程** 🔄
- ✅ 纯手动编辑：直接修改 JSON，点击保存
- ✅ 自动生成后微调：点击重新生成，检查后微调，保存
- ✅ 混合模式：部分手动，部分使用 LLM 生成

## 用户界面

### 编辑对话框布局

```
┌─────────────────────────────────────────┐
│ ℹ️ 可以手动编辑步骤和脚本，或点击'重新    │
│   生成脚本'按钮使用 LLM 自动生成          │
├─────────────────────────────────────────┤
│ 用例名称: [___________________]          │
│ 描述:     [___________________]          │
│ 自然语言: [___________________]          │
│           [___________________]          │
│ 预期结果: [___________________]          │
├─────────────────────────────────────────┤
│ 标准化步骤:                              │
│ [                                 ]      │
│ [   JSON 格式的步骤数组            ]      │
│ [                                 ]      │
│ 提示: JSON 格式数组，例如...              │
├─────────────────────────────────────────┤
│ Playwright 脚本:                         │
│ [                                 ]      │
│ [   JSON 格式的脚本对象            ]      │
│ [                                 ]      │
│ 提示: JSON 格式对象，包含...              │
├─────────────────────────────────────────┤
│ [重新生成脚本]        [取消] [保存]       │
└─────────────────────────────────────────┘
```

### 字段说明

#### 基本信息字段
- **用例名称**: 文本输入
- **描述**: 多行文本
- **自然语言描述**: 多行文本（用于 LLM 生成）
- **预期结果**: 多行文本

#### 脚本字段（新增）
- **标准化步骤**: JSON 格式文本框（8 行）
- **Playwright 脚本**: JSON 格式文本框（10 行）

#### 操作按钮
- **重新生成脚本**: 黄色警告按钮，使用 LLM 生成
- **取消**: 灰色按钮，关闭对话框
- **保存**: 蓝色主要按钮，保存所有修改

## 工作流程

### 流程 1: 手动编辑

```
打开编辑对话框
  ↓
查看当前的标准化步骤和 Playwright 脚本
  ↓
直接修改 JSON 内容
  ↓
点击"保存"
  ↓
✅ 验证 JSON 格式
  ↓
✅ 保存成功
```

### 流程 2: 使用 LLM 重新生成

```
打开编辑对话框
  ↓
修改自然语言描述
  ↓
点击"重新生成脚本"
  ↓
LLM 生成标准化步骤（显示在表单中）
  ↓
LLM 生成 Playwright 脚本（显示在表单中）
  ↓
检查生成的脚本
  ↓
(可选) 手动微调脚本
  ↓
点击"保存"
  ↓
✅ 保存成功
```

### 流程 3: 混合模式

```
打开编辑对话框
  ↓
点击"重新生成脚本" → LLM 生成脚本
  ↓
检查标准化步骤，手动调整某些步骤
  ↓
检查 Playwright 脚本，手动优化选择器
  ↓
点击"保存"
  ↓
✅ 保存成功
```

## 前端实现

### 文件修改

**文件**: `frontend/src/views/TestCaseDetail.vue`

#### 1. 新增状态变量

```javascript
const regenerating = ref(false)  // 重新生成中
const standardStepsJson = ref('')  // 标准化步骤 JSON
const playwrightScriptJson = ref('')  // Playwright 脚本 JSON
```

#### 2. 编辑对话框

```vue
<el-form-item label="标准化步骤">
  <el-input 
    v-model="standardStepsJson" 
    type="textarea" 
    :rows="8"
    placeholder="JSON 格式的标准化步骤"
  />
  <div style="font-size: 12px; color: #909399; margin-top: 4px;">
    JSON 格式数组，例如: [{"action": "goto", "value": "https://example.com"}]
  </div>
</el-form-item>

<el-form-item label="Playwright 脚本">
  <el-input 
    v-model="playwrightScriptJson" 
    type="textarea" 
    :rows="10"
    placeholder="JSON 格式的 Playwright 脚本"
  />
  <div style="font-size: 12px; color: #909399; margin-top: 4px;">
    JSON 格式对象，包含 browser、viewport、steps 等字段
  </div>
</el-form-item>
```

#### 3. 打开编辑对话框

```javascript
const handleEdit = () => {
  editForm.value = {
    name: testCase.value.name,
    description: testCase.value.description,
    natural_language: testCase.value.natural_language,
    expected_result: testCase.value.expected_result
  }
  
  // 将标准化步骤和 Playwright 脚本转为 JSON 字符串以便编辑
  standardStepsJson.value = JSON.stringify(testCase.value.standard_steps, null, 2)
  playwrightScriptJson.value = JSON.stringify(testCase.value.playwright_script, null, 2)
  
  showEditDialog.value = true
}
```

#### 4. 保存逻辑（手动编辑）

```javascript
const handleSave = async () => {
  saving.value = true
  try {
    // 解析 JSON 字符串
    let standardSteps
    let playwrightScript
    
    try {
      standardSteps = JSON.parse(standardStepsJson.value)
    } catch (e) {
      ElMessage.error('标准化步骤 JSON 格式错误，请检查')
      return
    }
    
    try {
      playwrightScript = JSON.parse(playwrightScriptJson.value)
    } catch (e) {
      ElMessage.error('Playwright 脚本 JSON 格式错误，请检查')
      return
    }
    
    // 保存所有字段
    const updateData = {
      name: editForm.value.name,
      description: editForm.value.description,
      natural_language: editForm.value.natural_language,
      expected_result: editForm.value.expected_result,
      standard_steps: standardSteps,
      playwright_script: playwrightScript
    }
    
    await testCaseAPI.update(caseId, updateData)
    
    ElMessage.success('保存成功')
    showEditDialog.value = false
    await loadTestCase()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}
```

#### 5. 重新生成逻辑

```javascript
const handleRegenerate = async () => {
  regenerating.value = true
  try {
    // 第一步：使用 LLM 从自然语言生成标准化步骤
    ElMessage.info('正在使用 LLM 生成测试步骤...')
    const standardCase = await testCaseAPI.generateFromNL(
      testCase.value.project_id,
      editForm.value.natural_language
    )
    
    // 更新标准化步骤到表单
    standardStepsJson.value = JSON.stringify(standardCase.standard_steps, null, 2)
    
    // 临时保存以便生成脚本（包含标准化步骤）
    await testCaseAPI.update(caseId, {
      standard_steps: standardCase.standard_steps
    })
    
    // 第二步：生成 Playwright 脚本
    ElMessage.info('正在生成 Playwright 脚本...')
    const scriptResult = await testCaseAPI.generateScript(caseId)
    
    // 更新 Playwright 脚本到表单
    playwrightScriptJson.value = JSON.stringify(scriptResult.playwright_script, null, 2)
    
    ElMessage.success('脚本重新生成成功，请检查后保存')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成失败')
  } finally {
    regenerating.value = false
  }
}
```

## JSON 格式示例

### 标准化步骤格式

```json
[
  {
    "action": "goto",
    "value": "https://www.baidu.com",
    "description": "打开百度首页"
  },
  {
    "action": "fill",
    "element": "input#kw",
    "value": "测试",
    "description": "在搜索框输入'测试'"
  },
  {
    "action": "click",
    "element": "input#su",
    "description": "点击搜索按钮"
  },
  {
    "action": "waitForSelector",
    "element": "#content_left",
    "description": "等待搜索结果出现"
  }
]
```

### Playwright 脚本格式

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
      "value": "https://www.baidu.com",
      "description": "打开百度首页",
      "timeout": 30000,
      "screenshot": true
    },
    {
      "index": 2,
      "action": "fill",
      "selector": "input#kw",
      "value": "测试",
      "description": "在搜索框输入'测试'",
      "timeout": 30000,
      "screenshot": true
    },
    {
      "index": 3,
      "action": "click",
      "selector": "input#su",
      "description": "点击搜索按钮",
      "timeout": 30000,
      "screenshot": true
    }
  ]
}
```

## 用户体验

### 提示信息

#### 编辑对话框顶部
```
ℹ️ 可以手动编辑步骤和脚本，或点击'重新生成脚本'按钮使用 LLM 自动生成
```

#### JSON 字段下方提示
- **标准化步骤**: "JSON 格式数组，例如: [{"action": "goto", "value": "https://example.com", "description": "打开页面"}]"
- **Playwright 脚本**: "JSON 格式对象，包含 browser、viewport、steps 等字段"

### 操作提示

#### 重新生成过程
```
点击"重新生成脚本"
  ↓
"正在使用 LLM 生成测试步骤..." [蓝色提示]
  ↓
"正在生成 Playwright 脚本..." [蓝色提示]
  ↓
"脚本重新生成成功，请检查后保存" [绿色提示]
```

#### 保存过程
```
点击"保存"
  ↓
验证 JSON 格式
  ↓
如果格式错误：
  "标准化步骤 JSON 格式错误，请检查" [红色提示]
  或
  "Playwright 脚本 JSON 格式错误，请检查" [红色提示]
  
如果格式正确：
  "保存中..." [按钮文字]
  ↓
  "保存成功" [绿色提示]
```

## 错误处理

### JSON 格式验证

```javascript
// 标准化步骤验证
try {
  standardSteps = JSON.parse(standardStepsJson.value)
} catch (e) {
  ElMessage.error('标准化步骤 JSON 格式错误，请检查')
  return  // 阻止保存
}

// Playwright 脚本验证
try {
  playwrightScript = JSON.parse(playwrightScriptJson.value)
} catch (e) {
  ElMessage.error('Playwright 脚本 JSON 格式错误，请检查')
  return  // 阻止保存
}
```

### 常见错误

#### 1. JSON 格式错误
```
错误输入: {action: "goto"}  // 缺少引号
正确输入: {"action": "goto"}

错误提示: "标准化步骤 JSON 格式错误，请检查"
```

#### 2. 缺少必需字段
```
错误输入: [{"action": "goto"}]  // 缺少 value
正确输入: [{"action": "goto", "value": "https://example.com"}]

后端会返回验证错误
```

#### 3. 类型错误
```
错误输入: {"steps": "invalid"}  // steps 应该是数组
正确输入: {"steps": []}

后端会返回验证错误
```

## 优点

1. **灵活性**: 可以手动编辑或使用 LLM 生成
2. **可控性**: 生成后可以检查和修改，不会立即保存
3. **效率**: 可以快速微调而不需要重新生成
4. **透明性**: 直接看到和编辑 JSON，了解脚本结构
5. **安全性**: JSON 格式验证防止保存无效数据

## 使用场景

### 场景 1: 快速微调
- LLM 生成的脚本基本正确，但选择器需要调整
- 使用"重新生成"获得基础脚本，手动修改选择器

### 场景 2: 复杂测试
- 测试步骤复杂，LLM 可能理解不准确
- 手动编写标准化步骤，然后使用 LLM 生成 Playwright 脚本

### 场景 3: 完全手动
- 对测试脚本有精确要求
- 直接手动编写完整的 JSON 脚本

### 场景 4: 学习和调试
- 查看 LLM 生成的脚本，学习正确格式
- 尝试修改和调试，理解脚本工作原理

## 最佳实践

1. **保持格式**: 使用生成的脚本作为模板，保持相同的 JSON 结构
2. **验证数据**: 修改后使用在线 JSON 验证工具检查格式
3. **小步修改**: 每次只修改一小部分，保存测试
4. **备份重要**: 大改动前复制用例作为备份
5. **测试验证**: 修改后立即执行测试验证脚本正确性

## 注意事项

1. **JSON 格式**: 必须是有效的 JSON 格式
2. **字段完整**: 保留所有必需的字段
3. **数据类型**: 注意字符串、数字、数组、对象的区别
4. **引号使用**: JSON 要求使用双引号，不能用单引号
5. **逗号分隔**: 最后一项后面不要有逗号

## 后续优化建议

1. **JSON 编辑器**: 使用专业的 JSON 编辑器组件，提供语法高亮和自动补全
2. **格式化按钮**: 添加"格式化 JSON"按钮，自动美化格式
3. **模板库**: 提供常用步骤的模板，可以快速插入
4. **语法检查**: 实时显示 JSON 语法错误位置
5. **差异对比**: 显示修改前后的差异

## 修改文件清单

- ✅ `frontend/src/views/TestCaseDetail.vue` - 添加脚本编辑功能

## 测试建议

1. **手动编辑测试**:
   - 打开编辑对话框
   - 修改标准化步骤或 Playwright 脚本
   - 保存并验证修改生效

2. **重新生成测试**:
   - 点击"重新生成脚本"
   - 检查生成的脚本
   - 进行微调后保存

3. **错误处理测试**:
   - 输入无效的 JSON
   - 验证错误提示是否正确

4. **混合编辑测试**:
   - 先生成脚本
   - 然后手动修改
   - 保存并执行测试

## 日期

2025-10-23
