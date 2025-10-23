# 录制脚本目标网址修复

## 问题描述

在点击"录制脚本"时，目标网址的默认值存在问题：
- ❌ 硬编码为 `ai.42lab.cn`
- ❌ 不是用户创建项目时配置的 base_url
- ❌ 用户需要手动修改 URL

## 需求

录制脚本时的目标网址应该：
1. ✅ 优先使用项目的 base_url（创建项目时配置的）
2. ✅ 其次从自然语言描述中提取 URL
3. ✅ 如果都没有，留空由用户输入
4. ✅ 用户始终可以手动修改

## 问题根因

### TestCaseDetail.vue

```javascript
// 原代码 - 硬编码默认值
const showRecordGuide = () => {
  // 尝试从自然语言提取
  if (testCase.value?.natural_language) {
    const urlMatch = testCase.value.natural_language.match(/(https?:\/\/[^\s,、。]+)/)
    if (urlMatch) {
      recordTargetUrl.value = urlMatch[1]
    }
  }
  
  // ❌ 硬编码的默认值
  if (!recordTargetUrl.value) {
    recordTargetUrl.value = 'ai.42lab.cn'
  }
  
  showRecordDialog.value = true
}
```

**问题**：
- 没有从项目信息中读取 base_url
- 硬编码了一个特定的域名
- testCase 对象没有包含项目的 base_url

### TestCaseForm.vue

```javascript
// 原代码 - 没有设置默认 URL
@click="showRecordDialog = true"  // 直接打开对话框，URL 为空
```

**问题**：
- 没有初始化 recordTargetUrl
- 用户需要完全手动输入

## 解决方案

### 1. 加载项目信息

在两个页面中都需要获取项目信息来读取 base_url：

#### TestCaseDetail.vue
```javascript
// 导入 projectAPI
import { testCaseAPI, testRunAPI, projectAPI } from '../api'

// 添加 project 状态
const project = ref(null)

// 在加载测试用例时同时加载项目信息
const loadTestCase = async () => {
  loading.value = true
  try {
    testCase.value = await testCaseAPI.get(caseId)
    // ✅ 加载项目信息（用于获取 base_url）
    if (testCase.value.project_id) {
      project.value = await projectAPI.get(testCase.value.project_id)
    }
  } catch (error) {
    ElMessage.error('加载测试用例失败')
  } finally {
    loading.value = false
  }
}
```

#### TestCaseForm.vue
```javascript
// 导入 projectAPI
import { testCaseAPI, testRunAPI, projectAPI } from '../api'

// 添加 project 状态
const project = ref(null)

// 在组件挂载时加载项目信息
const loadProject = async () => {
  try {
    project.value = await projectAPI.get(projectId)
  } catch (error) {
    console.error('加载项目信息失败:', error)
  }
}

onMounted(() => {
  loadProject()
})
```

### 2. 智能设置默认 URL

#### TestCaseDetail.vue
```javascript
const showRecordGuide = () => {
  // ✅ 优先从项目 base_url 读取
  if (project.value?.base_url) {
    recordTargetUrl.value = project.value.base_url
  }
  // ✅ 其次从自然语言描述中提取
  else if (testCase.value?.natural_language) {
    const urlMatch = testCase.value.natural_language.match(/(https?:\/\/[^\s,、。]+)/)
    if (urlMatch) {
      recordTargetUrl.value = urlMatch[1]
    }
  }
  
  // ✅ 如果都没有，留空由用户输入
  if (!recordTargetUrl.value) {
    recordTargetUrl.value = ''
  }
  
  showRecordDialog.value = true
}
```

#### TestCaseForm.vue
```javascript
// 创建专门的函数来处理显示录制对话框
const handleShowRecordDialog = () => {
  // ✅ 优先从项目 base_url 读取
  if (project.value?.base_url) {
    recordTargetUrl.value = project.value.base_url
  }
  // ✅ 其次从自然语言描述中提取
  else if (form.naturalLanguage) {
    const urlMatch = form.naturalLanguage.match(/(https?:\/\/[^\s,、。]+)/)
    if (urlMatch) {
      recordTargetUrl.value = urlMatch[1]
    }
  }
  
  // ✅ 如果都没有，留空由用户输入
  if (!recordTargetUrl.value) {
    recordTargetUrl.value = ''
  }
  
  showRecordDialog.value = true
}

// 更新模板中的点击事件
// 从: @click="showRecordDialog = true"
// 到: @click="handleShowRecordDialog"
```

## URL 设置优先级

