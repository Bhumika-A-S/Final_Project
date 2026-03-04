"""MCP-LLM Bridge for TipTrack.

Provides a unified interface for LLM-powered queries using MCP tools.
Can run as a standalone service or be integrated into other applications.

Usage (as a script):
    python mcp_llm_bridge.py "What is waiter W001's performance?"
    
Usage (as module):
    from mcp_llm_bridge import MCPLLMBridge
    bridge = MCPLLMBridge()
    response = bridge.process_query("Show me the team leaderboard")
    print(response['answer'])
    print(response['tools_used'])
"""
import os
import sys
import json
import argparse
from typing import Any, Dict, List, Optional

from mcp_server.server import MCPToolExecutor
from mcp_server.llm_client import TipTrackLLMClient


class MCPLLMBridge:
    """Bridge between MCP tools and LLM for TipTrack queries."""
    
    def __init__(
        self,
        backend_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
    ):
        """Initialize the bridge.
        
        Args:
            backend_url: TipTrack backend URL (defaults from env)
            auth_token: JWT token for backend auth (defaults from env)
            openai_api_key: OpenAI API key (defaults from env)
            model: OpenAI model to use
        """
        backend_url = backend_url or os.getenv("TIPTRACK_BACKEND_URL", "http://localhost:8000")
        auth_token = auth_token or os.getenv("TIPTRACK_MCP_TOKEN", "")
        
        self.tool_executor = MCPToolExecutor(backend_url=backend_url, auth_token=auth_token)
        self.llm_client = TipTrackLLMClient(api_key=openai_api_key, model=model)
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a natural language query using LLM + MCP tools.
        
        Args:
            query: Natural language user query
        
        Returns:
            Dictionary with:
            - 'answer': LLM-generated response
            - 'tools_used': List of tools that were called
            - 'success': Whether query succeeded
        """
        try:
            self.llm_client.clear_execution_trace()
            answer = self.llm_client.query(query, tool_executor=self.tool_executor)
            tools_used = self.llm_client.get_execution_trace()
            
            return {
                "answer": answer,
                "tools_used": tools_used,
                "success": True,
            }
        except Exception as e:
            return {
                "answer": f"Error processing query: {str(e)}",
                "tools_used": [],
                "success": False,
            }
    
    def interactive_session(self):
        """Start an interactive Q&A session."""
        print("🤖 TipTrack AI Assistant (powered by OpenAI + MCP)")
        print("=" * 60)
        print("Ask questions about waiter performance, team analytics, feedback, etc.")
        print("Type 'exit' to quit, 'help' for examples.\n")
        
        while True:
            try:
                query = input("👤 You: ").strip()
                
                if query.lower() == "exit":
                    print("Goodbye!")
                    break
                elif query.lower() == "help":
                    self._print_examples()
                    continue
                elif not query:
                    continue
                
                print("\n🔍 Processing query...\n")
                result = self.process_query(query)
                
                print(f"🤖 Assistant: {result['answer']}\n")
                
                if result['tools_used']:
                    print("📊 Tools used:")
                    for tool_info in result['tools_used']:
                        print(f"  • {tool_info['tool']}: {json.dumps(tool_info['args'])}")
                    print()
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}\n")
    
    @staticmethod
    def _print_examples():
        """Print example queries."""
        examples = [
            "What is waiter W001's total tips and average rating?",
            "Show me the team leaderboard",
            "What are the recommendations for improving team performance?",
            "Get insights for waiter W002",
            "Generate a business intelligence report",
            "What's the overall team score?",
        ]
        print("\n📋 Example queries:")
        for i, example in enumerate(examples, 1):
            print(f"  {i}. {example}")
        print()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TipTrack AI Assistant - Query business data with natural language"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Query to process (if not provided, starts interactive mode)",
    )
    parser.add_argument(
        "--backend-url",
        default=os.getenv("TIPTRACK_BACKEND_URL", "http://localhost:8000"),
        help="Backend API URL",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("TIPTRACK_MCP_TOKEN", ""),
        help="Authentication token for backend",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("OPENAI_API_KEY"),
        help="OpenAI API key",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Start interactive mode",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("❌ Error: OPENAI_API_KEY not set. Set it as an environment variable or use --api-key")
        sys.exit(1)
    
    bridge = MCPLLMBridge(
        backend_url=args.backend_url,
        auth_token=args.token,
        openai_api_key=args.api_key,
        model=args.model,
    )
    
    if args.interactive or not args.query:
        bridge.interactive_session()
    else:
        print(f"🔍 Query: {args.query}\n")
        result = bridge.process_query(args.query)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"🤖 Answer:\n{result['answer']}\n")
            if result['tools_used']:
                print("📊 Tools executed:")
                for tool in result['tools_used']:
                    print(f"  • {tool['tool']}: {json.dumps(tool['args'])}")


if __name__ == "__main__":
    main()
