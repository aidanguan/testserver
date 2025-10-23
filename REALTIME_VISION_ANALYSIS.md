# 实时视觉分析功能 - 每步执行后立即分析

## 功能概述

**改进前**：所有测试步骤执行完毕后，才批量分析所有截图  
**改进后**：每执行一个步骤后，立即使用视觉大模型分析该步骤的截图

## 核心改进

### 1. **实时分析** ⚡
- ✅ 执行步骤 → 生成截图 → 立即视觉分析 → 保存观察结果 → 执行下一步
- ✅ 每个步骤的视觉观察结果独立保存到数据库
- ✅ 前端实时显示每步的视觉分析结果

### 2. **更好的用户体验** 🎯
- ✅ 无需等待全部测试完成即可看到部分结果
- ✅ 每个步骤下方直接显示该步的视觉观察
- ✅ 清晰标识哪些步骤符合预期，哪些不符合

### 3. **数据完整性** 📊
- ✅ 步骤级别的观察记录永久保存
- ✅ 支持审计和追溯
- ✅ 便于调试和优化测试用例

## 实现细节

### 数据库改动

**文件**: `backend/app/models/step_execution.py`

添加了 `vision_observation` 字段：

```python
class StepExecution(Base):
    """步骤执行记录表模型"""
    __tablename__ = "step_execution"
    
    # ... 其他字段 ...
    vision_observation = Column(Text)  # 视觉观察结果(JSON格式)
```

**迁移脚本**: `backend/add_vision_observation_column.py`

```bash
cd backend
python add_vision_observation_column.py
```

### 后端改动

#### 1. 修改 PlaywrightExecutor

**文件**: `backend/app/services/playwright_executor.py`

**构造函数改动**：
```python
def __init__(self, artifacts_base_path: str, llm_service=None, expected_result: str = None):
    """
    初始化执行器
    
    Args:
        artifacts_base_path: 工件存储基础路径
        llm_service: LLM服务实例（用于视觉分析）
        expected_result: 预期结果描述
    """
    self.llm_service = llm_service
    self.expected_result = expected_result
    # ...
```

**步骤执行改动**：
```python
def _execute_step(self, step: Dict[str, Any], screenshots_path: str) -> Dict[str, Any]:
    step_result = {
        "index": step.get("index", 0),
        "description": step.get("description", ""),
        "status": "success",
        "screenshot_path": None,
        "vision_observation": None,  # 新增字段
        # ...
    }
    
    # 执行操作...
    # 截图...
    
    # 如果有截图且配置了LLM服务，立即进行视觉分析
    if step_result["screenshot_path"] and self.llm_service and self.expected_result:
        try:
            print(f"\n✨ 步骤 {step['index']} 执行完毕，立即开始视觉分析...")
            vision_result = self.llm_service._analyze_screenshot_with_vision(
                screenshot_path=step_result["screenshot_path"],
                expected_result=self.expected_result,
                step_status=step_result
            )
            # 将视觉分析结果序列化
            import json
            step_result["vision_observation"] = json.dumps(vision_result, ensure_ascii=False)
            print(f"✅ 步骤 {step['index']} 视觉分析完成: {vision_result.get('matches_expectation')}")
        except Exception as e:
            print(f"⚠️ 步骤 {step['index']} 视觉分析失败: {str(e)}")
            step_result["vision_observation"] = json.dumps({"error": str(e)}, ensure_ascii=False)
    
    return step_result
```

#### 2. 修改后台任务

**文件**: `backend/app/api/endpoints/test_runs.py`

**初始化LLM服务**：
```python
def execute_test_background(test_run_id: int, test_case_id: int, db_url: str):
    # ...
    
    # 初始化LLM服务用于实时视觉分析
    llm_service = None
    try:
        api_key = decrypt_api_key(project.llm_api_key)
        llm_service = LLMService(
            provider=project.llm_provider,
            model=project.llm_model,
            api_key=api_key,
            base_url=project.llm_base_url,
            config=project.llm_config
        )
        print(f"🤖 LLM服务初始化成功，将进行实时视觉分析")
    except Exception as e:
        print(f"⚠️ LLM服务初始化失败: {e}，将跳过视觉分析")
    
    # 传递LLM服务给执行器
    executor = PlaywrightExecutor(
        artifacts_base_path=settings.ARTIFACTS_PATH,
        llm_service=llm_service,
        expected_result=test_case.expected_result
    )
    # ...
```

**保存视觉观察结果**：
```python
# 保存步骤执行记录
for step_data in exec_result.get("steps", []):
    step = StepExecution(
        # ...
        vision_observation=step_data.get("vision_observation"),  # 保存视觉观察结果
        # ...
    )
    db.add(step)
```

#### 3. 更新Schema

**文件**: `backend/app/schemas/test_run.py`

```python
class StepExecutionResponse(BaseModel):
    """步骤执行响应Schema"""
    # ... 其他字段 ...
    vision_observation: Optional[str] = None  # 视觉观察结果（JSON字符串）
```

### 前端改动

**文件**: `frontend/src/views/TestRunDetail.vue`

#### 1. 模板改动 - 显示视觉观察

```vue
<!-- 视觉观察结果 -->
<div v-if="step.vision_observation" class="vision-observation">
  <el-alert
    :title="getVisionTitle(step)"
    :type="getVisionAlertType(step)"
    :closable="false"
    style="margin-top: 15px"
  >
    <template #default>
      <div class="vision-content">
        <div class="vision-observation-text">
          {{ getVisionObservation(step) }}
        </div>
        <div v-if="getVisionIssues(step).length > 0" class="vision-issues">
          <p style="font-weight: bold; margin-top: 10px; margin-bottom: 5px;">🚨 发现的问题：</p>
          <ul style="margin: 0; padding-left: 20px;">
            <li v-for="(issue, idx) in getVisionIssues(step)" :key="idx">{{ issue }}</li>
          </ul>
        </div>
      </div>
    </template>
  </el-alert>
</div>
```

