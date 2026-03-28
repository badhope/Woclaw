# 贡献指南

感谢你对 Woclaw 项目的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 报告问题

如果你发现了 bug 或有功能建议，请：

1. 在 [Issues](https://github.com/badhope/Xiaobai/issues) 中搜索是否已有相关问题
2. 如果没有，创建一个新的 Issue，包含：
   - 清晰的标题
   - 详细的问题描述
   - 复现步骤（如果是 bug）
   - 预期行为和实际行为
   - 环境信息（Python 版本、操作系统等）

### 提交代码

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 进行修改
4. 运行测试：`pytest`
5. 运行代码检查：`ruff check .` 和 `black .`
6. 提交更改：`git commit -m "feat: your feature description"`
7. 推送分支：`git push origin feature/your-feature`
8. 创建 Pull Request

### 代码规范

- 使用 [Black](https://github.com/psf/black) 格式化代码
- 使用 [Ruff](https://github.com/astral-sh/ruff) 进行代码检查
- 添加类型注解
- 为新功能编写测试
- 更新相关文档

### 提交信息规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式（不影响功能）
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具相关

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/badhope/Xiaobai.git
cd Xiaobai

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev,all]"

# 安装 Playwright 浏览器
playwright install

# 运行测试
pytest

# 代码检查
ruff check .
black .
mypy woclaw
```

### 添加新工具

1. 在 `woclaw/tools/` 目录下创建新文件
2. 继承 `BaseTool` 类
3. 实现 `execute` 方法
4. 在 `woclaw/tools/__init__.py` 中注册
5. 添加测试用例
6. 更新文档

示例：

```python
from woclaw.tools.base import BaseTool
from typing import Any, ClassVar


class MyTool(BaseTool):
    name: ClassVar[str] = "my_tool"
    description: ClassVar[str] = "我的工具描述"
    
    async def execute(self, action: str, **kwargs) -> Any:
        handlers = {
            "action1": self._action1,
        }
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        return await handler(**kwargs)
    
    async def _action1(self, **kwargs) -> dict[str, Any]:
        return {"success": True, "result": "done"}
```

## 行为准则

请保持友好和尊重。我们致力于为所有人提供包容、友好的环境。

## 许可证

通过贡献代码，你同意你的代码将在 MIT 许可证下发布。
