# 测试用例编辑自动生成脚本功能

## 功能概述

编辑测试用例时，系统会自动使用 LLM 重新生成标准化测试步骤和 Playwright 脚本，确保脚本与最新的测试描述保持同步。

## 工作流程

### 编辑保存流程

```
用户编辑测试用例
  ↓
点击"保存"按钮
  ↓
第一步: 使用 LLM 从自然语言生成标准化步骤
  ↓
第二步: 更新测试用例的基本信息和标准化步骤
  ↓
第三步: 使用 LLM 从标准化步骤生成 Playwright 脚本
  ↓
第四步: 更新 Playwright 脚本到测试用例
  ↓
✅ 保存完成，刷新页面显示新数据
```

### 详细步骤说明

#### 步骤 1: 生成标准化步骤
```javascript
// 调用 API: POST /api/cases/generate-from-nl
const standardCase = await testCaseAPI.generateFromNL(
  testCase.value.project_id,
  editForm.value.natural_language
)
```

**输入**: 自然语言描述
**输出**: 标准化测试步骤（JSON格式）

#### 步骤 2: 更新基本信息
```javascript
// 调用 API: PUT /api/cases/{case_id}
await testCaseAPI.update(caseId, {
  name: editForm.value.name,
  description: editForm.value.description,
  natural_language: editForm.value.natural_language,
  expected_result: editForm.value.expected_result,
  standard_steps: standardCase.standard_steps
})
```

**更新字段**:
- 用例名称
- 描述
- 自然语言描述
- 预期结果
- 标准化步骤（LLM 生成）

#### 步骤 3: 生成 Playwright 脚本
```javascript
// 调用 API: POST /api/cases/generate-script
const scriptResult = await testCaseAPI.generateScript(caseId)
```

**输入**: 测试用例ID（包含标准化步骤）
**输出**: Playwright 脚本（JSON格式）

#### 步骤 4: 更新 Playwright 脚本
```javascript
// 调用 API: PUT /api/cases/{case_id}
await testCaseAPI.update(caseId, {
  playwright_script: scriptResult.playwright_script
})
```

## 前端实现

### 文件修改

**文件**: `frontend/src/views/TestCaseDetail.vue`

#### 1. 添加用户提示

在编辑对话框顶部添加提示信息：

```vue
<el-alert
  title="修改后将使用 LLM 重新生成测试步骤和 Playwright 脚本"
  type="info"
  :closable="false"
  style="margin-bottom: 20px;"
/>
```

#### 2. 修改保存按钮文字

显示加载状态时的提示：

```vue
<el-button type="primary" @click="handleSave" :loading="saving">
  {{ saving ? '生成脚本并保存...' : '保存' }}
</el-button>
```

#### 3. 实现完整的保存逻辑

```javascript
const handleSave = async () => {
  saving.value = true
  try {
    // 第一步：使用 LLM 从自然语言生成标准化步骤
    ElMessage.info('正在使用 LLM 生成测试步骤...')
    const standardCase = await testCaseAPI.generateFromNL(
      testCase.value.project_id,
      editForm.value.natural_language
    )
    
    // 第二步：更新测试用例基本信息和标准化步骤
    const updateData = {
      name: editForm.value.name,
      description: editForm.value.description,
      natural_language: editForm.value.natural_language,
      expected_result: editForm.value.expected_result,
      standard_steps: standardCase.standard_steps
    }
    await testCaseAPI.update(caseId, updateData)
    
    // 第三步：生成 Playwright 脚本
    ElMessage.info('正在生成 Playwright 脚本...')
    const scriptResult = await testCaseAPI.generateScript(caseId)
    
    // 第四步：更新 Playwright 脚本
    await testCaseAPI.update(caseId, {
      playwright_script: scriptResult.playwright_script
    })
    
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

## 后端接口

### 1. 生成标准化步骤

**接口**: `POST /api/cases/generate-from-nl`

**请求体**:
```json
{
  "project_id": 1,
  "natural_language": "打开百度首页，搜索'测试'，点击第一个搜索结果"
}
```

**响应**:
```json
{
  "standard_steps": [
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
    }
  ]
}
```

### 2. 生成 Playwright 脚本

**接口**: `POST /api/cases/generate-script`

**请求体**:
```json
{
  "test_case_id": 1
}
```

**响应**:
```json
{
  "playwright_script": {
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
      }
    ]
  }
}
```

### 3. 更新测试用例

**接口**: `PUT /api/cases/{case_id}`

**请求体**:
```json
{
  "name": "百度搜索测试",
  "description": "测试百度搜索功能",
  "natural_language": "打开百度首页，搜索'测试'",
  "expected_result": "能够成功搜索并显示结果",
  "standard_steps": [...],
  "playwright_script": {...}
}
```

## 用户体验

### 编辑流程

1. **打开编辑对话框**
   - 进入测试用例详情页
   - 点击"编辑"按钮
   - 看到提示信息："修改后将使用 LLM 重新生成测试步骤和 Playwright 脚本"

2. **修改测试用例**
   - 修改用例名称、描述
   - 修改自然语言描述（最重要）
   - 修改预期结果

3. **保存并生成**
   - 点击"保存"按钮
   - 按钮显示"生成脚本并保存..."
   - 看到进度提示：
     - "正在使用 LLM 生成测试步骤..."
     - "正在生成 Playwright 脚本..."
   - 显示"保存成功"

4. **查看结果**
   - 对话框关闭
   - 页面自动刷新
   - 查看更新后的标准化步骤和脚本

### 加载状态提示

```
点击保存
  ↓
