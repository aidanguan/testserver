# 截图显示问题修复

## 问题描述

测试执行完成后，页面显示的截图是占位符，无法看到实际的测试截图。

## 根本原因

1. **后端缺少静态文件服务**：没有配置路由来提供 `artifacts` 目录下的静态文件访问
2. **截图路径格式问题**：
   - 数据库存储的路径：`../artifacts\runs/4\screenshots\step_1.png`
   - 混合了反斜杠 `\` 和正斜杠 `/`
   - 包含了相对路径前缀 `../artifacts`
3. **前端路径处理不正确**：直接拼接路径，没有处理特殊字符和前缀

## 修复方案

### 1. 后端：添加静态文件服务

**文件**: `backend/main.py`

添加静态文件挂载：

```python
from fastapi.staticfiles import StaticFiles
import os

# 配置静态文件服务 - 提供测试工件访问
artifacts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts")
os.makedirs(artifacts_path, exist_ok=True)
app.mount("/artifacts", StaticFiles(directory=artifacts_path), name="artifacts")
```

这样就可以通过 `http://localhost:8000/artifacts/runs/4/screenshots/step_1.png` 访问截图了。

### 2. 前端：修复路径处理

**文件**: `frontend/src/views/TestRunDetail.vue`

修改 `getScreenshotUrl` 函数：

```javascript
const getScreenshotUrl = (path) => {
  if (!path) return ''
  
  // 处理路径：移除 ../artifacts 前缀，将反斜杠改为正斜杠
  let cleanPath = path.replace(/\\/g, '/')  // 将反斜杠改为正斜杠
  cleanPath = cleanPath.replace('../artifacts/', '')  // 移除 ../artifacts/ 前缀
  cleanPath = cleanPath.replace(/^\//, '')  // 移除开头的斜杠
  
  // 返回完整的 URL
  return `http://localhost:8000/artifacts/${cleanPath}`
}
```

## 路径转换示例

| 数据库存储路径 | 清理后路径 | 最终 URL |
|--------------|-----------|---------|
| `../artifacts\runs/4\screenshots\step_1.png` | `runs/4/screenshots/step_1.png` | `http://localhost:8000/artifacts/runs/4/screenshots/step_1.png` |
| `../artifacts\runs/4\screenshots\step_2.png` | `runs/4/screenshots/step_2.png` | `http://localhost:8000/artifacts/runs/4/screenshots/step_2.png` |

## 验证步骤

1. **重启后端服务器**（应用静态文件服务配置）
2. **刷新前端页面**
3. **查看测试运行详情**：应该能看到实际的测试截图

## 测试验证

访问以下 URL 应该能看到截图：
```
http://localhost:8000/artifacts/runs/4/screenshots/step_1.png
http://localhost:8000/artifacts/runs/4/screenshots/step_2.png
```

## 相关文件

- **修改**: `backend/main.py` - 添加静态文件服务
- **修改**: `frontend/src/views/TestRunDetail.vue` - 修复截图路径处理
- **截图位置**: `artifacts/runs/{run_id}/screenshots/step_{index}.png`

## 后续优化建议

1. **统一路径格式**：在 `PlaywrightExecutor` 中保存截图路径时，统一使用相对路径格式，避免平台差异
2. **配置化 API 地址**：将 `http://localhost:8000` 提取到配置文件中
3. **添加图片加载失败提示**：当截图加载失败时显示友好提示

## 日期

2025-10-23
