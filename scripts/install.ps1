# Woclaw 一键安装脚本
# 启明星 AI 助手

param(
    [switch]$SkipOllama,
    [switch]$UseAPI
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨" -ForegroundColor Cyan
Write-Host ""
Write-Host "   🌟 Woclaw - 启明星 AI 助手 🌟" -ForegroundColor White
Write-Host ""
Write-Host "   在黑暗中为你指引方向 ✨" -ForegroundColor Yellow
Write-Host ""
Write-Host "✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
Write-Host "📦 检查 Python..." -ForegroundColor Green
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $result = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            Write-Host "   ✅ 找到 Python: $result" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Host "   ❌ 未找到 Python" -ForegroundColor Red
    Write-Host ""
    Write-Host "   💡 请先安装 Python 3.10+" -ForegroundColor Yellow
    Write-Host "   下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# 检查 pip
Write-Host "📦 检查 pip..." -ForegroundColor Green
try {
    & $pythonCmd -m pip --version 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ pip 可用" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️ pip 可能有问题，尝试修复..." -ForegroundColor Yellow
    & $pythonCmd -m ensurepip --default-pip 2>&1 | Out-Null
}

# 创建虚拟环境（可选）
Write-Host ""
Write-Host "📁 设置安装目录..." -ForegroundColor Green
$installDir = Join-Path $HOME ".woclaw"
$venvDir = Join-Path $installDir "venv"

if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    Write-Host "   ✅ 创建配置目录: $installDir" -ForegroundColor Green
}

# 创建虚拟环境
Write-Host "🐍 创建虚拟环境..." -ForegroundColor Green
if (-not (Test-Path $venvDir)) {
    & $pythonCmd -m venv $venvDir 2>&1 | Out-Null
    Write-Host "   ✅ 虚拟环境已创建" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  虚拟环境已存在" -ForegroundColor Yellow
}

# 激活虚拟环境
$pipCmd = Join-Path $venvDir "Scripts\pip.exe"
$pythonVenv = Join-Path $venvDir "Scripts\python.exe"

# 安装 Woclaw
Write-Host ""
Write-Host "📥 安装 Woclaw..." -ForegroundColor Green
Write-Host "   正在安装核心依赖..." -ForegroundColor Gray

& $pipCmd install click rich aiohttp psutil pyscreeze Pillow pywinauto 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ 核心依赖安装失败" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ 核心依赖安装完成" -ForegroundColor Green

# 安装可选依赖
if ($UseAPI) {
    Write-Host "   正在安装 API 依赖..." -ForegroundColor Gray
    & $pipCmd install openai anthropic 2>&1 | Out-Null
    Write-Host "   ✅ API 依赖安装完成" -ForegroundColor Green
}

if (-not $SkipOllama) {
    Write-Host "   正在检查 Ollama..." -ForegroundColor Gray
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:11434" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($?) {
            Write-Host "   ✅ Ollama 服务正在运行" -ForegroundColor Green
        }
    } catch {
        Write-Host "   ℹ️  Ollama 未运行（可选）" -ForegroundColor Yellow
        Write-Host "      如需使用本地模型，请安装 Ollama: https://ollama.com" -ForegroundColor Gray
    }
}

# 安装 Woclaw 本身
Write-Host "   正在安装 Woclaw..." -ForegroundColor Gray
$woclawDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
& $pipCmd install -e $woclawDir 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ⚠️  Woclaw 安装可能有问题，但可以继续" -ForegroundColor Yellow
}
Write-Host "   ✅ 安装完成" -ForegroundColor Green

# 创建快捷方式（可选）
Write-Host ""
Write-Host "🔗 创建快捷命令..." -ForegroundColor Green
$woclawExe = Join-Path $venvDir "Scripts\woclaw.exe"

# 添加到 PATH 提示
$profilePath = $PROFILE
$profileDir = Split-Path -Parent $profilePath
if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "✨ 安装完成！星灵已准备就绪！✨" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 快速开始：" -ForegroundColor Green
Write-Host ""
Write-Host "   1. 启动交互模式：" -ForegroundColor White
Write-Host "      $woclawExe chat" -ForegroundColor Cyan
Write-Host ""
Write-Host "   2. 执行任务：" -ForegroundColor White
Write-Host "      $woclawExe run `"帮我整理下载文件夹`"" -ForegroundColor Cyan
Write-Host ""
Write-Host "   3. 查看状态：" -ForegroundColor White
Write-Host "      $woclawExe status" -ForegroundColor Cyan
Write-Host ""

if (-not $SkipOllama) {
    Write-Host "💡 提示：" -ForegroundColor Yellow
    Write-Host "   - 默认使用 Ollama 本地模型（免费）" -ForegroundColor Gray
    Write-Host "   - 如需使用云端模型，设置环境变量 WOCLAW_LLM=openai" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "✨ 让我们开始吧！星灵在等你~ 🌟" -ForegroundColor Yellow
Write-Host ""
