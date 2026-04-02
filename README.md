<!-- Powered by AI Agent -->
<!-- Sponsored by OpenClaw -->

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=50&duration=4000&pause=1000&color=FFD700&background=0F0F23&center=true&vCenter=true&multiline=true&width=900&height=100&lines=Woclaw%20~%20Your%20AI%20Desktop%20Assistant" alt="Woclaw - AI Desktop Assistant">
</p>

<p align="center">
  <a href="https://github.com/badhope/Woclaw">
    <img src="https://img.shields.io/badge/Version-v0.3.0--alpha-FFD700?style=for-the-badge" alt="Version">
  </a>
  <a href="https://github.com/badhope/Woclaw/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge" alt="Python">
  </a>
  <a href="https://github.com/badhope/Woclaw/actions">
    <img src="https://img.shields.io/badge/Build-Passing-brightgreen?style=for-the-badge&logo=github-actions" alt="Build">
  </a>
</p>

<p align="center">
  <a href="https://github.com/badhope/Woclaw/stargazers">
    <img src="https://img.shields.io/github/stars/badhope/Woclaw?style=for-the-badge&color=FFD700" alt="Stars">
  </a>
  <a href="https://github.com/badhope/Woclaw/network/members">
    <img src="https://img.shields.io/github/forks/badhope/Woclaw?style=for-the-badge&color=orange" alt="Forks">
  </a>
  <a href="https://github.com/badhope/Woclaw/issues">
    <img src="https://img.shields.io/badge/Issues-Welcome-red?style=for-the-badge" alt="Issues">
  </a>
  <a href="https://github.com/badhope/Woclaw/pulls">
    <img src="https://img.shields.io/badge/PR-Welcome-blue?style=for-the-badge" alt="PR">
  </a>
</p>

<div align="center">

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ██╗   ██╗██╗   ██╗███╗   ███╗ ██████╗ ███╗   ██╗ █████╗ ██████╗     ║
║     ██║   ██║██║   ██║████╗ ████║██╔═══██╗████╗  ██║██╔══██╗██╔══██╗    ║
║     ██║   ██║██║   ██║██╔████╔██║██║   ██║██╔██╗ ██║███████║██████╔╝    ║
║     ╚██╗ ██╔╝██║   ██║██║╚██╔╝██║██║   ██║██║╚██╗██║██╔══██║██╔══██╗    ║
║      ╚████╔╝ ╚██████╔╝██║ ╚═╝ ██║╚██████╔╝██║ ╚████║██║  ██║██║  ██║    ║
║       ╚═══╝   ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝    ║
║                                                                              ║
║                    🌟  AI Desktop Assistant  🌟                               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

</div>

---

## 🎯 What is Woclaw?

**Woclaw** (pronounced "Wok-law") is a lightweight, intelligent **AI desktop assistant** that helps you control your computer through natural language.

> *"Like a guiding star in the dark, Woclaw illuminates your path through computer operations."*

### Core Philosophy

Unlike traditional automation tools that require you to become a programmer, Woclaw understands **natural language** and acts as a human would—managing files, controlling applications, automating workflows, and learning from experience.

---

## ✨ Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| 🧠 **Intelligent Supervisor** | Understands your intent, plans execution | ✅ |
| 🔧 **Universal Control** | Files, processes, GUI, web requests—all handled | ✅ |
| 📚 **Self-Learning** | Learns from mistakes, gets smarter over time | ✅ |
| 🔒 **Safety First** | Risk-tiered system, confirmations for dangerous ops | ✅ |
| 🛠️ **5 Built-in Workers** | File, GUI, Shell, Web, System operations | ✅ |
| 💬 **Multi-Platform** | CLI, WeChat, DingTalk, Feishu... | 🚧 |
| 🌐 **Internationalization** | Chinese, English, Japanese | ✅ |

---

## 🚀 Quick Start

### 🪟 Windows (Recommended)

Open **PowerShell** and run:

```powershell
irm https://raw.githubusercontent.com/badhope/Woclaw/main/scripts/install.ps1 | iex
```

**That's it!** The script automatically:
- ✅ Installs Python (if needed)
- ✅ Installs Ollama local model (if needed)
- ✅ Installs Woclaw and all dependencies
- ✅ Creates desktop shortcut
- ✅ Ready to use out of the box

**In 2-5 minutes, double-click the Woclaw icon to start!**

### Other Installation Methods

<details>
<summary>📦 Manual Installation (For Developers)</summary>

