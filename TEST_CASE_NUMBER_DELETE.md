# 测试用例编号与删除功能

## 功能概述

本次更新为测试用例添加了以下功能：
1. **显示用例编号** - 在所有相关页面显示测试用例ID作为编号
2. **删除测试用例** - 允许用户删除测试用例（带确认提示）

## 1. 测试用例编号显示

### 显示位置

测试用例编号（即数据库中的 `id` 字段）现在会显示在以下位置：

#### 1.1 项目详情页 - 测试用例列表

**文件**: `frontend/src/views/ProjectDetail.vue`

新增"编号"列，显示在表格最左侧：

```vue
<el-table :data="testCases">
  <el-table-column prop="id" label="编号" width="80" />
  <el-table-column prop="name" label="用例名称" />
  <el-table-column prop="description" label="描述" />
  <!-- ... -->
</el-table>
```

#### 1.2 测试用例详情页

**文件**: `frontend/src/views/TestCaseDetail.vue`

在用例信息描述列表顶部显示：

```vue
<el-descriptions :column="1" border>
  <el-descriptions-item label="用例编号">{{ testCase?.id }}</el-descriptions-item>
  <el-descriptions-item label="用例名称">{{ testCase?.name }}</el-descriptions-item>
  <!-- ... -->
</el-descriptions>
```

#### 1.3 测试历史页面

**文件**: `frontend/src/views/TestCaseHistory.vue`

在页面标题中显示：

```vue
<template #header>
  <div class="card-header">
    <div>
      <span>编号: {{ testCase?.id }} | {{ testCase?.name }} - 历史记录</span>
    </div>
    <el-button type="primary" @click="handleExecute">执行新测试</el-button>
  </div>
</template>
```

### 编号说明

- **编号来源**: 数据库自增ID
- **唯一性**: 每个测试用例的编号在整个系统中唯一
- **不可修改**: 编号由系统自动分配，不可手动修改
- **用途**: 
  - 快速识别和引用测试用例
  - 在日志和报告中追踪测试用例
  - 便于沟通和讨论时引用具体用例

## 2. 删除测试用例功能

### 删除入口

#### 2.1 项目详情页 - 测试用例列表

**文件**: `frontend/src/views/ProjectDetail.vue`

在操作列添加"删除"按钮：

```vue
<el-table-column label="操作" width="350">
  <template #default="scope">
    <el-button size="small" @click="handleViewCase(scope.row)">查看</el-button>
    <el-button size="small" type="primary" @click="handleExecute(scope.row)">执行</el-button>
    <el-button size="small" @click="handleViewHistory(scope.row)">历史</el-button>
    <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
  </template>
</el-table-column>
```

#### 2.2 测试用例详情页

**文件**: `frontend/src/views/TestCaseDetail.vue`

在页面头部操作按钮组添加"删除"按钮：

```vue
<div>
  <el-button type="primary" @click="handleEdit">编辑</el-button>
  <el-button type="success" @click="handleExecute">执行测试</el-button>
  <el-button @click="handleViewHistory">查看历史</el-button>
  <el-button type="danger" @click="handleDelete">删除</el-button>
</div>
```

### 删除逻辑

#### 2.3 确认对话框

删除操作需要用户确认，防止误删除：

```javascript
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试用例"${row.name}"吗？删除后将无法恢复！`,
      '警告',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消'
      }
    )
    
    await testCaseAPI.delete(row.id)
    ElMessage.success('删除成功')
    await loadTestCases()  // 刷新列表
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}
```

#### 2.4 权限控制

**后端**: `backend/app/api/endpoints/test_cases.py`

删除权限规则（已有实现）：
- ✅ **Admin用户**: 可以删除任何测试用例
- ✅ **普通用户**: 只能删除自己创建的测试用例

```python
@router.delete("/cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除测试用例"""
    test_case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测试用例不存在"
        )
    
    # 检查权限：Admin或创建者可以删除
    from app.models.user import UserRole
    if current_user.role != UserRole.ADMIN and test_case.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能删除自己创建的测试用例"
        )
    
    db.delete(test_case)
    db.commit()
    
    return None
```

#### 2.5 级联删除

**数据库模型**: `backend/app/models/test_case.py`

删除测试用例时，自动删除关联的测试运行记录：

```python
class TestCase(Base):
    # 关系定义，支持级联删除
    test_runs = relationship("TestRun", back_populates="test_case", cascade="all, delete-orphan")
