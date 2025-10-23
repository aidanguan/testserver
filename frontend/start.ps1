# 前端启动脚本

Write-Host "正在启动前端应用..." -ForegroundColor Green

# 检查 node_modules
if (!(Test-Path "node_modules")) {
    Write-Host "安装依赖..." -ForegroundColor Yellow
    npm install
}

# 启动开发服务器
Write-Host "启动 Vite 开发服务器..." -ForegroundColor Green
Write-Host "应用地址: http://localhost:5173" -ForegroundColor Cyan
npm run dev
