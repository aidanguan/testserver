# 快速启动指南

本指南帮助您在 5 分钟内快速启动项目。

## 前置条件

确保已安装:
- ✅ Python 3.9+
- ✅ Node.js 16+
- ✅ MySQL 8.0+

## Step 1: 数据库初始化 (1分钟)

```bash
# 登录 MySQL 并执行初始化脚本
mysql -u root -p < backend/init_db.sql

# 或在 MySQL 命令行中执行
mysql> source c:/AI/testserver/backend/init_db.sql
```

这将创建:
- 数据库 `ui_test_platform`
- 所有必要的表
- 默认管理员账号 (admin/admin)

## Step 2: 后端启动 (2分钟)

### Windows

```powershell
cd backend

# 使用启动脚本 (推荐)
.\start.ps1

# 或手动执行
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python main.py
```

### Linux/macOS

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
playwright install chromium

# 启动服务
python main.py
```

后端将在 `http://localhost:8000` 启动

✅ 验证: 访问 http://localhost:8000/docs 查看 API 文档

## Step 3: 前端启动 (2分钟)

新开一个终端窗口:

### Windows

```powershell
cd frontend

# 使用启动脚本 (推荐)
.\start.ps1

# 或手动执行
npm install
npm run dev
```

### Linux/macOS

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 启动

## Step 4: 登录系统

1. 打开浏览器访问 http://localhost:5173
2. 使用默认账号登录:
   - 用户名: `admin`
   - 密码: `admin`
3. 🎉 开始使用！

## 快速体验

### 创建第一个测试项目

1. 点击左侧菜单「项目管理」
2. 点击「创建项目」按钮
3. 填写表单:
   - 项目名称: `示例项目`
   - 描述: `我的第一个测试项目`
   - 测试站点: `https://example.com`
   - LLM 提供商: `openai` (或 `anthropic`)
   - 模型: `gpt-4` (或 `claude-3-sonnet`)
   - API 密钥: 你的 LLM API 密钥
4. 点击「创建」

### 创建第一个测试用例

1. 进入刚创建的项目
2. 点击「创建测试用例」
3. 输入自然语言描述，例如:
   ```
   打开网站首页，验证页面标题包含Example Domain，
   检查页面中是否显示了示例文本
   ```
4. 系统将自动生成:
   - 标准化测试步骤
   - Playwright 执行脚本
5. 保存用例

### 执行测试

1. 在测试用例列表中，点击「执行」按钮
2. 系统将自动:
   - 启动浏览器
   - 执行测试步骤
   - 采集截图和日志
   - AI 分析结果
3. 查看执行报告

## 常见问题

### Q: 后端启动失败 - 数据库连接错误

**A:** 检查 `backend/.env` 文件中的数据库配置:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_NAME=ui_test_platform
```

### Q: Playwright 安装失败

**A:** 手动安装:
```bash
playwright install chromium
```

如果仍然失败，安装系统依赖:
```bash
playwright install-deps
```

### Q: 前端无法连接后端

**A:** 
1. 确认后端已启动 (http://localhost:8000)
2. 检查浏览器控制台是否有 CORS 错误
3. 检查 `frontend/vite.config.js` 中的代理配置

### Q: LLM API 调用失败

**A:**
1. 检查 API 密钥是否正确
2. 确认网络可以访问 LLM API
3. 检查 API 配额是否充足

### Q: 默认密码不正确

**A:** 数据库初始化脚本中的默认密码哈希对应 `admin`
如果无法登录，重新执行初始化脚本:
```bash
mysql -u root -p ui_test_platform < backend/init_db.sql
```

## 下一步

- 📖 阅读 [README.md](README.md) 了解完整功能
- 🚀 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 了解部署方案
- 🛠️ 探索 API 文档 http://localhost:8000/docs

## 技术支持

如遇到问题:
1. 检查终端/控制台的错误信息
2. 查看日志文件
3. 提交 Issue 描述问题

---

**祝使用愉快！** 🎉
