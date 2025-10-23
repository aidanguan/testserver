# 视觉大模型测试分析功能

## 功能概述

测试执行完成后，系统会使用视觉大模型（Vision LLM）分析每个步骤的截图，与预期结果对比，智能判断测试是否通过。

## 核心改进

### 1. **视觉分析** 👁️
- ✅ 对每个测试步骤的截图使用视觉大模型分析
- ✅ 识别截图中的UI元素、文本、布局等
- ✅ 判断截图内容是否符合预期结果

### 2. **智能判定** 🤖
- ✅ 综合所有截图分析结果
- ✅ 结合步骤执行状态
- ✅ 给出最终测试判定（通过/失败/未知）

### 3. **详细反馈** 📝
- ✅ 每个步骤的视觉观察结果
- ✅ 发现的问题列表
- ✅ 判定置信度和理由

## 工作流程

```
执行测试
  ↓
生成每个步骤的截图
  ↓
对每个截图调用视觉大模型
  ↓
视觉模型分析：
  - 观察到的UI内容
  - 是否符合预期
  - 发现的问题
  ↓
综合所有分析结果
  ↓
判定测试结果：
  - passed: 所有步骤符合预期
  - failed: 多数步骤不符合预期
  - unknown: 部分步骤不确定
  ↓
保存判定结果和观察记录
```

## 后端实现

### 修改文件

**文件**: `backend/app/services/llm_service.py`

#### 1. 修改 `analyze_test_result` 方法

```python
def analyze_test_result(self, expected_result: str, step_screenshots: List[str], 
                        console_logs: List[str], step_statuses: List[Dict[str, Any]]) -> Dict[str, Any]:
    # 如果没有截图，使用基础判定
    if not step_screenshots:
        return self._analyze_without_vision(expected_result, console_logs, step_statuses)
    
    # 使用视觉大模型分析每个截图
    screenshot_analyses = []
    for idx, screenshot_path in enumerate(step_screenshots):
        try:
            analysis = self._analyze_screenshot_with_vision(
                screenshot_path, expected_result, 
                step_statuses[idx] if idx < len(step_statuses) else None
            )
            screenshot_analyses.append({
                "step_index": idx + 1,
                "screenshot_path": screenshot_path,
                "analysis": analysis
            })
        except Exception as e:
            screenshot_analyses.append({
                "step_index": idx + 1,
                "screenshot_path": screenshot_path,
                "analysis": {"error": str(e)}
            })
    
    # 综合所有分析结果
    return self._综合判定(expected_result, screenshot_analyses, console_logs, step_statuses)
```

#### 2. 新增 `_analyze_screenshot_with_vision` 方法

```python
def _analyze_screenshot_with_vision(self, screenshot_path: str, expected_result: str, 
                                     step_status: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    import base64
    
    # 读取截图并转为base64
    with open(screenshot_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    step_desc = step_status.get("description", "") if step_status else ""
    
    prompt = f"""你是一个专业的UI测试分析专家。请分析这张截图。

步骤描述: {step_desc}
预期结果: {expected_result}

请描述你在截图中看到的内容，并判断是否符合预期。返回JSON格式：
{{
  "observation": "具体观察到的内容",
  "matches_expectation": true/false,
  "issues": ["发现的问题列表"]
}}"""
    
    # 调用视觉大模型（OpenAI Vision API）
    if self.provider in ["openai", "dashscope"]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                ]
            }],
            max_tokens=500
        )
        result_text = response.choices[0].message.content
        return json.loads(result_text.strip())
```

#### 3. 新增 `_综合判定` 方法

```python
def _综合判定(self, expected_result: str, screenshot_analyses: List[Dict], 
            console_logs: List[str], step_statuses: List[Dict[str, Any]]) -> Dict[str, Any]:
    # 统计符合预期的截图数量
    matching_count = sum(1 for a in screenshot_analyses 
                        if a.get("analysis", {}).get("matches_expectation") == True)
    total_count = len(screenshot_analyses)
    
    # 收集所有观察
    observations = []
    for analysis in screenshot_analyses:
        if "analysis" in analysis and "observation" in analysis["analysis"]:
            observations.append({
                "step_index": analysis["step_index"],
                "type": "visual",
                "description": analysis["analysis"]["observation"],
                "severity": "error" if not analysis["analysis"].get("matches_expectation") else "info"
            })
    
    # 判定逻辑
    if matching_count == total_count:
        verdict = "passed"
        confidence = 0.9
        reason = f"所有{total_count}个步骤的截图分析都符合预期结果"
    elif matching_count >= total_count * 0.7:
        verdict = "unknown"
        confidence = 0.6
        reason = f"{matching_count}/{total_count}个步骤符合预期，部分步骤存在问题"
    else:
        verdict = "failed"
        confidence = 0.85
        reason = f"只有{matching_count}/{total_count}个步骤符合预期，测试失败"
    
    return {
        "verdict": verdict,
        "confidence": confidence,
        "reason": reason,
        "observations": observations
    }
```