正在使用 LLM 生成测试步骤...  [蓝色提示框]
  ↓
正在生成 Playwright 脚本...   [蓝色提示框]
  ↓
保存成功                      [绿色提示框]
```

## 错误处理

### 常见错误场景

#### 1. LLM API 错误
```
错误: LLM API 调用失败
提示: "保存失败: 生成测试用例失败: API rate limit exceeded"
处理: 保存操作中止，用例不会被修改
```

#### 2. 自然语言描述不清晰
```
错误: LLM 无法理解测试描述
提示: "保存失败: 无法从自然语言生成测试步骤"
处理: 提示用户修改自然语言描述，使其更清晰
```

#### 3. 网络错误
```
错误: 网络请求超时
提示: "保存失败: 网络请求超时"
处理: 可以重试保存操作
```

### 错误处理代码

```javascript
try {
  // ... 保存逻辑 ...
} catch (error) {
  ElMessage.error(error.response?.data?.detail || '保存失败')
} finally {
  saving.value = false
}
```

## 优点

1. **自动同步**: 编辑后自动生成最新的测试脚本
2. **一致性**: 确保脚本与自然语言描述保持一致
3. **用户友好**: 明确的进度提示，用户知道系统在做什么
4. **智能化**: 利用 LLM 自动生成，减少手动编写脚本的工作量
5. **可靠性**: 分步骤保存，出错时有明确提示

## 注意事项

1. **编辑时间**: 由于需要调用 LLM，保存过程可能需要几秒到几十秒
2. **自然语言质量**: 描述越清晰，生成的脚本质量越高
3. **网络要求**: 需要稳定的网络连接到 LLM API
4. **API 配额**: 每次编辑都会调用 LLM API，注意配额限制
5. **成本考虑**: LLM API 调用可能产生费用

## 最佳实践

1. **清晰描述**: 用自然语言清晰描述测试步骤
2. **完整信息**: 包含所有必要的操作和验证点
3. **合理分段**: 将复杂测试分解为多个小测试用例
4. **验证结果**: 保存后查看生成的脚本是否符合预期
5. **测试执行**: 生成后立即执行测试，验证脚本正确性

## 后续优化建议

1. **预览功能**: 保存前预览生成的脚本
2. **手动编辑**: 允许在自动生成后手动微调脚本
3. **版本对比**: 显示修改前后的脚本差异
4. **批量更新**: 支持批量重新生成多个测试用例的脚本
5. **缓存机制**: 相同的自然语言描述可以复用生成结果

## 修改文件清单

- ✅ `frontend/src/views/TestCaseDetail.vue` - 修改编辑保存逻辑
- ✅ `backend/app/api/endpoints/test_cases.py` - 已有所需的 API 接口

## 测试建议

1. **正常流程测试**:
   - 编辑测试用例的自然语言描述
   - 保存并观察进度提示
   - 验证生成的脚本是否正确

2. **错误处理测试**:
   - 测试 LLM API 不可用时的错误提示
   - 测试网络中断时的行为
   - 测试无效的自然语言描述

3. **性能测试**:
   - 测试复杂测试用例的生成时间
   - 测试并发编辑多个用例的情况

## 日期

2025-10-23
