# math_mcp/mcp_instance.py

from fastmcp import FastMCP

mcp = FastMCP(
    name="Mathematical MCP",
    version="1.0.0"
)

# ИМПОРТИРУЕМ ТУЛЗЫ ТОЛЬКО ТАК (абсолютно):
import server_mcp.tools.basic_math     # noqa: F401
import server_mcp.tools.geometry       # noqa: F401
import server_mcp.tools.statistics     # noqa: F401
import server_mcp.tools.resources      # noqa: F401
import server_mcp.tools.prompts        # noqa: F401
import server_mcp.tools.server_info    # noqa: F401