```
1. 项目 base_url (project.base_url)
   ↓
2. 自然语言描述中的 URL
   ↓
3. 留空，由用户输入
```

## 修复效果对比

### 修复前

**场景1：项目 base_url 是 https://example.com**
- 录制对话框显示：`https://ai.42lab.cn` ❌
- 用户需要手动改为：`https://example.com`

**场景2：自然语言包含 URL**
- 自然语言："访问 https://test.com 并登录"
- 录制对话框显示：`https://test.com` ✅
- 但如果没有 URL，显示：`https://ai.42lab.cn` ❌

### 修复后

**场景1：项目 base_url 是 https://example.com**
- 录制对话框显示：`https://example.com` ✅
- 用户可以直接开始录制或修改

**场景2：自然语言包含 URL**
- 自然语言："访问 https://test.com 并登录"
- 但项目 base_url 是 https://example.com
- 录制对话框显示：`https://example.com` ✅（优先级更高）

**场景3：都没有配置**
- 项目没有 base_url
- 自然语言没有 URL
- 录制对话框显示：空 ✅
- 用户手动输入

## 技术要点

### 1. API 调用优化

```javascript
// 只在需要时加载项目信息
const loadTestCase = async () => {
  testCase.value = await testCaseAPI.get(caseId)
  if (testCase.value.project_id) {
    project.value = await projectAPI.get(testCase.value.project_id)
  }
}
```

### 2. 正则表达式提取 URL

```javascript
// 匹配 http:// 或 https:// 开头的 URL
const urlMatch = text.match(/(https?:\/\/[^\s,、。]+)/)
```

### 3. 条件渲染逻辑

```javascript
// 使用 if-else 链实现优先级
if (condition1) {
  // 优先
} else if (condition2) {
  // 次优
} else {
  // 默认
}
```

### 4. 用户可编辑

```html
<!-- 用户始终可以修改 -->
<el-input
  v-model="recordTargetUrl"
  placeholder="请输入要测试的网站地址"
  clearable
>
  <template #prepend>https://</template>
</el-input>
```

## 相关文件

- **TestCaseDetail.vue**
  - 导入 `projectAPI`
  - 添加 `project` 状态
  - 修改 `loadTestCase()` 加载项目信息
  - 修改 `showRecordGuide()` 智能设置 URL

- **TestCaseForm.vue**
  - 导入 `projectAPI`
  - 添加 `project` 状态
  - 添加 `loadProject()` 函数
  - 添加 `handleShowRecordDialog()` 函数
  - 修改模板点击事件

## 测试验证

### 测试用例1：使用项目 base_url
1. 创建项目，设置 base_url 为 `https://example.com`
2. 创建测试用例
3. 点击"录制脚本"
4. **验证**：对话框中显示 `https://example.com` ✅

### 测试用例2：自然语言包含 URL
1. 创建项目，不设置 base_url 或设置为其他值
2. 创建测试用例，自然语言为"访问 https://test.com"
3. 点击"录制脚本"
4. **验证**：对话框中显示项目 base_url（如果有），否则显示 `https://test.com` ✅

### 测试用例3：都没有配置
1. 创建项目，不设置 base_url
2. 创建测试用例，自然语言中不包含 URL
3. 点击"录制脚本"
4. **验证**：对话框中输入框为空，等待用户输入 ✅

### 测试用例4：用户可以修改
1. 打开录制对话框（不管默认值是什么）
2. 手动修改 URL
3. **验证**：可以正常修改并使用新 URL 录制 ✅

## 最佳实践

### 1. 配置项目 base_url
创建项目时应该正确配置 base_url：
```
项目名称: 电商测试
Base URL: https://shop.example.com
```

### 2. 自然语言描述包含 URL
如果测试不同的环境，可以在描述中指定：
```
访问 https://dev.shop.example.com 并测试登录功能
```

### 3. 运行时修改
录制时可以临时修改 URL 而不影响项目配置：
```
默认: https://example.com
修改为: https://example.com/admin
```

## 用户体验改进

1. **智能默认值**：自动填充最可能正确的 URL
2. **灵活性**：用户始终可以修改
3. **清晰性**：空值比错误值更好
4. **一致性**：两个页面使用相同的逻辑

## 总结

通过这次修复：
- ✅ 录制脚本时自动使用项目配置的 base_url
- ✅ 减少用户手动输入的工作量
- ✅ 提高录制功能的易用性
- ✅ 保持灵活性，用户可随时修改
- ✅ 两个页面（详情页和创建流程）行为一致

现在录制功能更加智能和用户友好了！🎉
