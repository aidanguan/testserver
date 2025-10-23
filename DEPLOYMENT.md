# 部署指南

## 环境准备

### 系统要求
- 操作系统: Windows 10+, Linux, macOS
- Python: 3.9+
- Node.js: 16+
- MySQL: 8.0+

### 依赖安装

#### Windows
```powershell
# Python
python --version

# Node.js
node --version
npm --version

# MySQL
# 从官网下载并安装 MySQL 8.0+
```

#### Linux (Ubuntu/Debian)
```bash
# Python
sudo apt update
sudo apt install python3.9 python3-pip python3-venv

# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# MySQL
sudo apt install mysql-server
sudo mysql_secure_installation
```

## 数据库初始化

### 1. 创建数据库

```bash
# 登录 MySQL
mysql -u root -p

# 或者直接执行初始化脚本
mysql -u root -p < backend/init_db.sql
```

### 2. 验证数据库

```sql
USE ui_test_platform;
SHOW TABLES;

-- 应该看到以下表:
-- user, project, test_case, test_run, step_execution, audit_log
```

### 3. 验证默认管理员账号

```sql
SELECT username, role FROM user WHERE username = 'admin';
```

## 后端部署

### 1. 环境配置

```bash
cd backend

# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
# 修改数据库连接信息和其他配置
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 安装 Playwright 浏览器

```bash
playwright install chromium
```

### 5. 启动服务

```bash
# 开发模式
python main.py

# 生产模式 (使用 Uvicorn)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. 验证后端

访问 http://localhost:8000/docs 查看 API 文档

## 前端部署

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 开发模式启动

```bash
npm run dev
```

访问 http://localhost:5173

### 3. 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录

### 4. 生产部署

#### 使用 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端 API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 使用 Docker 部署 (可选)

### 后端 Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 前端 Dockerfile

```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

### Docker Compose

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: ui_test_platform
    volumes:
      - mysql-data:/var/lib/mysql
      - ./backend/init_db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"
  
  backend:
    build: ./backend
    depends_on:
      - mysql
    environment:
      DB_HOST: mysql
      DB_USER: root
      DB_PASSWORD: rootpassword
    volumes:
      - ./artifacts:/app/artifacts
    ports:
      - "8000:8000"
  
  frontend:
    build: ./frontend
    depends_on:
      - backend
    ports:
      - "80:80"

volumes:
  mysql-data:
```

## 常见问题

### 1. 数据库连接失败

检查:
- MySQL 服务是否启动
- .env 中的数据库配置是否正确
- 防火墙设置

### 2. Playwright 安装失败

```bash
# 手动安装浏览器
playwright install chromium

# 如果需要系统依赖
playwright install-deps
```

### 3. 前端无法连接后端

检查:
- 后端服务是否启动
- vite.config.js 中的代理配置
- CORS 设置

### 4. LLM API 调用失败

检查:
- API 密钥是否正确
- 网络连接
- API 配额

## 监控和日志

### 后端日志

```bash
# 查看应用日志
tail -f logs/app.log

# 使用 systemd 管理服务
sudo journalctl -u testplatform-backend -f
```

### 性能监控

推荐使用:
- Prometheus + Grafana
- New Relic
- DataDog

## 备份策略

### 数据库备份

```bash
# 每日备份脚本
mysqldump -u root -p ui_test_platform > backup_$(date +%Y%m%d).sql

# 定时任务
crontab -e
0 2 * * * /path/to/backup.sh
```

### 工件备份

```bash
# 定期备份 artifacts 目录
tar -czf artifacts_backup_$(date +%Y%m%d).tar.gz artifacts/
```

## 安全建议

1. 修改默认管理员密码
2. 使用强密码策略
3. 定期更新依赖包
4. 启用 HTTPS
5. 配置防火墙规则
6. 定期备份数据
7. 监控异常访问

## 扩展性

### 水平扩展

- 使用负载均衡器分发请求
- 部署多个后端实例
- 使用 Redis 做 session 共享

### 性能优化

- 启用数据库索引
- 使用缓存 (Redis)
- CDN 加速静态资源
- 数据库读写分离

---

部署完成后，访问应用并使用默认账号登录:
- 用户名: `admin`
- 密码: `admin`

**重要**: 首次登录后请立即修改默认密码！
