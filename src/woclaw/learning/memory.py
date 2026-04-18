"""
LearningMemory - 启明星的学习记忆系统
负责加载和保存学习经验
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Optional


class LearningMemory:
    """
    学习记忆系统
    参考 OpenClaw 的 self-improving-agent 设计
    """

    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path.home() / ".woclaw" / ".learnings"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 学习文件路径
        self.learnings_file = self.data_dir / "LEARNINGS.md"
        self.errors_file = self.data_dir / "ERRORS.md"
        self.feedback_file = self.data_dir / "FEEDBACK.md"
        self.skills_file = self.data_dir / "SKILLS_META.md"

        # 内存缓存
        self.learnings: list[dict] = []
        self.errors: list[dict] = []
        self.feedback: list[dict] = []
        self.skills: list[dict] = []

        # 是否已加载
        self._loaded = False

    async def load(self):
        """加载所有学习文件"""
        if self._loaded:
            return

        # 加载 LEARNINGS.md
        if self.learnings_file.exists():
            self.learnings = await self._parse_learnings(self.learnings_file)

        # 加载 ERRORS.md
        if self.errors_file.exists():
            self.errors = await self._parse_errors(self.errors_file)

        # 加载 FEEDBACK.md
        if self.feedback_file.exists():
            self.feedback = await self._parse_feedback(self.feedback_file)

        # 如果没有学习文件，创建模板
        if not self.learnings_file.exists():
            await self._create_templates()

        self._loaded = True

    async def save(self):
        """保存所有学习文件"""
        # 保存 LEARNINGS.md
        await self._save_learnings()

        # 保存 ERRORS.md
        await self._save_errors()

        # 保存 FEEDBACK.md
        await self._save_feedback()

    async def _create_templates(self):
        """创建学习文件模板"""
        # LEARNINGS.md
        template = f"""# Woclaw 学习经验库 ✨

> 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 用户偏好
- 记录用户喜欢的工作方式和习惯

## 常用工作流
- 记录成功的任务执行模式

## 成功案例
- 记录成功的任务和解决方法

## 最佳实践
- 记录实用技巧和经验

"""
        self.learnings_file.write_text(template, encoding="utf-8")

        # ERRORS.md
        errors_template = f"""# Woclaw 错误记录 ❌

> 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 已解决错误
| 时间 | 错误 | 原因 | 解决方案 |
|------|------|------|----------|

## 避免方法
1. 

"""
        self.errors_file.write_text(errors_template, encoding="utf-8")

        # FEEDBACK.md
        feedback_template = f"""# Woclaw 用户反馈 💬

> 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 用户纠正
| 时间 | 场景 | 用户纠正 | 正确做法 |
|------|------|----------|----------|

## 用户偏好
- 记录用户的偏好和习惯

"""
        self.feedback_file.write_text(feedback_template, encoding="utf-8")

    async def _parse_learnings(self, file: Path) -> list[dict]:
        """解析学习文件"""
        content = file.read_text(encoding="utf-8")
        learnings = []

        # 简单的 Markdown 表格解析
        lines = content.split("\n")
        in_case = False
        current_case = {}

        for line in lines:
            if "## 成功案例" in line:
                in_case = True
            elif in_case and "|" in line and "时间" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    current_case = {
                        "date": parts[1],
                        "task": parts[2],
                        "method": parts[3],
                    }
                    learnings.append(current_case)

        return learnings

    async def _parse_errors(self, file: Path) -> list[dict]:
        """解析错误文件"""
        content = file.read_text(encoding="utf-8")
        errors = []

        lines = content.split("\n")
        for line in lines:
            if "|" in line and "时间" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    errors.append({
                        "date": parts[1],
                        "error": parts[2],
                        "cause": parts[3],
                        "solution": parts[4] if len(parts) > 4 else "",
                    })

        return errors

    async def _parse_feedback(self, file: Path) -> list[dict]:
        """解析反馈文件"""
        content = file.read_text(encoding="utf-8")
        feedback = []

        lines = content.split("\n")
        for line in lines:
            if "|" in line and "时间" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    feedback.append({
                        "date": parts[1],
                        "scene": parts[2],
                        "correction": parts[3],
                        "correct": parts[4] if len(parts) > 4 else "",
                    })

        return feedback

    async def _save_learnings(self):
        """保存学习文件"""
        content = f"""# Woclaw 学习经验库 ✨

> 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 用户偏好
{self._get_user_preferences()}

## 常用工作流
{self._get_workflows()}

## 成功案例
| 时间 | 任务 | 方法 |
|------|------|------|
"""
        for item in self.learnings[-20:]:  # 只保留最近 20 条
            content += f"| {item.get('date', '')} | {item.get('task', '')} | {item.get('method', '')} |\n"

        content += "\n## 最佳实践\n"
        for item in self.learnings[-10:]:
            if "best_practice" in item:
                content += f"- {item['best_practice']}\n"

        self.learnings_file.write_text(content, encoding="utf-8")

    async def _save_errors(self):
        """保存错误文件"""
        content = f"""# Woclaw 错误记录 ❌

