# Woclaw 重构设计方案

> 版本：v0.2.0-draft  
> 日期：2026-03-29  
> 状态：待用户确认后启动开发

---

## 一、设计理念

### 核心目标
- **操作一切**：Windows GUI 精准操控（无白名单限制）
- **极简上手**：安装即用，有手就行
- **架构清晰**：每个模块职责单一，不混乱
- **国产优先**：微信 / 钉钉 / 飞书 / QQ 等全接入

### 对比 OpenClaw

| 问题 | OpenClaw | Woclaw v2 |
|------|----------|------------|
| 架构混乱 | 20+ 模块耦合严重 | 7 大核心模块，职责清晰 |
| 配置复杂 | 遍地配置，不知从哪改 | 单一 `config.yaml`，带引导 |
| 新手门槛 | 看着文档还是装不上 | 一键安装，5 分钟跑起来 |
| GUI 操控 | 需要配置白名单 | A11Y 引擎，任意窗口操作 |
| 网络问题 | 端口冲突、服务注册失败 | 端口自动探测 + 自愈机制 |
| 消息路由 | 路由逻辑混乱难懂 | 图状路由，状态可视化 |
| 文档质量 | 分散、版本不统一 | 集中文档，配套视频教程 |

---

## 二、系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                      用户层 (User Layer)                      │
│   微信  /  钉钉  /  飞书  /  QQ  /  Telegram  /  CLI        │
└────────────────────────┬─────────────────────────────────────┘
                         │ One Protocol
┌────────────────────────▼─────────────────────────────────────┐
│                  消息网关 (Message Gateway)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Channel  │  │ Channel  │  │ Channel  │  │ Channel  │   │
│  │ Adapter  │  │ Adapter  │  │ Adapter  │  │ Adapter  │   │
│  │ (微信)   │  │ (钉钉)   │  │ (飞书)   │  │ (CLI)    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬─────────────────────────────────────┘
                         │ Internal Message Bus
┌────────────────────────▼─────────────────────────────────────┐
│              多 Agent 编排层 (Agent Orchestrator)            │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Supervisor Agent（决策者）                   │  │
│  │  • 理解用户意图                                          │  │
│  │  • 拆解任务为子任务                                      │  │
│  │  • 分配任务给 Worker                                    │  │
│  │  • 审批 Worker 的执行计划                                │  │
│  │  • 整合结果返回给用户                                    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                               │                               │
│           ┌──────────────────┼──────────────────┐            │
│           │                  │                  │            │
│           ▼                  ▼                  ▼            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ FileWorker  │    │GUiWorker   │    │CodeWorker  │      │
│  │ 文件处理    │    │GUI操控     │    │代码执行    │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
│           │                  │                  │            │
│           ▼                  ▼                  ▼            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ WebWorker  │    │SysWorker  │    │BrowserWrkr │      │
│  │ 网络请求   │    │系统操作   │    │浏览器操控  │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                   Skill Manager（技能商店）                │  │
│  │  • 技能注册 / 发现 / 执行                                 │  │
│  │  • 技能依赖解析                                          │  │
│  │  • MCP 协议支持                                          │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                  工具层 (Tool Layer)                          │
│                                                                │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐      │
│  │GUI自动化│ │文件系统│ │进程管理│ │浏览器  │ │网络工具│      │
│  │A11Y引擎│ │        │ │        │ │        │ │        │      │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘      │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                 │
│  │系统监控│ │剪贴板  │ │截图OCR │ │注册表  │                 │
│  └────────┘ └────────┘ └────────┘ └────────┘                 │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                  LLM 层 (Model Layer)                        │
│                                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ OpenAI   │  │ Claude   │  │ Ollama   │  │ DeepSeek │    │
│  │ GPT-4/4o │  │ Opus/Sonnet│ │ 本地模型 │  │          │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │ Kimi/Moonshot│ │  Qwen  │  │  Gemini  │                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
└──────────────────────────────────────────────────────────────┘
```

---

## 三、核心模块详解

### 3.1 消息网关 (Message Gateway)

**职责**：统一处理所有聊天平台的消息

```
消息进来 → 标准化 → 路由决策 → Agent → 响应格式化 → 发回对应平台
```

**设计原则**：
- 每个平台一个 Adapter，互不干扰
- 消息格式统一为内部协议
- 支持消息撤回、已读、typing 等状态
- 自动重连、掉线自愈

**支持的平台**：
| 平台 | 优先级 | 状态 |
|------|--------|------|
| 微信 | P0 | 开发中 |
| 钉钉 | P0 | 待开发 |
| 飞书 | P0 | 待开发 |
| QQ | P1 | 待开发 |
| Telegram | P1 | 待开发 |
| 企业微信 | P2 | 待评估 |

### 3.2 Supervisor Agent（决策者）

**定位**：整个系统的大脑

**工作流程**：
```
1. 接收用户消息
2. 理解意图 → 判断是否需要执行动作
3. 若需要执行：
   a. 拆解为子任务
   b. 选择合适的 Worker
   c. 向 Worker 下发任务 + 获取执行计划
   d. 审批 Worker 的计划（有风险的操作需确认）
   e. 批准后 Worker 执行
   f. 整合结果，返回给用户
