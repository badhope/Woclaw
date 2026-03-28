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
| 💾 **持久存储** | PostgreSQL 存储任务历史 |

### 🏗️ 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         Woclaw Agent                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Agent Core                            │   │
│  │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐  │   │
│  │  │ 理解    │ → │ 规划    │ → │ 执行    │ → │ 验证    │  │   │
│  │  │Understand│   │ Plan    │   │ Execute │   │ Verify  │  │   │
│  │  └─────────┘   └─────────┘   └─────────┘   └─────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Tool Layer (13+ 工具)                 │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │
│  │  │FileSystem│ │  Shell   │ │ Browser  │ │   Web    │    │   │
│  │  │ 文件系统  │ │ 命令执行 │ │ 浏览器   │ │ 网络请求 │    │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │
│  │  │ Process  │ │Clipboard │ │ System   │ │ Network  │    │   │
│  │  │ 进程管理  │ │ 剪贴板   │ │ 系统监控 │ │ 网络工具 │    │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │
│  │  │Screenshot│ │Automation│ │ Archive  │ │  Image   │    │   │
│  │  │ 截图     │ │ 键盘鼠标 │ │ 压缩解压 │ │ 图像处理 │    │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    LLM Interface                         │   │
│  │  ┌─────────┐   ┌─────────┐   ┌─────────┐                │   │
│  │  │ OpenAI  │   │ Claude  │   │  Ollama │   ...          │   │
│  │  └─────────┘   └─────────┘   └─────────┘                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Storage Layer                         │   │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │   │
│  │  │ PostgreSQL  │   │   Cache     │   │ File Index  │    │   │
│  │  │ 任务历史    │   │   缓存      │   │ 文件索引    │    │   │
│  │  └─────────────┘   └─────────────┘   └─────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📦 安装

```bash
# 克隆仓库
git clone https://github.com/badhope/Xiaobai.git
cd Xiaobai

# 安装依赖
pip install -e .

# 安装浏览器驱动
playwright install
```

### 🚀 快速开始

```bash
# 启动交互模式
woclaw

# 执行单个任务
woclaw run "帮我整理下载文件夹"

# 从配置文件执行
woclaw run --config config.py
```

### ⚙️ 配置

```python
# config.py
from woclaw import Config

config = Config(
    llm={
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "your-api-key",
    },
    database={
        "host": "localhost",
        "port": 5432,
        "database": "woclaw",
        "user": "postgres",
        "password": "password",
    },
    concurrency={
        "max_workers": 4,
        "task_timeout": 300,
    },
)
```

### 🛠️ 工具列表

| 工具 | 功能 | 操作 |
|------|------|------|
| `filesystem` | 文件系统操作 | 读写、搜索、复制、移动、删除 |
| `shell` | 执行系统命令 | 运行程序、脚本执行 |
| `browser` | 浏览器控制 | 打开网页、点击、输入、截图 |
| `web` | HTTP 请求 | API 调用、网页抓取 |
| `data` | 数据处理 | JSON/CSV 读写、过滤、转换 |
| `process` | 进程管理 | 列出、查找、启动、终止进程 |
| `clipboard` | 剪贴板操作 | 读取、写入、清空 |
| `system` | 系统监控 | CPU、内存、磁盘、网络信息 |
| `network` | 网络工具 | 下载、端口扫描、DNS 查询 |
| `screenshot` | 截图 | 全屏、区域、窗口截图 |
| `automation` | 键盘鼠标 | 模拟按键、鼠标点击、移动 |
| `archive` | 压缩解压 | ZIP/TAR 创建和解压 |
| `image` | 图像处理 | 调整大小、格式转换、裁剪、滤镜 |

### 📊 使用示例

```python
# 示例：自动整理文件
woclaw run "把下载文件夹里的图片按日期整理到 Pictures"

# 示例：批量处理
woclaw run "把所有 PDF 转成图片，然后压缩成 ZIP"

# 示例：系统监控
woclaw run "监控 CPU 使用率，超过 80% 时发通知"

# 示例：自动化操作
woclaw run "打开记事本，输入今天的日期，保存到桌面"
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

### ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Fully Autonomous** | Understand, plan, execute, and verify without human intervention |
| 🪶 **Lightweight** | Minimal code, few dependencies, fast startup |
| 🔧 **Rich Tools** | 13+ tools covering all aspects of computer control |
| 🖱️ **Desktop Automation** | Keyboard/mouse simulation, operate any application |
| 📸 **Screenshot** | Full screen, region, window capture |
| 📊 **System Monitoring** | Real-time CPU, memory, disk, network monitoring |
| 🔄 **Process Management** | Start, stop, monitor processes |
| 📋 **Clipboard** | Read/write clipboard content |
| 🌐 **Network Tools** | Download, port scan, DNS lookup |
| 🤖 **Multi-LLM Support** | OpenAI, Claude, Ollama local models |
| 💾 **Persistent Storage** | PostgreSQL for task history |

### 📦 Installation

```bash
# Clone repository
git clone https://github.com/badhope/Xiaobai.git
cd Xiaobai

# Install dependencies
pip install -e .

# Install browser drivers
playwright install
```

### 🚀 Quick Start

```bash
# Start interactive mode
woclaw

# Execute single task
woclaw run "Organize my downloads folder"

# Execute from config file
woclaw run --config config.py
```

### 🛠️ Tools

| Tool | Function | Operations |
|------|----------|------------|
| `filesystem` | File system operations | Read, write, search, copy, move, delete |
| `shell` | Execute system commands | Run programs, execute scripts |
| `browser` | Browser control | Open pages, click, input, screenshot |
| `web` | HTTP requests | API calls, web scraping |
| `data` | Data processing | JSON/CSV read/write, filter, transform |
| `process` | Process management | List, find, start, kill processes |
| `clipboard` | Clipboard operations | Read, write, clear |
| `system` | System monitoring | CPU, memory, disk, network info |
| `network` | Network tools | Download, port scan, DNS lookup |
| `screenshot` | Screenshot | Full screen, region, window capture |
| `automation` | Keyboard/mouse | Simulate keys, mouse clicks, movement |
| `archive` | Archive operations | ZIP/TAR create and extract |
| `image` | Image processing | Resize, convert, crop, filter |

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by Woclaw Team**

</div>
