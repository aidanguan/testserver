# 项目编辑、测试用例编辑和历史记录功能

## 功能概述

本次更新添加了以下三个核心功能：
1. **项目编辑** - 允许管理员编辑已创建的项目信息
2. **测试用例编辑** - 允许用户编辑测试用例的基本信息
3. **测试执行历史** - 查看测试用例的所有历史执行记录

## 1. 项目编辑功能

### 前端修改

**文件**: `frontend/src/views/ProjectList.vue`

#### 新增功能：
- ✅ 在项目列表中添加"编辑"按钮（仅管理员可见）
- ✅ 点击"编辑"按钮打开编辑对话框，预填充现有数据
- ✅ 支持编辑所有项目字段（名称、描述、URL、LLM配置等）
- ✅ API密钥字段：编辑时留空表示不修改，填写则更新

#### 关键实现：
```javascript
// 编辑状态管理
const editingProject = ref(null)

// 点击编辑按钮
const handleEdit = (row) => {
  editingProject.value = row
  Object.assign(projectForm, {
    name: row.name,
    description: row.description,
    base_url: row.base_url,
    llm_provider: row.llm_provider,
    llm_model: row.llm_model,
    llm_api_key: '',  // 不显示原密钥
    llm_base_url: row.llm_base_url || ''
  })
  showCreateDialog.value = true
}

// 保存更新
const handleUpdate = async () => {
  const updateData = { ...projectForm }
  // 如果密钥为空，不传递密钥字段
  if (!updateData.llm_api_key) {
    delete updateData.llm_api_key
  }
  await projectStore.updateProject(editingProject.value.id, updateData)
}
```

### 后端修改

**文件**: `backend/app/api/endpoints/projects.py`

#### 更新内容：
- ✅ 添加对 `llm_base_url` 字段的更新支持
- ✅ 已有完整的项目更新接口 `PUT /api/projects/{project_id}`

```python
# 更新项目时支持 llm_base_url
if project_data.llm_base_url is not None:
    project.llm_base_url = project_data.llm_base_url
```

## 2. 测试用例详情与编辑功能

### 完善测试用例详情页

**文件**: `frontend/src/views/TestCaseDetail.vue`

#### 新增功能：
- ✅ 显示完整的测试用例信息（名称、描述、自然语言、步骤、预期结果、脚本）
- ✅ "编辑"按钮 - 打开编辑对话框
- ✅ "执行测试"按钮 - 立即执行测试
- ✅ "查看历史"按钮 - 跳转到历史记录页面

#### 界面展示：
```vue
<el-descriptions :column="1" border>
  <el-descriptions-item label="用例名称">{{ testCase?.name }}</el-descriptions-item>
  <el-descriptions-item label="描述">{{ testCase?.description }}</el-descriptions-item>
  <el-descriptions-item label="自然语言描述">
    <pre>{{ testCase?.natural_language }}</pre>
  </el-descriptions-item>
  <el-descriptions-item label="标准化步骤">
    <!-- 格式化显示每个步骤 -->
  </el-descriptions-item>
  <el-descriptions-item label="预期结果">
    <pre>{{ testCase?.expected_result }}</pre>
  </el-descriptions-item>
</el-descriptions>
```

#### 编辑功能：
- 支持编辑：用例名称、描述、自然语言描述、预期结果
- 使用对话框形式进行编辑
- 保存后自动刷新显示

### 后端接口

**文件**: `backend/app/api/endpoints/test_cases.py`

已有完整的更新接口：
- ✅ `PUT /api/cases/{case_id}` - 更新测试用例
- ✅ 支持更新所有可编辑字段

## 3. 测试执行历史功能

### 新增历史记录页面

**文件**: `frontend/src/views/TestCaseHistory.vue` (新建)

#### 功能特性：
- ✅ 显示指定测试用例的所有执行记录
- ✅ 表格展示：运行ID、状态、LLM判定、触发人、时间、耗时
- ✅ 状态标签：运行中/成功/失败/错误（带颜色区分）
- ✅ LLM判定标签：通过/失败/未知
- ✅ "查看详情"按钮 - 跳转到具体执行详情页
- ✅ "执行新测试"按钮 - 快速启动新的测试执行

#### 界面展示：
```vue
<el-table :data="runs">
  <el-table-column prop="id" label="运行ID" />
  <el-table-column label="状态">
    <el-tag :type="getStatusType(scope.row.status)">
      {{ getStatusText(scope.row.status) }}
    </el-tag>
  </el-table-column>
  <el-table-column label="LLM判定">
    <el-tag :type="getVerdictType(scope.row.llm_verdict)">
      {{ getVerdictText(scope.row.llm_verdict) }}
    </el-tag>
  </el-table-column>
  <el-table-column label="开始时间" />
  <el-table-column label="结束时间" />
  <el-table-column label="耗时" />
  <el-table-column label="操作">
    <el-button @click="handleView(row)">查看详情</el-button>
  </el-table-column>
</el-table>
```