> 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 已解决错误
| 时间 | 错误 | 原因 | 解决方案 |
|------|------|------|----------|
"""
        for item in self.errors[-20:]:
            content += f"| {item.get('date', '')} | {item.get('error', '')} | {item.get('cause', '')} | {item.get('solution', '')} |\n"

        content += "\n## 避免方法\n"
        seen_methods = set()
        for item in self.errors:
            method = item.get("solution", "")
            if method and method not in seen_methods:
                content += f"{len(seen_methods) + 1}. {method}\n"
                seen_methods.add(method)

        self.errors_file.write_text(content, encoding="utf-8")

    async def _save_feedback(self):
        """保存反馈文件"""
        content = f"""# Woclaw 用户反馈 💬

> 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 用户纠正
| 时间 | 场景 | 用户纠正 | 正确做法 |
|------|------|----------|----------|
"""
        for item in self.feedback[-20:]:
            content += f"| {item.get('date', '')} | {item.get('scene', '')} | {item.get('correction', '')} | {item.get('correct', '')} |\n"

        self.feedback_file.write_text(content, encoding="utf-8")

    def _get_user_preferences(self) -> str:
        """获取用户偏好"""
        prefs = []
        for item in self.feedback:
            if "preference" in item:
                prefs.append(f"- {item['preference']}")
        return "\n".join(prefs) if prefs else "- 暂无记录"

    def _get_workflows(self) -> str:
        """获取常用工作流"""
        workflows = []
        for item in self.learnings:
            if "workflow" in item:
                workflows.append(f"- {item['workflow']}")
        return "\n".join(workflows) if workflows else "- 暂无记录"

    # ==================== 记录方法 ====================

    async def record_success(self, task: str, steps: list[dict], **kwargs):
        """记录成功案例"""
        self.learnings.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "task": task,
            "steps": steps,
            "method": self._summarize_method(steps),
        })
        await self.save()

    async def record_error(self, operation: str, error: str, context: dict = None, **kwargs):
        """记录错误"""
        self.errors.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "error": error,
            "operation": operation,
            "context": context or {},
            "cause": self._analyze_error_cause(error, operation),
            "solution": "",
        })
        await self.save()

    async def record_feedback(self, scene: str, correction: str, correct_action: str, **kwargs):
        """记录用户反馈"""
        self.feedback.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "scene": scene,
            "correction": correction,
            "correct": correct_action,
        })
        await self.save()

    async def record_best_practice(self, practice: str, context: str, **kwargs):
        """记录最佳实践"""
        self.learnings.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "best_practice": practice,
            "context": context,
        })
        await self.save()

    # ==================== 获取上下文 ====================

    def get_context_prompt(self) -> str:
        """获取上下文提示（用于 LLM 提示词）"""
        if not self._loaded:
            return ""

        context_parts = []

        # 添加最近的错误和解决方案
        if self.errors:
            context_parts.append("### ⚠️ 需要注意的错误：")
            for item in self.errors[-5:]:
                if item.get("solution"):
                    context_parts.append(f"- {item['error']}: {item['solution']}")

        # 添加用户偏好
        if self.feedback:
            context_parts.append("\n### 💡 用户偏好：")
            prefs = set()
            for item in self.feedback[-10:]:
                if item.get("scene"):
                    prefs.add(f"- {item['scene']}")
            context_parts.extend(list(prefs)[:5])

        # 添加成功案例
        if self.learnings:
            context_parts.append("\n### ✨ 成功的经验：")
            for item in self.learnings[-3:]:
                if item.get("method"):
                    context_parts.append(f"- {item['method']}")

        return "\n".join(context_parts) if context_parts else ""

    def get_conversation_prompt(self) -> str:
        """获取对话提示"""
        if not self.feedback:
            return ""

        prefs = []
        for item in self.feedback[-5:]:
            if "偏好" in item.get("scene", ""):
                prefs.append(item.get("correct", ""))

        if prefs:
            return f"\n用户的偏好：{'；'.join(prefs)}\n"
        return ""

    # ==================== 辅助方法 ====================

    def _summarize_method(self, steps: list[dict]) -> str:
        """总结方法"""
        if not steps:
            return "直接执行"

        tools = [s.get("tool", "") for s in steps]
        return f"使用 {', '.join(set(tools))} 完成"

    def _analyze_error_cause(self, error: str, operation: str) -> str:
        """分析错误原因"""
        error_lower = error.lower()

        if "not found" in error_lower or "不存在" in error:
            return "路径或文件名错误"
        elif "permission" in error_lower or "权限" in error:
            return "需要管理员权限或文件被占用"
        elif "timeout" in error_lower or "超时" in error:
            return "操作耗时过长"
        elif "encoding" in error_lower or "编码" in error:
            return "文件编码问题"
        else:
            return "未知原因"

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "total_learnings": len(self.learnings),
            "total_errors": len(self.errors),
            "total_feedback": len(self.feedback),
            "resolved_errors": len([e for e in self.errors if e.get("solution")]),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
