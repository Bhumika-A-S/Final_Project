"""TipTrack MCP (Model Context Protocol) Server.

Provides LLM-accessible tools for TipTrack backend queries.

Components:
- tools.py: MCP tool definitions
- server.py: MCP protocol handler + tool executor
- llm_client.py: OpenAI integration
- mcp_llm_bridge.py: CLI and bridge interface
"""

__version__ = "1.0.0"