```bash
git clone https://github.com/badhope/Woclaw.git
cd Woclaw
pip install -e .
woclaw chat
```

</details>

<details>
<summary>🐳 Docker Installation</summary>

```bash
docker build -t woclaw .
docker run -it woclaw chat
```

</details>

---

## 📋 Requirements

| Component | Requirement |
|-----------|-------------|
| OS | Windows 10/11 (Primary) |
| Python | 3.10+ (Auto-installed) |
| RAM | 4GB+ |
| Storage | 1GB free |
| Model | Ollama (Auto-installed) or API Key |

---

## 💻 Usage

### Basic Commands

```bash
# Interactive chat
woclaw chat

# Execute single task
woclaw run "Organize my downloads folder"

# Check status
woclaw status

# List available tools
woclaw tools

# Initialize configuration
woclaw init
```

### Configure Model

```bash
# Use Ollama (Local, Free, Recommended)
export WOCLAW_LLM=ollama
export WOCLAW_MODEL=llama3.2
woclaw chat

# Use OpenAI
export WOCLAW_LLM=openai
export OPENAI_API_KEY=sk-your-key
woclaw chat

# Use Claude
export WOCLAW_LLM=claude
export ANTHROPIC_API_KEY=sk-ant-your-key
woclaw chat
```

### Supported Providers

| Provider | Example Models | API Key Required |
|----------|---------------|-----------------|
| Ollama | llama3.2, qwen2.5, codellama | ❌ No (Free Local) |
| OpenAI | gpt-4o, gpt-4, gpt-3.5 | ✅ Yes |
| Claude | claude-3-5-sonnet, claude-3-opus | ✅ Yes |
| DeepSeek | deepseek-chat, deepseek-coder | ✅ Yes |
| Kimi | moonshot-v1-8k, moonshot-v1-32k | ✅ Yes |
| Qwen | qwen-plus, qwen-max | ✅ Yes |

---

## 🏗️ Architecture

```
User Message
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Supervisor (Decision Layer)                              │
│                                                                              │
│  • Understand Intent   • Break Down Tasks   • Approve Plan                  │
│  • Verify Results      • Synthesize Output   • Self-Learn                  │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Workers (Execution Layer)                             │
│                                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   File       │  │   GUI        │  │   Shell     │  │   Web       │     │
│  │   Worker     │  │   Worker     │  │   Worker    │  │   Worker    │     │
│  │              │  │              │  │             │  │             │     │
│  │ • Read/Write │  │ • Click     │  │ • Scripts   │  │ • HTTP     │     │
│  │ • Organize   │  │ • Type      │  │ • Terminal  │  │ • APIs     │     │
│  │ • Search     │  │ • Windows   │  │ • Commands  │  │ • Scraping │     │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                                              │
│  ┌─────────────┐                                                            │
│  │   System    │                                                            │
│  │   Worker   │                                                            │
│  │            │                                                            │
│  │ • Process  │                                                            │
│  │ • Monitor  │                                                            │
│  │ • Info     │                                                            │
│  └─────────────┘                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Learning System                                       │
│                                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                       │
│  │  LEARNINGS  │  │    ERRORS   │  │   FEEDBACK  │                       │
│  │    .md      │  │     .md      │  │     .md     │                       │
│  │             │  │             │  │             │                       │
│  │ • Success   │  │ • Mistakes   │  │ • Preferences│                       │
│  │   Patterns  │  │   Lessons   │  │ • History   │                       │
│  └─────────────┘  └─────────────┘  └─────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Usage Examples

### 📁 File Management

```
You: Organize images in Downloads folder by date
Woclaw: Sure! Let me organize those images for you~

✅ Scanned Downloads folder (found 32 images)
✅ Created date folders (2026-03, 2026-02...)
✅ Moved files to corresponding folders
✨ Done! Organized 32 images
```

### 🖥️ GUI Automation

```
You: Open Notepad, type "Hello Woclaw", and save
Woclaw: On it! Just a moment~

✅ Launched Notepad
✅ Activated window
✅ Typed text
✅ Clicked File menu
✅ Clicked Save As
✅ Saved file
✨ Done! File saved successfully
```

### 📊 System Monitoring

```
You: Check my PC status, any memory-hogging programs?
Woclaw: Let me take a look~

✅ CPU: 23% usage
✅ Memory: 16.2 GB / 32 GB (50.6%)
✅ Disk: 256 GB / 512 GB (50%)
✅ Top Memory Usage:
   1. chrome.exe - 2.1 GB
   2. code.exe - 1.8 GB
   3. woclaw.exe - 450 MB
