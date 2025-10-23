# 视觉分析结果显示功能

## 问题描述

用户反馈：
1. ✅ 视觉大模型分析功能已正常工作
2. ❌ 前端页面没有显示详细的视觉分析观察记录（observations）
3. ❌ 测试执行状态和LLM判定结果混淆

## 解决方案

### 后端修改

**文件**: `backend/app/api/endpoints/test_runs.py`

#### 修改点：将完整判定结果序列化为JSON

```python
# 保存判定结果
verdict_map = {"passed": LLMVerdict.PASSED, "failed": LLMVerdict.FAILED, "unknown": LLMVerdict.UNKNOWN}
test_run.llm_verdict = verdict_map.get(verdict_result.get("verdict"), LLMVerdict.UNKNOWN)

# 将完整的判定结果(包括 observations)序列化为 JSON 存储
import json
test_run.llm_reason = json.dumps(verdict_result, ensure_ascii=False)
```

**存储的JSON结构**:
```json
{
  "verdict": "failed",
  "confidence": 0.85,
  "reason": "只有1/6个步骤符合预期，测试失败",
  "observations": [
    {
      "step_index": 1,
      "type": "visual",
      "description": "截图显示的是一个登录页面...",
      "severity": "info"
    },
    {
      "step_index": 2,
      "type": "visual", 
      "description": "截图显示用户名已填入，密码为空...",
      "severity": "error"
    }
  ]
}
```

### 前端修改

**文件**: `frontend/src/views/TestRunDetail.vue`

#### 修改1：添加JSON解析逻辑

```javascript
// 解析判定结果
const parsedVerdict = computed(() => {
  if (!runDetail.value.llm_reason) return null
  
  try {
    // 尝试解析 JSON
    const parsed = JSON.parse(runDetail.value.llm_reason)
    return parsed
  } catch (e) {
    // 如果不是 JSON，返回简单对象
    return {
      reason: runDetail.value.llm_reason,
      observations: []
    }
  }
})

// 提取观察记录
const observations = computed(() => {
  if (!parsedVerdict.value || !parsedVerdict.value.observations) return []
  return parsedVerdict.value.observations
})

const hasObservations = computed(() => observations.value.length > 0)

// 显示的判定理由文本
const verdictReasonText = computed(() => {
  if (!parsedVerdict.value) return ''
  return parsedVerdict.value.reason || runDetail.value.llm_reason || ''
})
```

#### 修改2：添加视觉分析观察记录显示

```vue
<!-- 视觉分析观察记录 -->
<div v-if="hasObservations" style="margin-top: 20px">
  <h3>👁️ 视觉分析观察记录</h3>
  <el-timeline style="margin-top: 15px">
    <el-timeline-item
      v-for="obs in observations"
      :key="obs.step_index"
      :color="obs.severity === 'error' ? '#F56C6C' : '#67C23A'"
      :icon="obs.severity === 'error' ? 'CloseBold' : 'SuccessFilled'"
    >
      <el-card>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px">
          <span style="font-weight: bold; color: #409EFF;">步骤 {{ obs.step_index }}</span>
          <el-tag :type="obs.severity === 'error' ? 'danger' : 'success'" size="small">
            {{ obs.severity === 'error' ? '❌ 不符合预期' : '✅ 符合预期' }}
          </el-tag>
        </div>
        <div style="color: #606266; line-height: 1.6;">
          {{ obs.description }}
        </div>
      </el-card>
    </el-timeline-item>
  </el-timeline>
</div>
```

## 功能展示

### 1. LLM判定区域

显示在页面顶部的描述区域下方：

```
🤖 视觉大模型判定理由
只有1/6个步骤符合预期，测试失败
```

类型颜色：
- ✅ **passed** - 绿色成功提示
- ❌ **failed** - 红色失败提示
- ⚠️ **unknown** - 黄色警告提示

### 2. 视觉分析观察记录

时间线展示每个步骤的视觉分析结果：

**步骤1** ✅ 符合预期
```
截图显示的是一个登录页面，包含用户名和密码输入框、蓝色的'登录'按钮和白色的'SSO 登录'按钮。
页面顶部有'请您登录'标题和42lab的logo，背景为金色机器人形象和二进制代码图案。
```

**步骤2** ❌ 不符合预期
```
截图显示的是一个登录页面，用户名输入框中已填入 'Aidan'，密码输入框为空。
页面标题为 '请您登录'，并包含 '登录' 和 'SSO 登录' 两个按钮。
当前未进行登录操作，也未跳转到首页。
```

### 3. 执行步骤时间线

原有的步骤执行时间线保持不变，显示：
- 步骤编号和描述
- 执行状态（成功/失败/跳过）
- 截图
- 错误信息
- 执行耗时

## 数据流程

```
测试执行
  ↓
生成截图
  ↓
视觉大模型分析每个截图
  ↓
生成完整判定结果对象:
  {
    verdict: "passed/failed/unknown",
    confidence: 0.85,
    reason: "判定理由文本",
    observations: [
      {step_index, type, description, severity},
      ...
    ]
  }
  ↓
后端序列化为JSON存储到 llm_reason 字段
  ↓
前端解析JSON
  ↓
分别显示:
  - verdict → LLM判定标签
  - reason → 判定理由文本
  - observations → 观察记录时间线
```

## 用户体验改进

### 改进前
- ❌ 只显示测试执行状态（success/failed）
- ❌ LLM判定结果隐藏或不明显
- ❌ 看不到视觉分析的详细观察
- ❌ 无法理解为什么判定为失败

### 改进后
- ✅ 清晰区分执行状态和LLM判定
- ✅ 显眼的LLM判定理由
- ✅ 每个步骤的视觉观察记录
- ✅ 明确标注哪些步骤不符合预期
- ✅ 完整的判定依据供审查

## 注意事项

1. **向后兼容**: 如果 `llm_reason` 不是JSON格式（旧数据），会自动降级显示为纯文本
2. **视觉标识**: 使用emoji和颜色区分不同严重级别
3. **响应式布局**: 适配不同屏幕尺寸
4. **性能**: JSON解析使用computed缓存，避免重复计算

## 测试方法

1. 执行一个测试用例（确保项目配置了视觉模型如 `qwen-vl-plus`）
2. 等待测试完成
3. 打开测试运行详情页面
4. 检查页面显示:
   - [ ] LLM判定标签显示正确
   - [ ] 判定理由文本清晰
   - [ ] 观察记录时间线展示完整
   - [ ] 每个步骤的观察描述准确
   - [ ] 符合/不符合预期的标签正确

## 修改文件清单

- ✅ `backend/app/api/endpoints/test_runs.py` - 序列化完整判定结果
- ✅ `frontend/src/views/TestRunDetail.vue` - 解析和显示观察记录

## 日期

2025-10-23
