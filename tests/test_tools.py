"""
工具测试
"""

import pytest
import tempfile
import os

from woclaw.tools.filesystem import FilesystemTool
from woclaw.tools.shell import ShellTool


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.mark.asyncio
async def test_filesystem_read_write(temp_dir):
    """测试文件读写"""
    tool = FilesystemTool()
    test_file = os.path.join(temp_dir, "test.txt")
    test_content = "Hello, Woclaw!"
    
    await tool.execute("write", path=test_file, content=test_content)
    content = await tool.execute("read", path=test_file)
    
    assert content == test_content


@pytest.mark.asyncio
async def test_filesystem_list(temp_dir):
    """测试目录列表"""
    tool = FilesystemTool()
    
    for i in range(3):
        with open(os.path.join(temp_dir, f"file{i}.txt"), "w") as f:
            f.write(f"content {i}")
    
    files = await tool.execute("list", path=temp_dir, pattern="*.txt")
    
    assert len(files) == 3


@pytest.mark.asyncio
async def test_filesystem_search(temp_dir):
    """测试文件搜索"""
    tool = FilesystemTool()
    
    test_file = os.path.join(temp_dir, "test.txt")
    with open(test_file, "w") as f:
        f.write("Hello World\nThis is a test\nHello again")
    
    results = await tool.execute("search", path=temp_dir, query="Hello")
    
    assert len(results) == 1
    assert results[0]["matches"] == 2


@pytest.mark.asyncio
async def test_shell_echo():
    """测试 Shell 命令执行"""
    tool = ShellTool()
    
    result = await tool.execute("echo 'Hello, Woclaw!'")
    
    assert result["success"] is True
    assert "Hello, Woclaw!" in result["stdout"]


@pytest.mark.asyncio
async def test_shell_timeout():
    """测试 Shell 命令超时"""
    tool = ShellTool()
    
    result = await tool.execute("sleep 10", timeout=1)
    
    assert result["success"] is False
    assert "timeout" in result["error"].lower()
