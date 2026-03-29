# Woclaw 一键安装脚本（真正傻瓜式）
# 用户只需运行一行命令：irm https://get.woclaw.dev | iex

param(
    [string]$Model = "ollama",  # ollama, openai, claude, deepseek
    [string]$ModelName = "llama3.2",
    [string]$APIKey = "",
    [switch]$NoGUI,
    [switch]$Uninstall
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-Banner {
    Clear-Host
    Write-Host ""
    Write-Host "  ╔═══════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║                                                   ║" -ForegroundColor Cyan
    Write-Host "  ║      🌟 Woclaw - 启明星 AI 助手 🌟               ║" -ForegroundColor Cyan
    Write-Host "  ║                                                   ║" -ForegroundColor Cyan
    Write-Host "  ║      让启明星照亮你的电脑世界                    ║" -ForegroundColor Cyan
    Write-Host "  ║                                                   ║" -ForegroundColor Cyan
    Write-Host "  ╚═══════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-Host "  ▶ $Message" -ForegroundColor White
}

function Write-Success {
    param([string]$Message)
    Write-Host "    ✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "    ❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "    ℹ️  $Message" -ForegroundColor Yellow
}

function Install-Python {
    Write-Step "检查 Python..."
    
    # 检查已有 Python
    $pythonCmd = $null
    foreach ($cmd in @("python", "python3", "py")) {
        try {
            $version = & $cmd --version 2>&1
            if ($version -match "3\.(\d+)") {
                $minor = [int]$matches[1]
                if ($minor -ge 10) {
                    $pythonCmd = $cmd
                    Write-Success "Python 已安装: $version"
                    return $pythonCmd
                }
            }
        } catch {}
    }
    
    # 需要安装 Python
    Write-Info "未找到 Python 3.10+，正在自动安装..."
    
    $pythonUrl = "https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe"
    $installerPath = Join-Path $env:TEMP "python-installer.exe"
    
    try {
        # 下载安装包
        Write-Info "下载 Python 安装包..."
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
        
        # 静默安装
        Write-Info "安装 Python（可能需要几分钟）..."
        $installArgs = "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0"
        Start-Process -FilePath $installerPath -ArgumentList $installArgs -Wait -NoNewWindow
        
        # 刷新环境变量
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        
        # 再次检查
        foreach ($cmd in @("python", "py")) {
            try {
                $null = & $cmd --version 2>&1
                if ($? -and (& $cmd -c "import sys; print(sys.version_info.minor)" 2>&1) -ge 10) {
                    $pythonCmd = $cmd
                    Write-Success "Python 安装成功"
                    return $pythonCmd
                }
            } catch {}
        }
        
        Write-Error "Python 安装失败"
        return $null
        
    } catch {
        Write-Error "Python 安装失败: $_"
        return $null
    } finally {
        if (Test-Path $installerPath) {
            Remove-Item $installerPath -Force
        }
    }
}

function Install-Ollama {
    Write-Step "检查 Ollama（本地模型引擎）..."
    
    # 检查已安装
    $ollamaPath = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
    if (Test-Path $ollamaPath) {
        Write-Success "Ollama 已安装"
        
        # 检查服务
        try {
            $null = Invoke-WebRequest -Uri "http://localhost:11434" -TimeoutSec 2
            Write-Success "Ollama 服务正在运行"
        } catch {
            Write-Info "启动 Ollama 服务..."
            Start-Process $ollamaPath -WindowStyle Hidden
            Start-Sleep -Seconds 3
        }
        
        return $true
    }
    
    # 自动安装 Ollama
    Write-Info "正在安装 Ollama..."
    
    $ollamaUrl = "https://ollama.com/download/OllamaSetup.exe"
    $installerPath = Join-Path $env:TEMP "ollama-setup.exe"
    
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $ollamaUrl -OutFile $installerPath -UseBasicParsing
        
        Write-Info "安装 Ollama（请按提示完成安装）..."
        Start-Process -FilePath $installerPath -Wait
        
        # 启动服务
        Start-Sleep -Seconds 5
        if (Test-Path $ollamaPath) {
            Start-Process $ollamaPath -WindowStyle Hidden
            Start-Sleep -Seconds 3
            Write-Success "Ollama 安装成功"
            return $true
        }
    } catch {
        Write-Error "Ollama 安装失败: $_"
    } finally {
        if (Test-Path $installerPath) {
            Remove-Item $installerPath -Force
        }
    }
    
    return $false
}