4. 若只是闲聊 → 直接回复
```

**关键设计**：
- **Plan-Act 双阶段**：Worker 先给计划，Supervisor 审批后再执行
- **多模型支持**：Supervisor 可以用更强的模型（GPT-4o/Claude Opus）
- **可配置审批规则**：用户可以设置哪些操作需要确认

### 3.3 Worker Agent（工作者）

**内置 Worker**：
| Worker | 能力 |
|--------|------|
| `FileWorker` | 文件读写、移动、压缩、批量处理 |
| `GuiWorker` | Windows GUI 操控、窗口操作 |
| `CodeWorker` | 代码生成、执行、调试 |
| `WebWorker` | HTTP 请求、API 调用 |
| `SysWorker` | 系统操作、进程管理、注册表 |
| `BrowserWorker` | 浏览器自动化（Playwright） |

**Worker 设计模式**：
```python
class BaseWorker:
    name: str                    # Worker 名称
    capabilities: list[str]      # 能处理的 task 类型
    model: str                   # 使用什么模型
    
    async def plan(task: Task) -> ExecutionPlan:
        """返回执行计划，等待 Supervisor 审批"""
        
    async def execute(plan: Plan) -> Result:
        """执行经审批的计划"""
```

### 3.4 GUI 操控引擎（重点）

**架构**：
```
┌─────────────────────────────────────────────┐
│              GUI Automation Engine           │
│                                              │
│  ┌───────────────┐  ┌───────────────┐      │
│  │  Window Tree  │  │  Accessibility│      │
│  │   窗口树解析   │  │    引擎       │      │
│  └───────┬───────┘  └───────┬───────┘      │
│          │                  │               │
│          ▼                  ▼               │
│  ┌─────────────────────────────────────┐   │
│  │         Control Finder               │   │
│  │  按标题 / 类型 / 位置 / 文本找控件    │   │
│  └───────┬─────────────────────────────┘   │
│          │                                  │
│          ▼                                  │
│  ┌─────────────────────────────────────┐   │
│  │       Action Executor                │   │
│  │  点击 / 输入 / 拖拽 / 滚轮 / 快捷键  │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**核心能力**：
- ✅ 读取任意窗口的 UI 树
- ✅ 按文本、类型、位置找控件
- ✅ 模拟点击、输入、拖拽
- ✅ 支持快捷键组合
- ✅ 截图 + OCR 辅助定位
- ✅ 不依赖坐标（窗口移动也能工作）
- ❌ 不需要白名单

### 3.5 Skill 技能系统

**设计参考**：CrewAI + OpenClaw Skills + MCP 协议

**技能结构**：
```
skill/
├── SKILL.md          # 技能描述、参数说明
├── scripts/
│   └── run.py        # 技能执行脚本
├── config.json       # 技能配置
└── requirements.txt  # 依赖
```

**内置技能**：
| 技能 | 功能 |
|------|------|
| `file-organizer` | 按规则整理文件夹 |
| `screenshot-ocr` | 截图识别文字 |
| `web-scraper` | 网页内容抓取 |
| `excel-auto` | Excel 操作 |
| `schedule-task` | 定时任务 |
| `habit-tracker` | 习惯追踪 |
| ... | 更多技能持续添加 |

**技能商店**：
- 支持从 ClawHub / GitHub 安装技能
- 一键安装：`woclaw skill install xxx`
- 用户可自己编写技能

### 3.6 LLM 模型层

