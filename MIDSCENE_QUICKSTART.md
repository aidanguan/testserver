# Midscene 快速开始指南

## 🚀 快速安装

### 1. 安装 Node.js 依赖

```powershell
cd backend\midscene
npm install
```

### 2. 安装 Playwright 浏览器

```powershell
npx playwright install chromium
```

### 3. 数据库迁移

```powershell
cd ..
python add_executor_type.py
```

### 4. 测试安装

创建测试脚本 `test_midscene.py`:

```python
import sys
sys.path.append('backend')

from app.services.midscene_executor import MidsceneExecutor

executor = MidsceneExecutor("./artifacts")
status = executor.check_installation()

if status['installed']:
    print("✅ Midscene 安装成功！")
    print(f"   - Node modules: {status['node_modules_exists']}")
    print(f"   - 目录: {status['midscene_dir']}")
else:
    print("❌ Midscene 未安装")
    print("   运行安装命令: cd backend/midscene && npm install")
```

运行测试:
```powershell
python test_midscene.py
```

## 📖 使用示例

### 创建 Midscene 测试用例

通过 API 创建:

```json
POST /api/cases/generate-from-nl
{
  "project_id": 1,
  "natural_language": "打开百度首页，在搜索框输入 Midscene，点击搜索按钮，验证搜索结果加载完成"
}
```

生成脚本时选择 Midscene:
```json
POST /api/cases/generate-midscene-script
{
  "test_case_id": 1
}
```

### 执行测试

```json
POST /api/cases/{case_id}/execute
```

系统会自动根据测试用例的 `executor_type` 选择 Playwright 或 Midscene 执行器。

## 🎯 Midscene vs Playwright

| 特性 | Midscene | Playwright |
|------|----------|-----------|
| 元素定位 | AI 自然语言 | CSS 选择器 |
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 灵活性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 性能 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 成本 | 需 LLM API | 免费 |

## ⚙️ 配置说明

在项目设置中配置 LLM:
- **OpenAI**: 推荐使用 gpt-4o 或 gpt-4-vision
- **Azure OpenAI**: 配置 base_url
- **国产模型**: 支持通义千问等

## 🔍 故障排查

### Midscene 执行失败?

1. 检查 Node.js 是否安装: `node --version`
2. 检查依赖是否安装: `cd backend/midscene && ls node_modules`
3. 查看执行日志中的详细错误信息
4. 确认 LLM API 密钥正确配置

### 浏览器未安装?

```powershell
cd backend\midscene
npx playwright install chromium
```

## 📚 更多资源

- [完整集成文档](./MIDSCENE_INTEGRATION.md)
- [Midscene 官网](https://midscenejs.com)
- [示例项目](https://github.com/web-infra-dev/midscene-example)