✨ No anomalies detected!
```

---

## 🔧 Configuration

Config file: `~/.woclaw/config.yaml`

```yaml
# Woclaw Configuration

# LLM Settings
llm:
  provider: ollama        # ollama, openai, claude, deepseek, kimi, qwen
  model: llama3.2        # Model name
  api_key: ""            # API Key (cloud models only)
  base_url: http://localhost:11434  # Ollama address

# Worker Settings
workers:
  shell:
    timeout: 300
  gui:
    backend: win32
  web:
    timeout: 30

# Security
security:
  allow_dangerous: false
  confirm_on_delete: true
  log_commands: true

# Learning
learning:
  enabled: true
  auto_save: true
  data_dir: ~/.woclaw/.learnings
```

---

## 📂 Project Structure

```
woclaw/
├── src/
│   └── woclaw/
│       ├── supervisor/          # Decision layer
│       │   ├── agent.py       # Supervisor main
│       │   ├── planner.py     # Task planning
│       │   └── executor.py     # Execution
│       ├── workers/            # Execution layer
│       │   ├── base.py         # Worker base class
│       │   ├── file_worker.py  # File operations
│       │   ├── gui_worker.py   # GUI control
│       │   ├── shell_worker.py # Command execution
│       │   ├── web_worker.py   # Network requests
│       │   └── sys_worker.py  # System info
│       ├── learning/           # Learning layer
│       │   └── memory.py      # Memory & learning
│       ├── llm/                # Model layer
│       │   └── registry.py     # Model registry
│       └── cli.py              # CLI entry
├── scripts/
│   └── install.ps1             # Windows installer
├── tests/                      # Tests
├── docs/                       # Docs (CN/EN/JP)
├── .github/
│   └── workflows/             # CI/CD
├── ARCHITECTURE.md             # Architecture docs
├── CHANGELOG.md               # Changelog
├── CONTRIBUTING.md            # Contributing guide
├── LICENSE                    # MIT License
├── pyproject.toml             # Project config
└── README.md                  # This file
```

---

## 🤝 Contributing

We welcome contributions!

### Development Setup

```bash
# Clone repository
git clone https://github.com/badhope/Woclaw.git
cd Woclaw

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Code style
ruff check src/
black src/
```

### Commit Convention

```
feat: New feature
fix: Bug fix
docs: Documentation
style: Code formatting
refactor: Refactoring
test: Tests
chore: Build/tools
```

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE).

---

## 🙏 Acknowledgments

- [pywinauto](https://github.com/pywinauto/pywinauto) - Windows GUI automation
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework reference
- [OpenClaw](https://github.com/openclaw/openclaw) - Project inspiration

---

## 📞 Support

| Channel | Link |
|---------|------|
| 🐛 **Bug Reports** | [GitHub Issues](https://github.com/badhope/Woclaw/issues) |
| 💬 **Discussions** | [GitHub Discussions](https://github.com/badhope/Woclaw/discussions) |
| 📖 **Wiki** | [GitHub Wiki](https://github.com/badhope/Woclaw/wiki) |

---

<p align="center">
  <strong>⭐ If Woclaw helps you, please give it a star! ⭐</strong>
</p>

<p align="center">
  <em>"Let the guiding star illuminate more people's computers"</em>
</p>

<p align="center">
  Made with ✨ by <a href="https://github.com/badhope">Woclaw Team</a>
</p>

---

<p align="center">
  <a href="https://github.com/badhope/Woclaw">Home</a> •
  <a href="https://github.com/badhope/Woclaw/releases">Releases</a> •
  <a href="https://github.com/badhope/Woclaw/issues">Issues</a> •
  <a href="https://github.com/badhope/Woclaw/discussions">Discussions</a>
</p>

---

<!-- MARKDOWN BADGES -->

[version-shield]: https://img.shields.io/badge/Version-v0.3.0--alpha-FFD700?style=for-the-badge
[license-shield]: https://img.shields.io/badge/License-MIT-green?style=for-the-badge
[python-shield]: https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge
[build-shield]: https://img.shields.io/badge/Build-Passing-brightgreen?style=for-the-badge
[stars-shield]: https://img.shields.io/github/stars/badhope/Woclaw?style=for-the-badge&color=FFD700
[forks-shield]: https://img.shields.io/github/forks/badhope/Woclaw?style=for-the-badge&color=orange
