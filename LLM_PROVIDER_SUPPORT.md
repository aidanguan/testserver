# LLM 提供商支持说明

## ✅ 新增功能

系统已支持以下 LLM 提供商和功能：

### 1. 支持的 LLM 提供商

| 提供商 | 代码标识 | 说明 |
|--------|---------|------|
| OpenAI | `openai` | OpenAI Chat Completion API (gpt-4, gpt-3.5-turbo等) |
| OpenAI Completion | `openai-completion` | OpenAI 传统 Completion API |
| Anthropic | `anthropic` | Claude 系列模型 |
| 阿里云百炼 | `dashscope` | 通义千问系列模型 (qwen-plus, qwen-turbo等) |

### 2. 自定义 Base URL

所有提供商都支持自定义 API Base URL，适用于：
- ✅ 使用代理服务
- ✅ 使用自部署的兼容接口
- ✅ 使用第三方中转服务
- ✅ 内网部署的模型服务

---

## 📋 使用说明

### OpenAI

**默认 Base URL**: `https://api.openai.com/v1`

**示例配置**:
```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-4-turbo-preview",
  "llm_api_key": "sk-xxxxxxxxxxxxxxxx",
  "llm_base_url": null  // 可选，留空使用默认
}
```

**推荐模型**:
- `gpt-4-turbo-preview` - 最强性能
- `gpt-4` - 稳定版本
- `gpt-3.5-turbo` - 经济实用

---

### OpenAI Completion API

**默认 Base URL**: `https://api.openai.com/v1`

**示例配置**:
```json
{
  "llm_provider": "openai-completion",
  "llm_model": "gpt-3.5-turbo-instruct",
  "llm_api_key": "sk-xxxxxxxxxxxxxxxx",
  "llm_base_url": null
}
```

**说明**: 
- 使用传统的 Completion API（非 Chat API）
- 适用于某些特定场景或旧版模型

---

### 阿里云百炼 (DashScope)

**默认 Base URL**: `https://dashscope.aliyuncs.com/compatible-mode/v1`

**示例配置**:
```json
{
  "llm_provider": "dashscope",
  "llm_model": "qwen-plus",
  "llm_api_key": "sk-xxxxxxxxxxxxxxxx",
  "llm_base_url": null  // 使用默认百炼地址
}
```

**推荐模型**:
- `qwen-plus` - 通用场景
- `qwen-turbo` - 快速响应
- `qwen-max` - 最高性能

