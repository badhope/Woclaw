<div align="center">

# 🦀 Woclaw

**轻量级自主电脑控制智能体**

*Lightweight Autonomous Computer Control Agent*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[English](#english) | [中文](#中文)

</div>

---

## 中文

### 简介

Woclaw 是一个完全自主的电脑控制智能体。它能够理解用户指令，自主规划并执行各种电脑操作——文件管理、程序运行、浏览器控制、系统监控等，无需人工干预。

**核心理念**：让 AI 像人类一样操作电脑。

```
用户: "帮我整理下载文件夹，把图片移到 Pictures，文档移到 Documents"

Woclaw: 
  ✓ 扫描下载文件夹 → 发现 50 个文件
  ✓ 分类文件 → 识别图片、文档、压缩包
  ✓ 创建目录 → Pictures/Downloads, Documents/Downloads
  ✓ 移动文件 → 完成 50 个文件整理
```

### ✨ 特性

| 特性 | 描述 |
|------|------|
| 🧠 **完全自主** | 理解任务、规划步骤、执行操作、验证结果 |
| 🪶 **轻量级** | 核心代码精简，依赖少，启动快 |
| 🔧 **丰富工具** | 13+ 工具覆盖电脑操作各个方面 |
| 🖱️ **桌面自动化** | 键盘鼠标模拟，可操作任何应用 |
| 📸 **屏幕截图** | 全屏、区域、窗口截图 |
| 📊 **系统监控** | CPU、内存、磁盘、网络实时监控 |
| 🔄 **进程管理** | 启动、停止、监控进程 |
| 📋 **剪贴板** | 读写剪贴板内容 |
| 🌐 **网络工具** | 下载、端口扫描、DNS 查询 |
| 🤖 **多 LLM 支持** | OpenAI、Claude、Ollama 本地模型 |

### 📦 安装

```bash
# 克隆仓库
git clone https://github.com/badhope/Xiaobai.git
cd Xiaobai

# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .

# 安装浏览器驱动 (用于 browser 工具)
playwright install

# 安装 LLM 提供者 (选择一个或多个)
pip install openai        # OpenAI
pip install anthropic     # Claude
# Ollama 无需额外安装，只需本地运行 Ollama 服务
```

### ⚙️ 配置

```bash
# 复制配置模板
cp config.example.py config.py

# 编辑配置文件，填入你的 API Key
# Windows
notepad config.py
# Mac/Linux
nano config.py
```

配置示例：

```python
from woclaw import Config

# OpenAI
config = Config(
    llm={
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "sk-your-api-key",
    }
)

# 或 Claude
config = Config(
    llm={
        "provider": "claude",
        "model": "claude-3-opus-20240229",
        "api_key": "sk-ant-your-api-key",
    }
)

# 或 Ollama 本地模型 (免费)
config = Config(
    llm={
        "provider": "ollama",
        "model": "llama2",
        "base_url": "http://localhost:11434",
    }
)
```

### 🚀 快速开始

```bash
# 方式1: 交互模式 (推荐)
woclaw

# 方式2: 执行单个任务
woclaw run "帮我整理下载文件夹"

# 方式3: 使用配置文件
woclaw run --config config.py

# 查看可用工具
woclaw tools

# 查看当前配置
woclaw config
```

### 🛠️ 工具列表

| 工具 | 功能 | 操作 |
|------|------|------|
| `filesystem` | 文件系统操作 | read, write, copy, move, delete, list, search |
| `shell` | 执行系统命令 | run |
| `browser` | 浏览器控制 | navigate, click, type, screenshot, content |
| `web` | HTTP 请求 | get, post, download |
| `data` | 数据处理 | read_json, write_json, read_csv, write_csv |
| `process` | 进程管理 | list, find, start, kill |
| `clipboard` | 剪贴板操作 | read, write, clear |
| `system` | 系统监控 | info, cpu, memory, disk, network, battery |
| `network` | 网络工具 | download, dns, port_scan, ping |
| `screenshot` | 截图 | full, region, window |
| `automation` | 键盘鼠标 | key_press, key_hotkey, mouse_click, mouse_move |
| `archive` | 压缩解压 | compress, extract |
| `image` | 图像处理 | resize, convert, crop, filter |

### 📊 使用示例

```bash
# 文件整理
woclaw run "把下载文件夹里的图片按日期整理到 Pictures"

# 批量处理
woclaw run "把所有 PDF 转成图片，然后压缩成 ZIP"

# 系统监控
woclaw run "查看当前系统 CPU 和内存使用情况"

# 网络操作
woclaw run "下载 https://example.com/file.zip 到下载文件夹"

# 自动化操作
woclaw run "打开记事本，输入今天的日期，保存到桌面"

# 浏览器操作
woclaw run "打开百度搜索 Python 教程，截图保存"
```

### 🏗️ 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         Woclaw Agent                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Agent Core                            │   │
│  │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐  │   │
│  │  │ 理解    │ → │ 规划    │ → │ 执行    │ → │ 验证    │  │   │
│  │  └─────────┘   └─────────┘   └─────────┘   └─────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Tool Layer (13+ 工具)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    LLM Interface                         │   │
│  │         OpenAI  |  Claude  |  Ollama  |  ...            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## English

### Introduction

Woclaw is a fully autonomous computer control agent. It can understand user commands, autonomously plan and execute various computer operations—file management, program execution, browser control, system monitoring, etc.—without human intervention.

**Core Philosophy**: Let AI operate computers like humans.

### 📦 Installation

```bash
# Clone repository
git clone https://github.com/badhope/Xiaobai.git
cd Xiaobai

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .

# Install browser drivers
playwright install

# Install LLM provider
pip install openai  # or anthropic
```

### ⚙️ Configuration

```bash
cp config.example.py config.py
# Edit config.py and add your API key
```

### 🚀 Quick Start

```bash
# Interactive mode
woclaw

# Execute single task
woclaw run "Organize my downloads folder"

# Use config file
woclaw run --config config.py
```

### 🛠️ Tools

| Tool | Function | Operations |
|------|----------|------------|
| `filesystem` | File operations | read, write, copy, move, delete, list, search |
| `shell` | Execute commands | run |
| `browser` | Browser control | navigate, click, type, screenshot, content |
| `web` | HTTP requests | get, post, download |
| `data` | Data processing | read_json, write_json, read_csv, write_csv |
| `process` | Process management | list, find, start, kill |
| `clipboard` | Clipboard operations | read, write, clear |
| `system` | System monitoring | info, cpu, memory, disk, network |
| `network` | Network tools | download, dns, port_scan, ping |
| `screenshot` | Screenshot | full, region, window |
| `automation` | Keyboard/mouse | key_press, key_hotkey, mouse_click, mouse_move |
| `archive` | Archive operations | compress, extract |
| `image` | Image processing | resize, convert, crop, filter |

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by Woclaw Team**

</div>