function Install-Woclaw {
    param([string]$PythonCmd)
    
    Write-Step "安装 Woclaw..."
    
    # 创建安装目录
    $installDir = Join-Path $env:USERPROFILE ".woclaw"
    $venvDir = Join-Path $installDir "venv"
    
    if (-not (Test-Path $installDir)) {
        New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    }
    
    # 创建虚拟环境
    Write-Info "创建虚拟环境..."
    & $PythonCmd -m venv $venvDir 2>&1 | Out-Null
    
    $pipCmd = Join-Path $venvDir "Scripts\pip.exe"
    $pythonExe = Join-Path $venvDir "Scripts\python.exe"
    
    # 升级 pip
    & $pythonExe -m pip install --upgrade pip 2>&1 | Out-Null
    
    # 安装核心依赖
    Write-Info "安装核心依赖..."
    $coreDeps = @(
        "click",
        "rich",
        "aiohttp",
        "psutil",
        "pywinauto",
        "pyscreeze",
        "Pillow",
        "playwright"
    )
    
    foreach ($dep in $coreDeps) {
        & $pipCmd install $dep --quiet 2>&1 | Out-Null
    }
    
    # 安装 Woclaw
    Write-Info "安装 Woclaw 核心程序..."
    & $pipCmd install "git+https://github.com/badhope/Woclaw.git" --quiet 2>&1 | Out-Null
    
    # 安装 Playwright 浏览器
    Write-Info "安装浏览器组件..."
    & $pythonExe -m playwright install chromium 2>&1 | Out-Null
    
    # 创建配置文件
    $configFile = Join-Path $installDir "config.json"
    $config = @{
        llm = @{
            provider = $Model
            model = $ModelName
        }
        gateway = @{}
        skills = @{}
    }
    
    if ($APIKey) {
        $config.llm.api_key = $APIKey
    }
    
    $config | ConvertTo-Json -Depth 10 | Out-File $configFile -Encoding UTF8
    
    # 创建启动脚本
    $startScript = Join-Path $installDir "start.ps1"
    @"
`$env:WOCLAW_LLM = '$Model'
`$env:WOCLAW_MODEL = '$ModelName'
$(Join-Path $venvDir 'Scripts\woclaw.exe') chat
"@ | Out-File $startScript -Encoding UTF8
    
    Write-Success "Woclaw 安装完成"
    
    return $venvDir
}

function New-DesktopShortcut {
    param([string]$VenvDir)
    
    Write-Step "创建桌面快捷方式..."
    
    $woclawExe = Join-Path $VenvDir "Scripts\woclaw.exe"
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktopPath "Woclaw.lnk"
    
    try {
        $WScriptShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WScriptShell.CreateShortcut($shortcutPath)
        $Shortcut.TargetPath = "powershell.exe"
        $Shortcut.Arguments = "-NoExit -Command `"`$env:WOCLAW_LLM='ollama'; $woclawExe chat`""
        $Shortcut.WorkingDirectory = $env:USERPROFILE
        $Shortcut.Description = "Woclaw - 启明星 AI 助手"
        $Shortcut.Save()
        
        Write-Success "桌面快捷方式已创建"
    } catch {
        Write-Info "快捷方式创建失败（不影响使用）"
    }
}

function Show-Success {
    param([string]$VenvDir)
    
    $woclawExe = Join-Path $VenvDir "Scripts\woclaw.exe"
    
    Clear-Host
    Write-Host ""
    Write-Host "  ╔═══════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "  ║                                                   ║" -ForegroundColor Green
    Write-Host "  ║         ✨ 安装完成！星灵已准备就绪！✨          ║" -ForegroundColor Green
    Write-Host "  ║                                                   ║" -ForegroundColor Green
    Write-Host "  ╚═══════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "  🚀 立即开始：" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "      双击桌面上的 " -NoNewline
    Write-Host "Woclaw" -ForegroundColor Yellow -NoNewline
    Write-Host " 图标"
    Write-Host ""
    Write-Host "      或在命令行运行：" -ForegroundColor Gray
    Write-Host "      $woclawExe chat" -ForegroundColor White
    Write-Host ""
    Write-Host "  ───────────────────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  💬 示例对话：" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "      你: 帮我整理下载文件夹" -ForegroundColor White
    Write-Host "      你: 打开记事本，输入 Hello World" -ForegroundColor White
    Write-Host "      你: 查看系统信息" -ForegroundColor White
    Write-Host ""
    Write-Host "  ───────────────────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  🌟 默认使用 Ollama 本地模型（完全免费）" -ForegroundColor Yellow
    Write-Host "  🌟 如需使用 GPT-4/Claude，请设置 API Key" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  ✨ 让启明星照亮你的电脑世界！🌟" -ForegroundColor Cyan
    Write-Host ""
}

function Uninstall-Woclaw {
    Write-Banner
    Write-Step "卸载 Woclaw..."
    
    $installDir = Join-Path $env:USERPROFILE ".woclaw"
    
    if (Test-Path $installDir) {
        Remove-Item $installDir -Recurse -Force
        Write-Success "已删除安装目录"
    }
    
    # 删除快捷方式
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktopPath "Woclaw.lnk"
    if (Test-Path $shortcutPath) {
        Remove-Item $shortcutPath -Force
        Write-Success "已删除快捷方式"
    }
    
    Write-Host ""
    Write-Host "  ✨ Woclaw 已完全卸载" -ForegroundColor Green
    Write-Host ""
}

# ==================== 主程序 ====================

if ($Uninstall) {
    Uninstall-Woclaw
    exit 0
}

Write-Banner

Write-Host "  正在准备安装，请稍候..." -ForegroundColor Gray
Write-Host ""

# 1. 安装 Python
$pythonCmd = Install-Python
if (-not $pythonCmd) {
    Write-Host ""
    Write-Host "  ❌ Python 安装失败，请手动安装 Python 3.10+" -ForegroundColor Red
    Write-Host "     下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "按回车键退出"
    exit 1
}

# 2. 安装 Ollama（如果是本地模型）
if ($Model -eq "ollama") {
    $ollamaOk = Install-Ollama
    if (-not $ollamaOk) {
        Write-Info "Ollama 安装失败，将使用云端模型"
        Write-Info "您可以稍后手动安装 Ollama: https://ollama.com"
    }
}

# 3. 安装 Woclaw
$venvDir = Install-Woclaw -PythonCmd $pythonCmd

# 4. 创建快捷方式
if (-not $NoGUI) {
    New-DesktopShortcut -VenvDir $venvDir
}

# 5. 显示成功
Show-Success -VenvDir $venvDir
