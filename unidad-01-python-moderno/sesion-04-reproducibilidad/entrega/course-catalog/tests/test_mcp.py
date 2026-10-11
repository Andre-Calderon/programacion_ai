import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters


async def check_server() -> None:
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).resolve().parents[1] / "server.py")],
        cwd=str(Path(__file__).resolve().parents[2]),
    )
    async with Client(server) as client:
        tools = await client.list_tools()
        assert [tool.name for tool in tools.tools] == ["find_courses"]
        result = await client.call_tool("find_courses", {"query": "python"})
        assert not result.is_error
        assert "PY01" in result.model_dump_json()
        assert "PY02" in result.model_dump_json()
        empty = await client.call_tool("find_courses", {"query": "astronomy"})
        assert not empty.is_error
        invalid = await client.call_tool("find_courses", {"query": " "})
        assert invalid.is_error
        again = await client.call_tool("find_courses", {"query": "python"})
        assert not again.is_error


def test_real_stdio_server() -> None:
    asyncio.run(check_server())