**获取 API Key**:
1. 访问 [阿里云百炼控制台](https://dashscope.console.aliyun.com/)
2. 开通百炼服务
3. 创建 API Key

---

### Anthropic

**默认 Base URL**: `https://api.anthropic.com`

**示例配置**:
```json
{
  "llm_provider": "anthropic",
  "llm_model": "claude-3-opus-20240229",
  "llm_api_key": "sk-ant-xxxxxxxxxxxxxxxx",
  "llm_base_url": null
}
```

**推荐模型**:
- `claude-3-opus-20240229` - 最强性能
- `claude-3-sonnet-20240229` - 平衡选择
- `claude-3-haiku-20240307` - 快速响应

---

## 🔧 前端配置

### 创建项目时的表单选项

```vue
<el-select v-model="projectForm.llm_provider">
  <el-option label="OpenAI" value="openai" />
  <el-option label="OpenAI Completion API" value="openai-completion" />
  <el-option label="Anthropic" value="anthropic" />
  <el-option label="阿里云百炼 (DashScope)" value="dashscope" />
</el-select>
```

### Base URL 输入

- **可选字段**: 不填写则使用默认值
- **示例值**:
  - OpenAI 代理: `https://your-proxy.com/v1`
  - 百炼: `https://dashscope.aliyuncs.com/compatible-mode/v1`
  - 自部署: `http://localhost:8080/v1`

---

## 💻 后端实现

### LLM 服务初始化

```python
llm_service = LLMService(
    provider="dashscope",           # 提供商
    model="qwen-plus",              # 模型名称
    api_key="sk-xxx",               # API密钥
    base_url="https://...",         # 自定义Base URL (可选)
    config={
        "temperature": 0.7,
        "max_tokens": 2000
    }
)
```

### 支持的提供商判断

```python
if self.provider in ["openai", "dashscope"]:
    # 使用 OpenAI Chat Completion API
    response = self.client.chat.completions.create(...)
    
elif self.provider == "openai-completion":
    # 使用 OpenAI Completion API
    response = self.client.completions.create(...)
    
elif self.provider == "anthropic":
    # 使用 Anthropic API
    response = self.client.messages.create(...)
```

---

## 📊 数据库变更

### 新增字段

**表名**: `project`

**新字段**: `llm_base_url`

```sql
ALTER TABLE project 
ADD COLUMN llm_base_url VARCHAR(500);
```

**说明**:
- 类型: `VARCHAR(500)`
- 可空: `NULL`
- 用途: 存储自定义的 LLM API Base URL

### 数据迁移

已提供迁移脚本: `backend/add_llm_base_url.py`

```bash
cd backend
python add_llm_base_url.py
```

---

## 🧪 测试示例

### 1. 测试 OpenAI

```python
# 使用默认 Base URL
llm = LLMService("openai", "gpt-4", "sk-xxx")

# 使用自定义 Base URL (如代理)
llm = LLMService("openai", "gpt-4", "sk-xxx", 
                 base_url="https://proxy.com/v1")
```

### 2. 测试百炼

```python
# 使用默认百炼地址
llm = LLMService("dashscope", "qwen-plus", "sk-xxx")

# 等价于
llm = LLMService("dashscope", "qwen-plus", "sk-xxx",
                 base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
```

### 3. 测试 Completion API

```python
llm = LLMService("openai-completion", "gpt-3.5-turbo-instruct", "sk-xxx")
```

---

## 🔍 常见问题

### Q: 百炼如何收费？
**A**: 阿里云百炼按 Token 计费，有免费额度。查看[官方定价](https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-thousand-questions-metering-and-billing)

### Q: 如何使用自己部署的模型？
**A**: 只要模型服务兼容 OpenAI API 格式，填入自定义 Base URL 即可

### Q: Base URL 填错了怎么办？
**A**: 可以在项目管理中编辑项目，修改 Base URL

### Q: 不同提供商的响应格式一样吗？
**A**: 系统已做统一处理，返回格式一致

---

## 📝 修改的文件

### 后端
- ✅ `app/models/project.py` - 添加 llm_base_url 字段
- ✅ `app/schemas/project.py` - 更新 Schema
- ✅ `app/services/llm_service.py` - 支持多提供商和自定义 Base URL
- ✅ `app/api/endpoints/test_cases.py` - 传递 base_url 参数
- ✅ `add_llm_base_url.py` - 数据库迁移脚本

### 前端
- ✅ `views/ProjectList.vue` - 添加提供商选项和 Base URL 输入
- ✅ `views/ProjectDetail.vue` - 显示 Base URL 信息

---

## 🎯 下一步

1. **创建测试项目**
   - 选择 "阿里云百炼" 作为提供商
   - 填入百炼 API Key
   - 留空 Base URL（使用默认）

2. **测试用例生成**
   - 输入自然语言描述
   - 系统调用百炼生成测试用例

3. **执行测试**
   - 生成 Playwright 脚本
   - 执行自动化测试
   - LLM 智能判定结果

---

## ✨ 优势

1. **灵活性**
   - 支持多种 LLM 提供商
   - 可自定义 API 地址
   - 适配各种部署场景

2. **成本优化**
   - 可选择性价比高的模型
   - 支持国内服务商（百炼）
   - 避免网络问题

3. **兼容性**
   - 统一的接口调用
   - 支持 OpenAI 兼容的第三方服务
   - 易于扩展新提供商

---

**祝使用愉快！** 🚀

如有问题，请查看系统日志或联系技术支持。
