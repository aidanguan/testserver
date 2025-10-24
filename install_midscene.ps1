# Midscene 安装脚本
# 自动安装所有必需的依赖

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Midscene 集成安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Node.js
Write-Host "[1/5] 检查 Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Node.js 已安装: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Node.js 未安装" -ForegroundColor Red
    Write-Host "  请先安装 Node.js: https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# 检查 Python
Write-Host "[2/5] 检查 Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Python 已安装: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python 未安装" -ForegroundColor Red
    Write-Host "  请先安装 Python: https://www.python.org/" -ForegroundColor Red
    exit 1
}

# 安装 Node.js 依赖
Write-Host "[3/5] 安装 Midscene 依赖..." -ForegroundColor Yellow
Set-Location backend\midscene
npm install
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Midscene 依赖安装成功" -ForegroundColor Green
} else {
    Write-Host "  ✗ Midscene 依赖安装失败" -ForegroundColor Red
    exit 1
}

# 安装 Playwright 浏览器
Write-Host "[4/5] 安装 Playwright 浏览器..." -ForegroundColor Yellow
npx playwright install chromium
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Playwright 浏览器安装成功" -ForegroundColor Green
} else {
    Write-Host "  ✗ Playwright 浏览器安装失败" -ForegroundColor Red
    exit 1
}

# 运行数据库迁移
Write-Host "[5/5] 运行数据库迁移..." -ForegroundColor Yellow
Set-Location ..
python add_executor_type.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ 数据库迁移成功" -ForegroundColor Green
} else {
    Write-Host "  ✗ 数据库迁移失败" -ForegroundColor Red
    Write-Host "  如果数据库未运行，可以稍后手动执行：python backend/add_executor_type.py" -ForegroundColor Yellow
}

# 创建环境变量文件
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  配置环境变量" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$envFile = "midscene\.env"
if (-not (Test-Path $envFile)) {
    Write-Host "创建 .env 文件..." -ForegroundColor Yellow
    Copy-Item "midscene\.env.example" $envFile
    Write-Host "  ✓ 已创建 .env 文件" -ForegroundColor Green
    Write-Host ""
    Write-Host "  ⚠️  请编辑 backend\midscene\.env 文件，配置你的 LLM API 密钥" -ForegroundColor Yellow
    Write-Host "  例如：OPENAI_API_KEY=sk-..." -ForegroundColor Yellow
} else {
    Write-Host "  ✓ .env 文件已存在" -ForegroundColor Green
}

# 完成
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  安装完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "下一步:" -ForegroundColor Cyan
Write-Host "1. 配置 LLM API 密钥: backend\midscene\.env" -ForegroundColor White
Write-Host "2. 运行测试: python test_midscene_integration.py" -ForegroundColor White
Write-Host "3. 启动后端: cd backend; python main.py" -ForegroundColor White
Write-Host "4. 启动前端: cd frontend; npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "文档:" -ForegroundColor Cyan
Write-Host "- 快速开始: MIDSCENE_QUICKSTART.md" -ForegroundColor White
Write-Host "- 完整指南: MIDSCENE_INTEGRATION.md" -ForegroundColor White
Write-Host "- 集成总结: MIDSCENE_INTEGRATION_SUMMARY.md" -ForegroundColor White
Write-Host ""
