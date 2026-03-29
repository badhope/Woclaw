# Woclaw - Morning Star AI Assistant 🌟

> **Let AI guide you through the darkness, like a morning star**

[English](en.md) | [中文](index.md) | [日本語](ja.md)

---

## ✨ What is Woclaw?

Woclaw (pronounces like "Morning Star") is a **lightweight autonomous computer control AI assistant**. It understands your natural language instructions and helps you control your computer to complete various tasks.

**Core Philosophy**: Let AI operate computers like humans, instead of making you become a programmer.

## 🌟 Key Features

- 🧠 **Smart Supervisor** - Understands your intent, creates execution plans
- 🔧 **Full Control** - Files, processes, GUI windows, network requests - all covered
- 📚 **Self-Learning** - Learn from mistakes, get smarter over time
- 🔒 **Secure & Controllable** - Risk levels, dangerous operations require confirmation
- 🛠️ **Rich Tools** - 5 built-in Workers ready to use
- 💬 **Multi-Platform** - CLI, WeChat, DingTalk, Feishu...

## 🚀 Quick Start

### One-Click Install (Windows)

```powershell
# Download and run install script
iwr https://raw.githubusercontent.com/badhope/Woclaw/main/scripts/install.ps1 -UseBasicParsing | iex
```

### Manual Installation

```bash
# Clone the project
git clone https://github.com/badhope/Woclaw.git
cd Woclaw

# Install dependencies
pip install -e .

# Start
woclaw chat
```

## 🏗️ Architecture

```
User Message
    ↓
┌─────────────────────────────┐
│   Supervisor (Decision Maker) │
│   • Understand intent        │
│   • Plan tasks              │
│   • Approve plans          │
│   • Verify results          │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│   Workers                   │
│   • FileWorker - File ops   │
│   • GuiWorker - GUI control │
│   • ShellWorker - Commands  │
│   • WebWorker - HTTP       │
│   • SysWorker - System     │
└─────────────────────────────┘
```

## 📖 Examples

### File Management

```
You: Organize images in Downloads folder by date
Star: Sure! Let me help you organize those images~

✅ Scanning Downloads folder (found 32 images)
✅ Creating date folders (2026-03, 2026-02...)
✅ Moving files to folders
✨ Done! Organized 32 images
```

### GUI Control

```
You: Open Notepad, type "Hello Star", and save
Star: On it! Operating now~

✅ Opening Notepad
✅ Activating window
✅ Typing text
✅ Clicking File menu
✅ Clicking Save As
✅ Saving file
✨ Done! File saved
```

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License

---

**Made with ✨ by Woclaw Team**