**支持列表**：
| 模型 | 状态 | 说明 |
|------|------|------|
| OpenAI GPT-4/4o | ✅ 已支持 | API |
| Claude 3.5/3.7 | ✅ 已支持 | API |
| Ollama (本地) | ✅ 已支持 | 本地 |
| DeepSeek | 🔄 开发中 | API |
| Kimi (Moonshot) | 🔄 开发中 | API |
| Qwen (通义) | 🔄 开发中 | API |
| Gemini | 🔄 开发中 | API |

**模型选择策略**：
- 简单任务 → 本地模型（快、省钱）
- 复杂规划 → 云端强模型（GPT-4o / Claude Opus）
- 用户可配置默认模型

---

## 四、项目结构（重构后）

```
woclaw/
├── config.yaml                 # 唯一配置文件（替代 config.py）
├── pyproject.toml
├── README.md
├── docs/                       # 文档
│   ├── getting-started.md       # 快速入门
│   ├── configuration.md        # 配置指南
│   ├── skills/                 # 技能文档
│   └── platform/               # 平台接入指南
├── src/
│   └── woclaw/
│       ├── __init__.py
│       ├── cli.py              # CLI 入口
│       │
│       ├── core/                # 核心
│       │   ├── __init__.py
│       │   ├── supervisor.py    # Supervisor Agent
│       │   ├── worker.py        # Worker 基类
│       │   ├── workers/        # 具体 Worker
│       │   │   ├── __init__.py
│       │   │   ├── file_worker.py
│       │   │   ├── gui_worker.py
│       │   │   ├── code_worker.py
│       │   │   ├── web_worker.py
│       │   │   ├── sys_worker.py
│       │   │   └── browser_worker.py
│       │   ├── skill/          # 技能系统
│       │   │   ├── __init__.py
│       │   │   ├── manager.py   # 技能管理器
│       │   │   ├── registry.py  # 技能注册表
│       │   │   └── runner.py    # 技能执行器
│       │   └── memory/          # 记忆系统
│       │       ├── __init__.py
│       │       ├── short_term.py
│       │       └── long_term.py
│       │
│       ├── llm/                 # LLM 适配层
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── openai.py
│       │   ├── anthropic.py
│       │   ├── ollama.py
│       │   └── registry.py
│       │
│       ├── gateway/            # 消息网关
│       │   ├── __init__.py
│       │   ├── router.py        # 消息路由
│       │   ├── session.py       # 会话管理
│       │   └── adapters/        # 平台适配器
│       │       ├── __init__.py
│       │       ├── base.py
│       │       ├── wechat.py
│       │       ├── dingtalk.py
│       │       ├── feishu.py
│       │       ├── qq.py
│       │       ├── telegram.py
│       │       └── cli.py
│       │
│       ├── tools/              # 工具集
│       │   ├── __init__.py
│       │   ├── gui/            # GUI 操控（重点！）
│       │   │   ├── __init__.py
│       │   │   ├── engine.py    # A11Y 引擎
│       │   │   ├── window.py    # 窗口操作
│       │   │   ├── control.py   # 控件操作
│       │   │   └── finder.py    # 控件查找
│       │   ├── filesystem.py
│       │   ├── process.py
│       │   ├── network.py
│       │   ├── clipboard.py
│       │   ├── screenshot.py
│       │   ├── system.py
│       │   └── browser.py
│       │
│       └── utils/              # 工具函数
│           ├── __init__.py
│           ├── config.py        # 配置加载
│           ├── log.py          # 日志
│           └── security.py      # 安全相关
│
├── tests/                      # 测试
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
└── scripts/                    # 脚本
    ├── install.bat             # Windows 一键安装
    └── setup-wizard.py         # 配置引导
```

---

## 五、CLI 设计

### 5.1 命令结构

```bash
woclaw --help

# 核心命令
woclaw run "帮我整理下载文件夹"     # 执行任务
woclaw chat                        # 交互模式
woclaw status                       # 查看状态
woclaw config                       # 配置管理
woclaw config --wizard              # 引导配置

# 技能管理
woclaw skill list                   # 列出技能
woclaw skill install <name>         # 安装技能
woclaw skill uninstall <name>       # 卸载技能
woclaw skill search <keyword>       # 搜索技能

# 平台管理
woclaw channel list                 # 列出已接入平台
woclaw channel add wechat           # 接入微信
woclaw channel add dingtalk         # 接入钉钉
woclaw channel remove wechat        # 移除平台

# 开发者
woclaw dev test-worker <name>       # 测试 Worker
woclaw dev skill scaffold <name>    # 创建技能模板
woclaw log --tail                   # 查看日志
```

