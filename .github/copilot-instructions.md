# Copilot Instructions for MCP Server Setup

To support Model Context Protocol (MCP) servers in this repository, follow these guidelines:

1. Refer to the official MCP SDK documentation on GitHub: https://github.com/modelcontextprotocol.  The repository contains SDKs for TypeScript, JavaScript, Python, C#, Java, and Kotlin.  For this project we are using Python.
2. The upstream specifications and usage examples can be found via the protocol website (e.g. https://modelcontextprotocol.io/).  Developers should review the "LLMs full" text file for details on message formats.
3. Add or update the `.vscode/mcp.json` file (below) to register the MCP server and allow debugging within VS Code.
4. Install the necessary VS Code extension for the chosen language (Python extension is already recommended).
5. Once the server project is available, the user can start and debug it using the command specified in `mcp.json`.

The `mcp_server` folder contains a minimal Python-based MCP server implementation.  It listens on standard input/output and responds to simple context requests.  Developers can expand this server to handle the full MCP messages and integrate with the TipTrack backend as needed.
