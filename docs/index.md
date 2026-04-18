# Woclaw - 启明星 AI 助手 🌟

> **让 AI 像启明星一样，在黑暗中为你指引方向**

[English](en.md) | [中文](index.md) | [日本語](ja.md)

---

## ✨ 什么是 Woclaw？

Woclaw（谐音"启明星"）是一个**轻量级自主电脑控制 AI 助手**。它能理解你的自然语言指令，帮你操控电脑完成各种任务。

**核心理念**：让 AI 像人类一样操作电脑，而不是让你变成程序员。

## 🌟 核心特性

- 🧠 **智能决策者** - Supervisor Agent 理解你的意图，制定执行计划
- 🔧 **全能操控** - 文件、进程、GUI 窗口、网络请求，全部拿下
- 📚 **自我进化** - 从错误中学习，越用越聪明
- 🔒 **安全可控** - 风险分级，高风险操作需要确认
- 🛠️ **工具丰富** - 开箱即用的 5 大 Worker
- 💬 **多平台支持** - CLI、微信、钉钉、飞书...

## 🚀 快速开始

### 一键安装（Windows）

```powershell
# 下载并运行安装脚本
iwr https://raw.githubusercontent.com/badhope/Woclaw/main/scripts/install.ps1 -UseBasicParsing | iex
```

### 或手动安装

```bash
# 克隆项目
git clone https://github.com/badhope/Woclaw.git
cd Woclaw

# 安装依赖
pip install -e .

# 启动
woclaw chat
```

## 🏗️ 架构概览

```
用户消息
    ↓
┌─────────────────────────────┐
│   Supervisor（决策者）         │
│   • 理解意图                  │
│   • 规划任务                  │
│   • 审批计划                  │
│   • 验证结果                  │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│   Workers（工作者）           │
│   • FileWorker - 文件操作    │
│   • GuiWorker - GUI 操控     │
│   • ShellWorker - 命令执行   │
│   • WebWorker - 网络请求     │
│   • SysWorker - 系统信息     │
└─────────────────────────────┘
```

## 📖 使用示例

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

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**Made with ✨ by Woclaw Team**
