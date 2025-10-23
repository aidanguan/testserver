# 基于 Web 的自然语言驱动 UI 测试平台

一个创新的自动化测试平台，允许测试人员使用自然语言描述测试意图，自动生成并执行 UI 测试用例。

## 🎯 核心特性

- **自然语言驱动**：用自然语言描述测试场景，AI 自动生成标准化测试用例
- **智能脚本生成**：自动将测试用例转换为 Playwright 执行脚本
- **AI 结果判定**：使用 LLM 智能分析测试结果，提供详细判定理由
- **完整工件管理**：自动采集截图、日志、HAR 文件等测试证据
- **项目级配置**：支持多项目管理，每个项目可配置独立的 LLM
- **权限管理**：基于角色的访问控制（Admin/Member）

## 🏗️ 技术架构

### 后端技术栈
- **Web 框架**：FastAPI (Python)
- **数据库**：MySQL 8.0+
- **ORM**：SQLAlchemy
- **认证**：JWT + bcrypt
- **AI 集成**：OpenAI / Anthropic
- **自动化引擎**：Playwright
- **加密**：Cryptography (AES-256)

### 前端技术栈
- **框架**：Vue 3
- **状态管理**：Pinia
- **UI 组件**：Element Plus
- **路由**：Vue Router
- **HTTP 客户端**：Axios
- **构建工具**：Vite

## 📦 项目结构

```
testserver/
├── backend/                # 后端服务
│   ├── app/
│   │   ├── api/           # API 端点
│   │   │   └── endpoints/
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── projects.py
│   │   │       ├── test_cases.py
│   │   │       └── test_runs.py
│   │   ├── models/        # 数据模型
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── test_case.py
│   │   │   ├── test_run.py
│   │   │   ├── step_execution.py
│   │   │   └── audit_log.py
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # 业务逻辑
│   │   │   ├── llm_service.py
│   │   │   └── playwright_executor.py
│   │   ├── utils/         # 工具函数
│   │   │   ├── security.py
│   │   │   └── encryption.py
│   │   ├── config.py      # 配置管理
│   │   └── database.py    # 数据库连接
│   ├── main.py            # 应用入口
│   ├── init_db.sql        # 数据库初始化脚本
│   ├── requirements.txt   # Python 依赖
│   └── .env               # 环境变量
│
├── frontend/              # 前端应用
│   ├── src/
│   │   ├── api/          # API 客户端
│   │   ├── components/   # Vue 组件
│   │   ├── views/        # 页面视图
│   │   ├── stores/       # Pinia stores
│   │   ├── router/       # 路由配置
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
└── artifacts/            # 测试工件存储
    └── runs/
        └── {run_id}/
            ├── screenshots/
            ├── logs/
            └── network/
```

## 🚀 快速开始

### 前置要求

- Python 3.9+
- Node.js 16+
- MySQL 8.0+
- npm 或 yarn

### 1. 数据库初始化

```bash
# 创建数据库并执行初始化脚本
mysql -u root -p < backend/init_db.sql
```

默认会创建管理员账号：
- 用户名：`admin`
- 密码：`admin`

### 2. 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 编辑 .env 文件，设置数据库连接信息

# 安装 Playwright 浏览器
playwright install chromium

# 启动服务
python main.py
```

后端服务将在 `http://localhost:8000` 启动

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 `http://localhost:5173` 启动

### 4. 访问应用

打开浏览器访问 `http://localhost:5173`

使用默认账号登录：
- 用户名：`admin`
- 密码：`admin`

## 📖 使用指南

### 1. 创建项目

1. 登录后进入「项目管理」
2. 点击「创建项目」
3. 填写项目信息：
   - 项目名称
   - 测试站点 URL
   - LLM 配置（提供商、模型、API 密钥）
4. 保存

### 2. 创建测试用例

1. 进入项目详情页
2. 点击「创建测试用例」
3. 输入自然语言测试描述，例如：
   ```
   访问登录页面，输入用户名admin和密码admin，
   点击登录按钮，验证成功跳转到主页
   ```
4. 系统将自动生成：
   - 标准化测试步骤
   - Playwright 执行脚本
5. 可以手动调整生成的内容
6. 保存用例

### 3. 执行测试

1. 在测试用例列表中点击「执行」
2. 系统将：
   - 启动 Playwright 浏览器
   - 逐步执行测试脚本
   - 采集每步的截图
   - 记录控制台日志和网络请求
3. 执行完成后，LLM 自动分析结果
4. 查看详细的执行报告和判定理由

### 4. 查看结果

测试运行详情包含：
- 步骤执行时间线
- 每步的截图
- 控制台日志
- HAR 网络文件
- LLM 智能判定结果和理由

## 🔧 配置说明

### 后端环境变量 (.env)

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ui_test_platform

# JWT 配置
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 服务器配置
API_HOST=0.0.0.0
API_PORT=8000

# 工件存储路径
ARTIFACTS_PATH=../artifacts

# 执行配置
MAX_EXECUTION_TIME=300
```

### LLM 配置

支持的 LLM 提供商：

1. **OpenAI**
   - Provider: `openai`
   - 模型示例: `gpt-4`, `gpt-3.5-turbo`
   - 需要 OpenAI API Key

2. **Anthropic**
   - Provider: `anthropic`
   - 模型示例: `claude-3-opus`, `claude-3-sonnet`
   - 需要 Anthropic API Key

## 🛡️ 安全特性

- **密码加密**：使用 bcrypt 哈希存储密码
- **JWT 认证**：基于令牌的无状态认证
- **API 密钥加密**：LLM API 密钥使用 AES-256 加密存储
- **角色权限**：基于角色的访问控制
- **审计日志**：记录关键操作（待完善）

## 📊 数据模型

### 核心表结构

- **user**：用户表（认证、权限）
- **project**：项目表（包含 LLM 配置）
- **test_case**：测试用例表
- **test_run**：运行记录表
- **step_execution**：步骤执行记录表
- **audit_log**：审计日志表

## 🎯 MVP 范围

✅ **已实现**
- 用户认证与授权
- 项目管理（含 LLM 配置）
- 自然语言转测试用例
- 测试用例转 Playwright 脚本
- Playwright 脚本执行
- 截图、日志、HAR 采集
- LLM 智能结果判定
- 基础前端界面

⏳ **待完善**
- 完整的测试用例创建表单
- 测试运行详情页面
- 用户管理界面
- 审计日志查看
- 工件下载功能
- 数据统计和可视化

🚫 **MVP 不包含**
- 审批流程
- CI/CD 集成
- 消息通知
- 数据导入导出
- SSO 单点登录
- 视频录制
- 云并发执行

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证

## 👥 团队

本项目基于设计文档实现，旨在提供一个创新的自然语言驱动的 UI 自动化测试解决方案。

## 📞 支持

如有问题，请提交 Issue 或联系开发团队。

---

**注意**：这是一个 MVP 版本，部分功能仍在开发中。请勿在生产环境中使用未经充分测试的代码。