### 路由配置

**文件**: `frontend/src/router/index.js`

新增路由：
```javascript
{
  path: 'cases/:id/history',
  name: 'TestCaseHistory',
  component: () => import('../views/TestCaseHistory.vue')
}
```

### 后端接口

**文件**: `backend/app/api/endpoints/test_runs.py`

已有接口：
- ✅ `GET /api/runs?case_id={case_id}` - 获取指定用例的执行记录列表

## 4. 项目详情页增强

**文件**: `frontend/src/views/ProjectDetail.vue`

#### 新增功能：
- ✅ 页面标题处添加"编辑项目"按钮（仅管理员可见）
- ✅ 测试用例列表添加"历史"按钮
- ✅ 点击"历史"按钮跳转到对应用例的历史记录页面

## 使用流程

### 编辑项目
1. 进入"项目管理"页面
2. 找到要编辑的项目，点击"编辑"按钮
3. 在弹出的对话框中修改项目信息
4. 点击"保存"完成更新

**注意**：API密钥字段留空表示不修改，填写则更新为新密钥

### 编辑测试用例
1. 进入测试用例详情页
2. 点击右上角"编辑"按钮
3. 在弹出的对话框中修改用例信息
4. 点击"保存"完成更新

### 查看执行历史
1. **方式一**：在项目详情页 → 测试用例列表 → 点击"历史"按钮
2. **方式二**：在测试用例详情页 → 点击"查看历史"按钮
3. 在历史记录页面查看所有执行记录
4. 点击"查看详情"可以查看具体执行的步骤和截图

## API 接口汇总

### 项目管理
- `GET /api/projects` - 获取项目列表
- `GET /api/projects/{id}` - 获取项目详情
- `POST /api/projects` - 创建项目
- `PUT /api/projects/{id}` - 更新项目 ✨ (支持 llm_base_url)
- `DELETE /api/projects/{id}` - 删除项目

### 测试用例管理
- `GET /api/projects/{project_id}/cases` - 获取项目的测试用例列表
- `GET /api/cases/{id}` - 获取用例详情
- `POST /api/projects/{project_id}/cases` - 创建用例
- `PUT /api/cases/{id}` - 更新用例 ✨
- `DELETE /api/cases/{id}` - 删除用例

### 测试执行
- `POST /api/cases/{case_id}/execute` - 执行测试
- `GET /api/runs/{run_id}` - 获取运行详情
- `GET /api/runs?case_id={case_id}` - 获取用例的执行历史 ✨
- `GET /api/runs/{run_id}/steps` - 获取步骤执行记录

## 权限说明

| 功能 | Admin | Member |
|-----|-------|--------|
| 查看项目 | ✅ | ✅ |
| 编辑项目 | ✅ | ❌ |
| 删除项目 | ✅ | ❌ |
| 查看测试用例 | ✅ | ✅ |
| 编辑测试用例 | ✅ | ✅ (自己创建的) |
| 删除测试用例 | ✅ | ✅ (自己创建的) |
| 执行测试 | ✅ | ✅ |
| 查看历史 | ✅ | ✅ |

## 文件清单

### 新建文件
- ✅ `frontend/src/views/TestCaseHistory.vue` - 测试执行历史页面

### 修改文件
- ✅ `frontend/src/views/ProjectList.vue` - 添加项目编辑功能
- ✅ `frontend/src/views/ProjectDetail.vue` - 添加编辑按钮和历史按钮
- ✅ `frontend/src/views/TestCaseDetail.vue` - 完善详情页和编辑功能
- ✅ `frontend/src/router/index.js` - 添加历史记录路由
- ✅ `backend/app/api/endpoints/projects.py` - 支持 llm_base_url 更新

### 已有接口（无需修改）
- ✅ `backend/app/api/endpoints/test_cases.py` - 已有完整的更新接口
- ✅ `backend/app/api/endpoints/test_runs.py` - 已有历史记录查询接口
- ✅ `frontend/src/stores/project.js` - 已有 updateProject 方法
- ✅ `frontend/src/api/index.js` - 已有所有必需的 API 方法

## 测试建议

1. **测试项目编辑**：
   - 编辑项目名称、描述
   - 修改 LLM 配置（提供商、模型、Base URL）
   - 测试密钥更新（填写新密钥）和保持不变（留空）

2. **测试用例编辑**：
   - 修改用例名称和描述
   - 更新自然语言描述和预期结果
   - 验证保存后页面自动刷新

3. **测试历史记录**：
   - 执行多次测试，验证历史记录累积
   - 查看不同状态的执行记录（成功、失败、错误）
   - 从历史记录跳转到详情页

## 日期

2025-10-23