#### 2. 脚本改动 - 解析视觉观察

```javascript
// 解析视觉观察结果
const parseVisionObservation = (visionJson) => {
  if (!visionJson) return null
  try {
    return JSON.parse(visionJson)
  } catch (e) {
    return null
  }
}

// 获取视觉观察标题
const getVisionTitle = (step) => {
  const vision = parseVisionObservation(step.vision_observation)
  if (!vision) return ''
  
  if (vision.error) return '⚠️ 视觉分析失败'
  if (vision.matches_expectation === true) return '✅ 视觉分析：符合预期'
  if (vision.matches_expectation === false) return '❌ 视觉分析：不符合预期'
  return '👁️ 视觉分析结果'
}

// 获取视觉Alert类型
const getVisionAlertType = (step) => {
  const vision = parseVisionObservation(step.vision_observation)
  if (!vision) return 'info'
  
  if (vision.error) return 'warning'
  if (vision.matches_expectation === true) return 'success'
  if (vision.matches_expectation === false) return 'error'
  return 'info'
}

// 获取视觉观察文本
const getVisionObservation = (step) => {
  const vision = parseVisionObservation(step.vision_observation)
  if (!vision) return ''
  if (vision.error) return vision.error
  return vision.observation || ''
}

// 获取发现的问题列表
const getVisionIssues = (step) => {
  const vision = parseVisionObservation(step.vision_observation)
  if (!vision || !vision.issues) return []
  return vision.issues
}
```

## 数据流程

```
开始测试执行
  ↓
执行步骤1
  ↓
生成截图1
  ↓
🔍 立即调用Vision LLM分析截图1
  ↓
保存步骤1执行记录（包含vision_observation）
  ↓
执行步骤2
  ↓
生成截图2
  ↓
🔍 立即调用Vision LLM分析截图2
  ↓
保存步骤2执行记录（包含vision_observation）
  ↓
... 重复直到所有步骤完成
  ↓
测试执行完成
  ↓
前端显示：每个步骤下方都有独立的视觉分析结果
```

## 视觉观察数据结构

每个步骤的 `vision_observation` 字段存储JSON格式：

```json
{
  "observation": "截图显示的是一个登录页面，包含用户名和密码输入框...",
  "matches_expectation": true,
  "issues": []
}
```

或者不符合预期的情况：

```json
{
  "observation": "截图显示用户名已填入，但密码输入框为空...",
  "matches_expectation": false,
  "issues": [
    "用户名已输入，但未输入密码，无法完成登录流程。",
    "未执行登录操作（点击登录按钮），因此未进入首页。"
  ]
}
```

## 页面展示效果

### 执行步骤时间线

每个步骤卡片包含：

**步骤1** - 成功 ✅
- 步骤描述
- 执行状态
- 📸 截图
- **✅ 视觉分析：符合预期** （绿色）
  - 观察内容：截图显示的是一个登录页面，包含用户名和密码输入框、蓝色的'登录'按钮...

**步骤2** - 成功 ✅
- 步骤描述
- 执行状态
- 📸 截图
- **❌ 视觉分析：不符合预期** （红色）
  - 观察内容：截图显示用户名已填入，密码输入框为空...
  - 🚨 发现的问题：
    - 用户名已输入，但未输入密码
    - 未执行登录操作

## 优势对比

### 改进前（批量分析）

❌ 必须等待所有步骤执行完成  
❌ 无法提前发现问题  
❌ 观察记录不关联到具体步骤  
❌ 调试困难

### 改进后（实时分析）

✅ 每步执行完立即分析  
✅ 实时反馈问题  
✅ 每个步骤都有独立的观察记录  
✅ 清晰的问题定位  
✅ 更好的可追溯性

## 性能考虑

### 时间成本
- 每个步骤的视觉分析耗时：2-5秒
- 6个步骤的测试：额外增加 12-30秒
- **权衡**：实时反馈的价值 > 额外的时间成本

### API成本
- 每个步骤调用一次Vision API
- 成本与之前相同（分析的截图数量未变）
- **优势**：可以在步骤失败时提前停止，节省成本

## 注意事项

⚠️ **重要提示**:

1. **模型配置**: 必须使用支持视觉的模型（如 `qwen-vl-plus`, `gpt-4o`）
2. **API可用性**: 确保LLM API稳定可访问
3. **错误处理**: 视觉分析失败不影响测试执行
4. **数据库字段**: 需要执行数据库迁移脚本添加 `vision_observation` 字段

## 使用方法

### 1. 执行数据库迁移

```bash
cd backend
python add_vision_observation_column.py
```

### 2. 重启后端服务

后端会自动重载新代码

### 3. 执行测试

在前端页面执行任意测试用例

### 4. 查看结果

打开测试运行详情页面，每个步骤下方会显示：
- ✅ 步骤截图
- ✅ 视觉分析结果（符合/不符合预期）
- ✅ 观察描述
- ✅ 发现的问题列表

## 修改文件清单

### 后端
- ✅ `backend/app/models/step_execution.py` - 添加 vision_observation 字段
- ✅ `backend/app/services/playwright_executor.py` - 实时视觉分析逻辑
- ✅ `backend/app/api/endpoints/test_runs.py` - 传递LLM服务，保存观察结果
- ✅ `backend/app/schemas/test_run.py` - 更新Schema
- ✅ `backend/add_vision_observation_column.py` - 数据库迁移脚本（新建）

### 前端
- ✅ `frontend/src/views/TestRunDetail.vue` - 显示每步的视觉观察结果

## 日期

2025-10-23