## 视觉模型支持

### 支持的模型

| 提供商 | 模型 | 说明 |
|--------|------|------|
| OpenAI | gpt-4-vision-preview | GPT-4 Vision |
| OpenAI | gpt-4o | 最新多模态模型 |
| DashScope | qwen-vl-plus | 阿里千问视觉模型 |

### 模型配置

在项目配置中指定支持视觉的模型：

```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-4o",
  "llm_api_key": "sk-...",
  "llm_base_url": "https://api.openai.com/v1"
}
```

## 分析示例

### 输入

**步骤1截图**: 登录页面
**步骤描述**: "打开登录页面"
**预期结果**: "显示登录表单，包含用户名和密码输入框"

### Vision LLM 分析

```json
{
  "observation": "截图显示一个登录页面，包含'用户名'和'密码'两个输入框，以及一个蓝色的'登录'按钮。页面顶部有网站Logo。",
  "matches_expectation": true,
  "issues": []
}
```

### 最终判定

如果所有步骤都符合预期：

```json
{
  "verdict": "passed",
  "confidence": 0.9,
  "reason": "所有3个步骤的截图分析都符合预期结果",
  "observations": [
    {
      "step_index": 1,
      "type": "visual",
      "description": "截图显示登录页面，包含用户名和密码输入框",
      "severity": "info"
    },
    {
      "step_index": 2,
      "type": "visual",
      "description": "成功填写用户名和密码",
      "severity": "info"
    },
    {
      "step_index": 3,
      "type": "visual",
      "description": "点击登录后跳转到仪表板页面",
      "severity": "info"
    }
  ]
}
```

## 判定规则

### Passed（通过）
- 条件：100% 步骤符合预期
- 置信度：0.9
- 示例：3/3 步骤符合预期

### Unknown（未知）
- 条件：70%-99% 步骤符合预期
- 置信度：0.6
- 示例：2/3 步骤符合预期

### Failed（失败）
- 条件：< 70% 步骤符合预期
- 置信度：0.85
- 示例：1/3 步骤符合预期

## 优势

1. **智能分析** - 不仅看步骤状态，还分析实际UI效果
2. **准确判定** - 基于视觉证据，更接近人工测试
3. **详细反馈** - 提供每个步骤的观察结果
4. **自动化** - 无需人工查看截图
5. **可追溯** - 保留所有观察记录供审查

## 使用场景

### 场景 1: UI 布局验证
- 验证页面元素是否正确显示
- 检查布局是否符合设计
- 发现视觉缺陷

### 场景 2: 文本内容验证
- 验证页面文本是否正确
- 检查提示信息是否显示
- 确认错误消息内容

### 场景 3: 交互结果验证
- 验证点击后的页面变化
- 检查表单提交后的反馈
- 确认导航是否正确

## 注意事项

⚠️ **重要提示**:

1. **模型选择**: 必须使用支持视觉的模型（如 gpt-4o, qwen-vl-plus）
2. **API 成本**: Vision API 调用成本较高，每个截图都会调用
3. **处理时间**: 视觉分析需要额外时间（每张图 2-5 秒）
4. **图片质量**: 截图质量影响分析准确度
5. **网络要求**: 需要稳定的网络上传截图到 LLM API

## 最佳实践

1. **清晰的预期结果**: 编写具体、明确的预期结果描述
2. **关键步骤截图**: 确保关键验证点都有截图
3. **合理步骤数**: 避免过多步骤导致成本过高
4. **检查分析结果**: 查看observations了解详细判定依据
5. **调整判定阈值**: 根据实际情况调整70%的阈值

## 后续优化建议

1. **缓存机制**: 相同截图避免重复分析
2. **并行分析**: 多个截图并行调用Vision API
3. **区域标注**: 在截图上标注关键元素
4. **对比分析**: 对比期望截图和实际截图
5. **自定义规则**: 允许配置判定规则和阈值

## 修改文件清单

- ✅ `backend/app/services/llm_service.py` - 添加视觉分析功能

## 测试建议

1. **配置视觉模型**: 将项目LLM模型改为 `gpt-4o` 或 `qwen-vl-plus`
2. **执行测试**: 运行一个测试用例
3. **查看判定**: 检查LLM判定结果和理由
4. **查看观察**: 查看observations字段的详细分析

## 日期

2025-10-23