### 5.2 交互模式 UI

```
┌─────────────────────────────────────────────┐
│  🦀 Woclaw v0.2.0                          │
│─────────────────────────────────────────────│
│  状态: 🟢 运行中                            │
│  模型: Claude Opus (本地 Ollama 备用)       │
│  平台: 微信 🟢  钉钉 🟢  飞书 🔴           │
│─────────────────────────────────────────────│
│                                             │
│  你 > 帮我把桌面上的截图移到 Pictures 文件夹  │
│                                             │
│  🦀 > 好的，正在处理...                      │
│                                             │
│  📋 执行计划：                               │
│  1. 扫描桌面，找到所有 .png/.jpg 文件        │
│  2. 创建 Pictures/Screenshots 文件夹         │
│  3. 移动文件到目标位置                       │
│                                             │
│  ✓ 已开始执行...                            │
│  ✓ 找到 12 个截图文件                       │
│  ✓ 创建文件夹成功                           │
│  ✓ 已移动 12 个文件                         │
│                                             │
│  ✅ 完成！已将 12 个截图整理到 Pictures/Screenshots │
│                                             │
└─────────────────────────────────────────────┘
```

### 5.3 配置引导流程

```
$ woclaw config --wizard

欢迎使用 Woclaw 配置向导！
让我们一步步配置你的 AI 助手。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 第 1 步：选择 LLM 模型

你有以下选择：
  [1] OpenAI GPT-4o    - 最强模型，需 API Key
  [2] Claude 3.7 Sonnet - 性价比高，需 API Key  
  [3] Ollama (本地)    - 免费，但需要本地部署
  [4] DeepSeek         - 国产，便宜

请选择 [1-4] 或按回车跳过:

> _
```

---

## 六、安装与部署

### 6.1 Windows 一键安装

```powershell
# 方式 1: PowerShell 一键安装（推荐）
iwr https://raw.githubusercontent.com/badhope/Woclaw/main/scripts/install.ps1 -UseBasicParsing | iex

# 方式 2: 手动安装
git clone https://github.com/badhope/Woclaw.git
cd Woclaw
.\scripts\install.bat
```

### 6.2 启动流程

```bash
# 首次启动，自动进入配置向导
woclaw start

# 或手动启动
woclaw start --no-config
```

---

## 七、开发计划

### Phase 1：核心框架（2-3 周）
- [ ] 重构项目结构
- [ ] 实现 Supervisor + Worker 架构
- [ ] 实现 GUI A11Y 引擎
- [ ] 实现 LLM 适配层
- [ ] 实现 CLI 入口

### Phase 2：平台接入（2 周）
- [ ] 微信适配器
- [ ] 钉钉适配器
- [ ] 飞书适配器

### Phase 3：技能系统（1-2 周）
- [ ] 技能管理器
- [ ] 内置技能
- [ ] 技能商店

### Phase 4：优化与文档（持续）
- [ ] 新手引导
- [ ] 配置向导
- [ ] 完整文档
- [ ] 视频教程

---

## 八、关键决策清单

以下决策需要你确认：

| # | 决策项 | 选项 | 你的选择 |
|---|--------|------|----------|
| 1 | 开发语言 | Python / Go / TypeScript | 待定 |
| 2 | Supervisor 模型 | GPT-4o / Claude Opus / 本地 | 待定 |
| 3 | Worker 模型 | 本地 / 云端混用 | 待定 |
| 4 | GUI 引擎 | Windows UI Automation / pywinauto | 待定 |
| 5 | 数据库 | SQLite（本地）/ PostgreSQL（可选） | 待定 |
| 6 | 微信接入 | 网页协议 / Windows Hook | 待定 |

---

## 九、待你回答

1. **开发语言**：继续用 Python，还是考虑 Go / TypeScript？
2. **Supervisor 模型**：你想用哪个模型做决策？GPT-4o / Claude Opus / 其他？
3. **其他 OpenClaw 问题**：你用过 OpenClaw 吗？遇到的最头疼的问题是什么？
4. **优先级**：Phase 1 里，哪个功能你最急着要？（GUI 操控？聊天入口？）

---

_本文档将随项目进展持续更新_
