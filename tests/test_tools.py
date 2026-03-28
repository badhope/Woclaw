"""
工具测试
"""

import pytest
import tempfile
import os

from woclaw.tools.filesystem import FilesystemTool
from woclaw.tools.shell import ShellTool
from woclaw.tools.data import DataTool


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


@pytest.mark.asyncio
async def test_data_json_read_write(temp_dir):
    """测试 JSON 读写"""
    tool = DataTool()
    test_file = os.path.join(temp_dir, "test.json")
    test_data = {"name": "Woclaw", "version": "0.1.0"}
    
    await tool.execute("json_write", path=test_file, data=test_data)
    data = await tool.execute("json_read", path=test_file)
    
    assert data == test_data


@pytest.mark.asyncio
async def test_data_csv_read_write(temp_dir):
    """测试 CSV 读写"""
    tool = DataTool()
    test_file = os.path.join(temp_dir, "test.csv")
    test_data = [
        {"name": "Woclaw", "version": "0.1.0"},
        {"name": "OpenClaw", "version": "1.0.0"},
    ]
    
    await tool.execute("csv_write", path=test_file, data=test_data)
    data = await tool.execute("csv_read", path=test_file)
    
    assert len(data) == 2
    assert data[0]["name"] == "Woclaw"


@pytest.mark.asyncio
async def test_data_filter():
    """测试数据过滤"""
    tool = DataTool()
    test_data = [
        {"name": "Woclaw", "type": "agent"},
        {"name": "OpenClaw", "type": "framework"},
        {"name": "MiniClaw", "type": "agent"},
    ]
    
    result = await tool.execute("filter", data=test_data, conditions={"type": "agent"})
    
    assert len(result) == 2


@pytest.mark.asyncio
async def test_data_transform():
    """测试数据转换"""
    tool = DataTool()
    test_data = [
        {"old_name": "Woclaw", "old_version": "0.1.0"},
    ]
    
    result = await tool.execute(
        "transform",
        data=test_data,
        mapping={"old_name": "name", "old_version": "version"}
    )
    
    assert result[0]["name"] == "Woclaw"
    assert result[0]["version"] == "0.1.0"
