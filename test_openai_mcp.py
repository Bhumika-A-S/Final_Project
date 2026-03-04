#!/usr/bin/env python3
"""Test script for TipTrack OpenAI MCP integration.

Run after setting OPENAI_API_KEY environment variable.
"""
import os
import sys
from mcp_server.server import MCPToolExecutor
from mcp_server.llm_client import TipTrackLLMClient


def test_tool_executor():
    """Test that tool executor can call backend endpoints."""
    print("=" * 60)
    print("Testing MCPToolExecutor...")
    print("=" * 60)
    
    executor = MCPToolExecutor(
        backend_url="http://localhost:8000",
        auth_token=""
    )
    
    # Test a simple tool call (requires backend running)
    try:
        result = executor.execute_tool("get_waiter_stats", {"waiter_id": "W001"})
        print(f"✓ Tool executor working: {result}")
        return True
    except Exception as e:
        print(f"✗ Tool executor error: {e}")
        print("  (Make sure backend is running on http://localhost:8000)")
        return False


def test_llm_client():
    """Test OpenAI LLM client initialization."""
    print("\n" + "=" * 60)
    print("Testing TipTrackLLMClient...")
    print("=" * 60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("✗ OPENAI_API_KEY not set")
        return False
    
    try:
        client = TipTrackLLMClient(api_key=api_key)
        print(f"✓ LLM client initialized successfully")
        print(f"  Model: {client.model}")
        print(f"  Available tools: {len(client.convert_tools_to_openai_format())}")
        return True
    except Exception as e:
        print(f"✗ LLM client error: {e}")
        return False


def test_query(query: str = "What tools are available?"):
    """Test a simple LLM query without tool execution."""
    print("\n" + "=" * 60)
    print(f"Testing Query: '{query}'")
    print("=" * 60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("✗ OPENAI_API_KEY not set")
        return False
    
    try:
        client = TipTrackLLMClient(api_key=api_key)
        print("🔍 Sending query to OpenAI...")
        
        # Create a simple message without tool execution
        from openai import OpenAI
        openai_client = OpenAI(api_key=api_key)
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for TipTrack hospitality system."},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
        )
        
        answer = response.choices[0].message.content
        print(f"✓ Query successful!\n")
        print(f"Response:\n{answer}")
        return True
    except Exception as e:
        print(f"✗ Query error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("🧪 TipTrack OpenAI MCP Integration Tests")
    print("=" * 60)
    
    # Check environment
    print("\nEnvironment Check:")
    print(f"  OPENAI_API_KEY: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ Not set'}")
    print(f"  Backend URL: {os.getenv('TIPTRACK_BACKEND_URL', 'http://localhost:8000')} (default)")
    
    results = {
        "Tool Executor": test_tool_executor(),
        "LLM Client": test_llm_client(),
        "Simple Query": test_query(),
    }
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ All tests passed! Ready to use TipTrack with OpenAI.")
        print("\nNext steps:")
        print("1. Run backend: uvicorn backend.main:app --reload")
        print("2. Run AI assistant: python mcp_server/mcp_llm_bridge.py -i")
    else:
        print("\n✗ Some tests failed. Check the errors above.")
        print("\nTroubleshooting:")
        print("- Ensure OpenAI API key is set: export OPENAI_API_KEY='sk-...'")
        print("- Ensure backend is running: uvicorn backend.main:app")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
