"""Expose the same catalog function as a local MCP tool."""

import logging

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from catalog.logging_config import configure_logging
from catalog.search import Course, search_courses

mcp = MCPServer("Course catalog")
logger = logging.getLogger(__name__)


@mcp.tool()
def find_courses(query: str) -> list[Course]:
    """Find courses by words in their title, ignoring letter case."""
    try:
        return search_courses(query)
    except (OSError, ValueError) as error:
        logger.exception("Catalog search failed")
        raise ToolError(
            "Cannot search the catalog. Check the query and server logs."
        ) from error


if __name__ == "__main__":
    configure_logging()
    mcp.run(transport="stdio")
