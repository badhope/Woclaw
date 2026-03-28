# 更新日志

所有重要的更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2026-03-29

### 新增

#### 核心功能
- Agent 核心模块（理解、规划、执行、验证工作流）
- LLM 接口层（支持 OpenAI、Claude、Ollama）
- 任务规划器（智能分解任务为可执行步骤）
- 任务执行器（支持重试和超时）
- 记忆系统（任务历史存储）

#### 工具集 (13个工具)
- `filesystem` - 文件系统操作（读写、复制、移动、删除、搜索）
- `shell` - 执行系统命令
- `browser` - 浏览器控制（导航、点击、输入、截图）
- `web` - HTTP 请求（GET/POST/下载）
- `data` - 数据处理（JSON/CSV 读写、过滤、转换）
- `process` - 进程管理（列出、查找、启动、终止）
- `clipboard` - 剪贴板操作（读、写、清空）
- `system` - 系统监控（CPU、内存、磁盘、网络、电池）
- `network` - 网络工具（下载、DNS、端口扫描、Ping）
- `screenshot` - 截图（全屏、区域、窗口）
- `automation` - 键盘鼠标模拟（按键、热键、点击、移动）
- `archive` - 压缩解压（ZIP/TAR 创建和提取）
- `image` - 图像处理（调整大小、格式转换、裁剪、滤镜）

#### 存储层
- PostgreSQL 数据库支持
- 内存缓存系统

#### CLI 命令行工具
- `woclaw` - 交互模式
- `woclaw run "任务"` - 执行任务
- `woclaw tools` - 列出工具
- `woclaw config` - 显示配置

#### 其他
- 配置文件模板 (`config.example.py`)
- 完整的项目文档
- GitHub Actions CI/CD
- 单元测试框架

### 技术栈
- Python 3.10+
- asyncio 异步编程
- Playwright 浏览器自动化
- psutil 系统监控
- PyAutoGUI 桌面自动化
- Pillow 图像处理

## [Unreleased]

### 计划中
- 音频处理工具（录音、播放、语音识别）
- 视频处理工具（录屏、剪辑）
- PDF 处理工具（读取、合并、分割）
- 邮件发送工具
- 定时任务功能
- Web UI 界面
- 插件系统
