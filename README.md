# Woclaw - 启明星 AI 助手 🌟

> **让 AI 像启明星一样，在黑暗中为你指引方向**

[English](docs/en.md) | [中文](docs/index.md) | [日本語](docs/ja.md)

---

[![GitHub Stars](https://img.shields.io/github/stars/badhope/Woclaw?style=for-the-badge&color=FFD700)](https://github.com/badhope/Woclaw/stargazers)
[![Version](https://img.shields.io/badge/version-0.2.0--alpha-blue?style=for-the-badge)](https://github.com/badhope/Woclaw/releases)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-yellow?style=for-the-badge)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Windows-Support-brightgreen?style=for-the-badge&logo=windows)](https://github.com/badhope/Woclaw)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=for-the-badge&logo=github-actions)](https://github.com/badhope/Woclaw/actions)

[![Stars](https://img.shields.io/badge/Stars-Welcome-FFD700?style=for-the-badge&logo=github)](https://github.com/badhope/Woclaw/stargazers)
[![Issues](https://img.shields.io/badge/Issues-Welcome-red?style=for-the-badge&logo=github)](https://github.com/badhope/Woclaw/issues)
[![PR](https://img.shields.io/badge/PR-Welcome-blue?style=for-the-badge&logo=github)](https://github.com/badhope/Woclaw/pulls)

---

## ✨ 什么是 Woclaw？

**Woclaw**（谐音"启明星"）是一个**轻量级自主电脑控制 AI 助手**。它能理解你的自然语言指令，帮你操控电脑完成各种任务——从简单的文件管理到复杂的 GUI 自动化操作。

**核心理念**：让 AI 像人类一样操作电脑，而不是让你变成程序员。

### 🌟 品牌故事

> Woclaw 的名字来源于"启明星"——北极星，指引方向的星光。
> 无论你在电脑操作的黑暗中迷失，Woclaw 都会像那颗最亮的星，为你指引方向。

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 🧠 **智能决策者** | Supervisor Agent 理解你的意图，制定执行计划 |
| 🔧 **全能操控** | 文件、进程、GUI 窗口、网络请求，全部拿下 |
| 📚 **自我进化** | 从错误中学习，越用越聪明 |
| 🔒 **安全可控** | 风险分级，高风险操作需要确认 |
| 🛠️ **工具丰富** | 开箱即用的 5 大 Worker |
| 💬 **多平台支持** | CLI、微信、钉钉、飞书... |
| 🌐 **国际化** | 支持中文、English、日语 |

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Windows 10/11（主要支持平台）
- 2GB+ RAM
- 500MB 可用磁盘空间

### 一键安装（Windows 推荐）

```powershell
# PowerShell 管理员模式运行
iwr https://raw.githubusercontent.com/badhope/Woclaw/main/scripts/install.ps1 -UseBasicParsing | iex
```

### 手动安装

```bash
# 克隆项目
git clone https://github.com/badhope/Woclaw.git
cd Woclaw

# 安装依赖
pip install -e .

# 启动交互模式
woclaw chat
```

### Docker 安装（可选）

```bash
# 构建镜像
docker build -t woclaw .

# 运行容器
docker run -it woclaw chat
```

## 📖 使用指南

### 基本命令

```bash
# 交互式聊天
woclaw chat

# 执行单个任务
woclaw run "帮我整理下载文件夹"

# 查看状态
woclaw status

# 查看可用工具
woclaw tools

# 初始化配置
woclaw init
```

### 配置模型

```bash
# 使用 Ollama（本地免费，推荐）
export WOCLAW_LLM=ollama
export WOCLAW_MODEL=llama3.2
woclaw chat

# 使用 OpenAI
export WOCLAW_LLM=openai
export OPENAI_API_KEY=sk-your-key
woclaw chat

# 使用 Claude
export WOCLAW_LLM=claude
export ANTHROPIC_API_KEY=sk-ant-your-key
woclaw chat
```

### 支持的模型提供商

| 提供商 | 模型示例 | 需要 API Key |
|--------|----------|--------------|
| Ollama | llama3.2, qwen2.5, codellama | ❌ 否（本地免费）|
| OpenAI | gpt-4o, gpt-4, gpt-3.5 | ✅ 是 |
| Claude | claude-3-5-sonnet, claude-3-opus | ✅ 是 |
| DeepSeek | deepseek-chat, deepseek-coder | ✅ 是 |
| Kimi | moonshot-v1-8k, moonshot-v1-32k | ✅ 是 |
| 通义千问 | qwen-plus, qwen-max | ✅ 是 |

## 🏗️ 系统架构

```
用户消息
    ↓
┌─────────────────────────────────────────┐
│           Supervisor（决策者）                │
│                                          │
│  • 理解意图  • 拆解任务  • 审批计划        │
│  • 验证结果  • 整合输出  • 自我学习        │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│            Workers（工作者）               │
│                                          │
│  • FileWorker   - 文件操作（读/写/整理）  │
│  • GuiWorker    - GUI 操控（窗口/点击）  │
│  • ShellWorker  - 命令执行（脚本/终端）  │
│  • WebWorker    - 网络请求（HTTP/API）    │
│  • SysWorker    - 系统信息（进程/监控）   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│          Learning（学习系统）               │
│                                          │
│  • LEARNINGS.md  - 成功经验记录          │
│  • ERRORS.md     - 错误教训记录          │
│  • FEEDBACK.md   - 用户偏好记录          │
└─────────────────────────────────────────┘
```

## 🎨 使用示例

### 文件管理

```
你：把下载文件夹里的图片按日期整理
星灵：好的！我来帮你整理图片~

✅ 扫描下载文件夹（找到 32 张图片）
✅ 创建分类文件夹（2026-03、2026-02...）
✅ 移动文件到对应文件夹
✨ 完成！已整理 32 张图片
```

### GUI 操控

```
你：帮我打开记事本，输入"你好启明星"然后保存
星灵：收到！马上操作~

✅ 打开记事本
✅ 激活窗口
✅ 输入文本
✅ 点击文件菜单
✅ 点击另存为
✅ 保存文件
✨ 完成！文件已保存
```

### 系统监控

```
你：帮我看看电脑状态，有没有占用内存太多的程序
星灵：好的！让我检查一下~

✅ CPU: 23% 使用率
✅ 内存: 16.2 GB / 32 GB (50.6%)
✅ 磁盘: 256 GB / 512 GB (50%)
✅ 最高内存占用:
   1. chrome.exe - 2.1 GB
   2. code.exe - 1.8 GB
   3. woclaw.exe - 450 MB
✨ 没有发现异常情况！
```

## 🔧 配置文件

配置文件位于 `~/.woclaw/config.yaml`：

```yaml
# Woclaw 配置文件示例

# LLM 配置
llm:
  provider: ollama  # ollama, openai, claude, deepseek, kimi, qwen
  model: llama3.2   # 具体模型名
  api_key: ""       # API Key（云端模型需要）
  base_url: http://localhost:11434  # Ollama 地址

# Worker 配置
workers:
  shell:
    timeout: 300
  gui:
    backend: win32
  web:
    timeout: 30

# 安全配置
security:
  allow_dangerous: false
  confirm_on_delete: true
  log_commands: true

# 学习配置
learning:
  enabled: true
  auto_save: true
  data_dir: ~/.woclaw/.learnings
```

## 📁 项目结构

```
woclaw/
├── src/
│   └── woclaw/
│       ├── supervisor/          # 决策层
│       │   ├── agent.py        # Supervisor 主逻辑
│       │   ├── planner.py      # 任务规划
│       │   └── executor.py      # 执行调度
│       ├── workers/            # 执行层
│       │   ├── base.py         # Worker 基类
│       │   ├── file_worker.py  # 文件操作
│       │   ├── gui_worker.py   # GUI 操控
│       │   ├── shell_worker.py # 命令执行
│       │   ├── web_worker.py   # 网络请求
│       │   └── sys_worker.py   # 系统信息
│       ├── learning/            # 学习层
│       │   └── memory.py       # 学习记忆
│       ├── llm/                 # 模型层
│       │   └── registry.py     # 模型注册表
│       └── cli.py              # 命令行入口
├── scripts/
│   └── install.ps1            # Windows 一键安装
├── tests/                       # 测试
├── docs/                        # 文档（中/英/日）
├── .github/
│   └── workflows/             # CI/CD 配置
└── pyproject.toml              # 项目配置
```

## 🤝 贡献指南

欢迎贡献代码！

### 开发环境设置

```bash
# 克隆并进入目录
git clone https://github.com/badhope/Woclaw.git
cd Woclaw

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/

# 代码格式检查
ruff check src/
black src/
```

### 提交规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具
```

## 🐛 问题反馈

发现 Bug？请 [提交 Issue](https://github.com/badhope/Woclaw/issues)！

## 📄 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。

---

## 🙏 致谢

- [pywinauto](https://github.com/pywinauto/pywinauto) - Windows GUI 自动化
- [LangChain](https://github.com/langchain-ai/langchain) - LLM 框架参考
- [OpenClaw](https://github.com/openclaw/openclaw) - 项目灵感来源

---

<div align="center">

**⭐ 如果 Woclaw 对你有帮助，请给我们一个 Star！**

*让启明星照亮更多人的电脑*

**Made with ✨ by Woclaw Team**

</div>
