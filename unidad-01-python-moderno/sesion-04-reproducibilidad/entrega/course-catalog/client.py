"""Launch the local server, list its tools, and make one request."""

import argparse
import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters


async def query_server(query: str) -> int:
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).resolve().with_name("server.py"))],
    )
    async with Client(server) as client:
        tools = await client.list_tools()
        print("Tools:", [tool.name for tool in tools.tools])
        result = await client.call_tool("find_courses", {"query": query})
        print(result.model_dump_json(indent=2))
        return 1 if result.is_error else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Try the local MCP catalog")
    parser.add_argument("query", nargs="?", default="python")
    args = parser.parse_args()
    return asyncio.run(query_server(args.query))


if __name__ == "__main__":
    raise SystemExit(main())
