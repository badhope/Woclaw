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

Woclaw 是一个从 OpenClaw 蒸馏而来的轻量级自主电脑控制智能体。它能够完全自主地理解任务、规划步骤、调用工具、执行操作，并验证结果——无需人工干预。

**核心理念**：代码精简，功能完整。

```
用户: "帮我从某网站抓取产品数据，整理成 Excel，然后发邮件给团队"

Woclaw: 
  ✓ 理解任务 → 分解为 5 个子任务
  ✓ 打开浏览器 → 导航到目标网站
  ✓ 抓取数据 → 解析并清洗
  ✓ 生成 Excel → 保存到本地
  ✓ 发送邮件 → 完成报告
```

### ✨ 特性

| 特性 | 描述 |
|------|------|
| 🧠 **完全自主** | 无需人工干预，Agent 自主规划与执行 |
| 🪶 **轻量级** | 核心代码 < 3000 行，依赖 < 10 个 |
| 🔧 **丰富工具** | 文件系统、Shell、浏览器、网络请求 |
| 🌐 **混合浏览器** | 支持无头浏览器与真实浏览器控制 |
| 🤖 **多 LLM 支持** | OpenAI、Claude、Ollama 本地模型 |
| 💾 **持久存储** | PostgreSQL 存储任务历史与学习经验 |
| ⚡ **高并发** | 多进程架构，支持大规模任务处理 |
| 🛡️ **高级反爬** | Cloudflare 绕过、验证码处理 |

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
│  │                    Tool Layer                            │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │
│  │  │FileSystem│ │  Shell   │ │ Browser  │ │   Web    │    │   │
│  │  │ 文件系统  │ │ 命令执行 │ │ 浏览器   │ │ 网络请求 │    │   │
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
git clone https://github.com/badhope/Woclaw.git
cd woclaw

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
woclaw run "从 example.com 抓取所有产品信息"

# 从配置文件执行
woclaw run --config tasks.yaml
```

### ⚙️ 配置

Woclaw 使用 Python 配置文件，灵活且强大：

```python
# config.py
from woclaw import Config

config = Config(
    # LLM 配置
    llm={
        "provider": "openai",  # openai, claude, ollama
        "model": "gpt-4",
        "api_key": "your-api-key",
    },
    
    # 数据库配置
    database={
        "host": "localhost",
        "port": 5432,
        "database": "woclaw",
        "user": "postgres",
        "password": "password",
    },
    
    # 浏览器配置
    browser={
        "headless": True,
        "proxy": None,
    },
    
    # 并发配置
    concurrency={
        "max_workers": 4,
        "task_timeout": 300,
    },
)
```

### 🛠️ 工具列表

| 工具 | 功能 | 示例 |
|------|------|------|
| `filesystem` | 文件读写、搜索、组织 | 读取文件、创建目录、搜索内容 |
| `shell` | 执行系统命令 | 运行脚本、安装软件 |
| `browser` | 浏览器控制 | 打开网页、点击、输入、截图 |
| `web` | HTTP 请求 | API 调用、网页抓取 |
| `data` | 数据处理 | JSON/CSV/Excel 处理 |

### 📊 性能

| 指标 | 数值 |
|------|------|
| 核心代码 | < 3000 行 |
| 依赖数量 | < 10 个 |
| 启动时间 | < 1 秒 |
| 并发能力 | > 10000 页/天 |

### 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## English

### Introduction

Woclaw is a lightweight autonomous computer control agent distilled from OpenClaw. It can fully autonomously understand tasks, plan steps, call tools, execute operations, and verify results—all without human intervention.

**Core Philosophy**: Minimal code, complete functionality.

### ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Fully Autonomous** | No human intervention needed, Agent plans and executes independently |
| 🪶 **Lightweight** | Core code < 3000 lines, dependencies < 10 |
| 🔧 **Rich Tools** | File system, Shell, Browser, Network requests |
| 🌐 **Hybrid Browser** | Headless and real browser control support |
| 🤖 **Multi-LLM Support** | OpenAI, Claude, Ollama local models |
| 💾 **Persistent Storage** | PostgreSQL for task history and learning |
| ⚡ **High Concurrency** | Multi-process architecture for large-scale tasks |
| 🛡️ **Advanced Anti-Bot** | Cloudflare bypass, CAPTCHA handling |

### 📦 Installation

```bash
# Clone repository
git clone https://github.com/badhope/Woclaw.git
cd woclaw

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
woclaw run "Scrape all product info from example.com"

# Execute from config file
woclaw run --config tasks.yaml
```

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by Woclaw Team**

</div>