```

这意味着删除测试用例时：
- ✅ 所有相关的测试运行记录（TestRun）会被自动删除
- ✅ 所有运行记录的步骤执行记录（StepExecution）会被自动删除
- ✅ 工件文件（截图、日志等）仍保留在文件系统中

### 删除后行为

#### 从项目详情页删除
- 删除成功后自动刷新测试用例列表
- 保持在当前页面

#### 从测试用例详情页删除
- 删除成功后自动跳转回项目详情页
- 显示删除成功提示

```javascript
// 测试用例详情页的删除逻辑
const handleDelete = async () => {
  // ... 确认对话框 ...
  
  await testCaseAPI.delete(caseId)
  ElMessage.success('删除成功')
  // 跳转回项目详情页
  router.push(`/projects/${testCase.value.project_id}`)
}
```

## 3. UI 变化总结

### 项目详情页

**修改前**:
```
编号 | 用例名称 | 描述 | 操作（查看、执行、历史）
```

**修改后**:
```
编号 | 用例名称 | 描述 | 操作（查看、执行、历史、删除）
      ↑                               ↑
    新增列                          新增删除按钮
```

### 测试用例详情页

**修改前**:
```
用例信息
- 用例名称: xxx
- 描述: xxx
...
操作按钮: [编辑] [执行测试] [查看历史]
```

**修改后**:
```
用例信息
- 用例编号: 1        ← 新增
- 用例名称: xxx
- 描述: xxx
...
操作按钮: [编辑] [执行测试] [查看历史] [删除]  ← 新增删除按钮
```

### 测试历史页面

**修改前**:
```
标题: 测试用例名称 - 历史记录
```

**修改后**:
```
标题: 编号: 1 | 测试用例名称 - 历史记录
        ↑
      新增编号显示
```

## 4. 安全性考虑

### 删除确认
- ✅ 双重确认机制（弹窗确认）
- ✅ 警告类型对话框，红色按钮强调危险性
- ✅ 提示"删除后将无法恢复"

### 权限检查
- ✅ 后端接口进行权限验证
- ✅ 普通用户只能删除自己创建的用例
- ✅ Admin可以删除所有用例

### 数据完整性
- ✅ 级联删除相关测试运行记录
- ✅ 数据库外键约束确保一致性
- ✅ 事务处理保证原子性

## 5. API 接口

### 删除测试用例

**接口**: `DELETE /api/cases/{case_id}`

**权限**: 需要登录，Admin或用例创建者

**响应**:
- 成功: `204 No Content`
- 未找到: `404 Not Found`
- 无权限: `403 Forbidden`

**示例**:
```bash
DELETE http://localhost:8000/api/cases/1
Authorization: Bearer {token}
```

## 6. 修改文件清单

### 前端文件
- ✅ `frontend/src/views/ProjectDetail.vue`
  - 添加编号列
  - 添加删除按钮和删除逻辑
  
- ✅ `frontend/src/views/TestCaseDetail.vue`
  - 显示用例编号
  - 添加删除按钮和删除逻辑
  
- ✅ `frontend/src/views/TestCaseHistory.vue`
  - 在标题中显示用例编号

### 后端文件
- ✅ `backend/app/api/endpoints/test_cases.py`
  - 已有完整的删除接口和权限控制
  
- ✅ `backend/app/models/test_case.py`
  - 已有级联删除配置

## 7. 使用流程

### 查看测试用例编号
1. 进入项目详情页，在测试用例列表最左侧查看编号
2. 进入测试用例详情页，在用例信息顶部查看编号
3. 进入测试历史页面，在页面标题查看编号

### 删除测试用例

**方式一：从项目详情页删除**
1. 进入项目详情页
2. 找到要删除的测试用例
3. 点击"删除"按钮
4. 在确认对话框中点击"确定删除"
5. 列表自动刷新，用例已被删除

**方式二：从测试用例详情页删除**
1. 进入测试用例详情页
2. 点击右上角"删除"按钮
3. 在确认对话框中点击"确定删除"
4. 自动返回项目详情页

## 8. 注意事项

⚠️ **重要提醒**：
1. 删除操作不可逆，请谨慎操作
2. 删除测试用例会同时删除其所有执行历史记录
3. 工件文件（截图、日志）不会被自动删除，需手动清理
4. 普通用户只能删除自己创建的测试用例
5. 测试用例编号是数据库ID，删除后该编号不会被重新使用

## 9. 后续优化建议

1. **软删除**: 考虑实现软删除机制，保留删除记录
2. **工件清理**: 删除用例时可选是否同时删除工件文件
3. **批量删除**: 支持批量选择和删除测试用例
4. **删除审计**: 记录删除操作到审计日志
5. **回收站**: 实现回收站功能，允许恢复误删除的用例

## 日期

2025-10-23
