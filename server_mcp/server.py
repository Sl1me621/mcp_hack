# server.py
import os
from dotenv import load_dotenv
from server_mcp.mcp_instance import mcp

load_dotenv()

HOST = os.getenv("MCP_HOST", "127.0.0.1")
PORT = int(os.getenv("MCP_PORT", "8000"))
NAME = os.getenv("MCP_NAME", "MCP Server")

if __name__ == "__main__":
    print(f"🚀 Starting MCP server '{NAME}' on {HOST}:{PORT}")
    mcp.run(
        transport="http",
        host=HOST,
        port=PORT
    )
