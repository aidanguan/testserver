# 后端启动脚本

Write-Host "正在启动后端服务..." -ForegroundColor Green

# 检查虚拟环境
if (!(Test-Path "venv")) {
    Write-Host "创建 Python 虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# 安装依赖
Write-Host "检查并安装依赖..." -ForegroundColor Yellow
pip install -r requirements.txt

# 检查 Playwright
Write-Host "检查 Playwright 浏览器..." -ForegroundColor Yellow
playwright install chromium

# 启动服务
Write-Host "启动 FastAPI 服务..." -ForegroundColor Green
Write-Host "API 文档: http://localhost:8000/docs" -ForegroundColor Cyan
python main.py
