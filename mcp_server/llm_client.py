"""OpenAI Integration for TipTrack MCP Server.

Provides an LLM client that uses OpenAI's function calling API
to invoke MCP tools based on natural language queries.
"""
import json
import os
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:
    raise ImportError("openai package required. Install with: pip install openai")

from mcp_server.tools import MCP_TOOLS


class TipTrackLLMClient:
    """OpenAI LLM client for TipTrack with MCP tool integration."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (default: reads from OPENAI_API_KEY env var)
            model: Model name (default: gpt-4o-mini for cost-efficiency)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.tools_executed = []  # Track tool calls for transparency
    
    def convert_tools_to_openai_format(self) -> List[Dict[str, Any]]:
        """Convert MCP tool definitions to OpenAI function calling format."""
        openai_tools = []
        
        for tool in MCP_TOOLS:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"],
                }
            }
            openai_tools.append(openai_tool)
        
        return openai_tools
    
    def query(self, user_message: str, tool_executor: Optional[Any] = None) -> str:
        """Send a query to OpenAI and execute MCP tools as needed.
        
        Args:
            user_message: Natural language user query
            tool_executor: MCPToolExecutor instance for tool execution
        
        Returns:
            Final response from LLM after tool calls
        """
        messages = [
            {
                "role": "system",
                "content": """You are an AI assistant for TipTrack, a smart hospitality tip and feedback management system.
You have access to tools that let you:
- Retrieve waiter performance statistics and analytics
- Submit tips and feedback
- Analyze customer sentiment and trends  
- Generate business intelligence reports
- Verify transactions via blockchain-style signatures

Use these tools to answer user queries about waiter performance, team analytics, customer feedback, and business recommendations.
Provide clear, actionable insights based on the data retrieved."""
            },
            {"role": "user", "content": user_message}
        ]
        
        openai_tools = self.convert_tools_to_openai_format()
        
        # Initial request to LLM with tools
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=openai_tools,
            tool_choice="auto",
            temperature=0.7,
        )
        
        # Process response and handle tool calls
        while response.choices[0].finish_reason == "tool_calls":
            tool_calls = response.choices[0].message.tool_calls
            
            # Add assistant's response to conversation
            messages.append({"role": "assistant", "content": response.choices[0].message.content or ""})
            
            # Execute each tool call
            tool_results = []
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                print(f"  🔧 Calling tool: {tool_name} with args: {tool_args}")
                self.tools_executed.append({"tool": tool_name, "args": tool_args})
                
                # Execute tool
                if tool_executor:
                    try:
                        result = tool_executor.execute_tool(tool_name, tool_args)
                        result_text = json.dumps(result, indent=2)
                    except Exception as e:
                        result_text = f"Error: {str(e)}"
                else:
                    result_text = "Tool executor not available"
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": result_text,
                })
            
            # Add tool results to conversation
            messages.append({"role": "user", "content": tool_results})
            
            # Request next response from LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=openai_tools,
                tool_choice="auto",
                temperature=0.7,
            )
        
        # Extract final text response
        final_response = response.choices[0].message.content or "No response generated"
        return final_response
    
    def get_execution_trace(self) -> List[Dict[str, Any]]:
        """Return list of tools that were executed during the last query."""
        return self.tools_executed
    
    def clear_execution_trace(self):
        """Clear the execution trace."""
        self.tools_executed = []


# Convenience function for simple queries
def query_tiptrack_ai(question: str, tool_executor: Optional[Any] = None, api_key: Optional[str] = None) -> str:
    """Quick function to query TipTrack AI.
    
    Args:
        question: Natural language question
        tool_executor: MCPToolExecutor instance (optional)
        api_key: OpenAI API key (optional, reads from env if not provided)
    
    Returns:
        AI-generated response with tool-based insights
    """
    client = TipTrackLLMClient(api_key=api_key)
    return client.query(question, tool_executor=tool_executor)
