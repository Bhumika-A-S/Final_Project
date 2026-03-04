#!/usr/bin/env python3
"""MCP Server for TipTrack Backend Integration.

Exposes backend endpoints as MCP tools that LLMs can call.
Implements the Model Context Protocol stdio transport.

Usage:
    python mcp_server/server.py < input.jsonl > output.jsonl
"""
import sys
import json
import traceback
import httpx
import os
from typing import Any, Dict, List, Optional

# Import tool definitions
from mcp_server.tools import MCP_TOOLS, get_tool_by_name, get_tools_for_role


# Backend API Configuration
BACKEND_URL = os.getenv("TIPTRACK_BACKEND_URL", "http://localhost:8000")
DEFAULT_TOKEN = os.getenv("TIPTRACK_MCP_TOKEN", "")  # JWT token if needed


class MCPToolExecutor:
    """Executes backend API calls based on MCP tool requests."""
    
    def __init__(self, backend_url: str = BACKEND_URL, auth_token: str = ""):
        self.backend_url = backend_url.rstrip("/")
        self.auth_token = auth_token
        self.client = httpx.Client(timeout=30.0)
    
    def _get_headers(self) -> Dict[str, str]:
        """Build request headers with auth token if available."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by calling the corresponding backend endpoint."""
        tool = get_tool_by_name(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        # Dispatch to appropriate handler
        if tool_name == "get_waiter_stats":
            return self._get_waiter_stats(args)
        elif tool_name == "get_owner_analytics":
            return self._get_owner_analytics(args)
        elif tool_name == "submit_tip":
            return self._submit_tip(args)
        elif tool_name == "get_feedback":
            return self._get_feedback(args)
        elif tool_name == "blockchain_verify":
            return self._blockchain_verify(args)
        elif tool_name == "get_waiter_insights":
            return self._get_waiter_insights(args)
        elif tool_name == "generate_business_intelligence":
            return self._generate_business_intelligence(args)
        else:
            raise ValueError(f"No handler for tool '{tool_name}'")
    
    def _get_waiter_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get waiter stats from /waiters/{waiter_id}/summary"""
        waiter_id = args.get("waiter_id")
        if not waiter_id:
            raise ValueError("waiter_id is required")
        
        url = f"{self.backend_url}/waiters/{waiter_id}/summary"
        try:
            resp = self.client.get(url, headers=self._get_headers())
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
    
    def _get_owner_analytics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get team analytics from /insights/team"""
        url = f"{self.backend_url}/insights/team"
        try:
            resp = self.client.get(url, headers=self._get_headers())
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
    
    def _submit_tip(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a tip to /transactions"""
        payload = {
            "waiter_id": args.get("waiter_id"),
            "amount": args.get("amount"),
            "rating": args.get("rating"),
            "feedback": args.get("feedback", ""),
        }
        
        url = f"{self.backend_url}/transactions"
        try:
            resp = self.client.post(url, json=payload, headers=self._get_headers())
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
    
    def _get_feedback(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get feedback from /transactions/waiter/{waiter_id}"""
        waiter_id = args.get("waiter_id")
        if not waiter_id:
            raise ValueError("waiter_id is required")
        
        url = f"{self.backend_url}/transactions/waiter/{waiter_id}"
        try:
            resp = self.client.get(url, headers=self._get_headers())
            resp.raise_for_status()
            data = resp.json()
            # Limit results
            limit = args.get("limit", 10)
            return {
                "waiter_id": waiter_id,
                "feedback_items": data[:limit] if isinstance(data, list) else []
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _blockchain_verify(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Verify QR payload from /qr/validate"""
        payload = args.get("payload")
        signature = args.get("signature")
        if not payload or not signature:
            raise ValueError("payload and signature are required")
        
        url = f"{self.backend_url}/qr/validate"
        try:
            resp = self.client.post(
                url,
                json={"payload": payload, "signature": signature},
                headers=self._get_headers()
            )
            resp.raise_for_status()
            return {"valid": True, **resp.json()}
        except Exception as e:
            return {"valid": False, "message": str(e)}
    
    def _get_waiter_insights(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI insights from /insights/waiter/{waiter_id}"""
        waiter_id = args.get("waiter_id")
        if not waiter_id:
            raise ValueError("waiter_id is required")
        
        url = f"{self.backend_url}/insights/waiter/{waiter_id}"
        try:
            resp = self.client.get(url, headers=self._get_headers())
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_business_intelligence(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate BI report by combining analytics endpoints"""
        report_type = args.get("report_type", "all")
        
        try:
            # Fetch team insights
            team_url = f"{self.backend_url}/insights/team"
            team_resp = self.client.get(team_url, headers=self._get_headers())
            team_resp.raise_for_status()
            team_data = team_resp.json()
            
            # Compile BI report
            bi_report = {
                "report_type": report_type,
                "summary": f"Team performance for {len(team_data.get('leaderboard', []))} waiters",
                "key_metrics": {
                    "total_orders": team_data.get("total_orders", 0),
                    "overall_score": team_data.get("overall_score", 0),
                    "low_ratings_pct": team_data.get("pct_low_ratings", 0),
                },
                "insights": [
                    f"Top performer: {team_data['leaderboard'][0]['name']}" if team_data.get("leaderboard") else "No data",
                ],
                "recommendations": team_data.get("recommendations", []),
                "generated_at": "2024-03-03T00:00:00Z",
            }
            return bi_report
        except Exception as e:
            return {"error": str(e)}


# Global executor instance
executor = None


def init_executor():
    """Initialize the tool executor."""
    global executor
    token = DEFAULT_TOKEN or os.getenv("TIPTRACK_TOKEN", "")
    executor = MCPToolExecutor(backend_url=BACKEND_URL, auth_token=token)


def handle_initialize() -> Dict[str, Any]:
    """Handle MCP initialize request."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {
                "listChanged": True,
            }
        },
        "serverInfo": {
            "name": "TipTrack MCP Server",
            "version": "1.0.0",
        },
    }


def handle_list_tools() -> Dict[str, Any]:
    """Handle tools/list request - return all available tools."""
    return {
        "tools": MCP_TOOLS,
    }


def handle_call_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tools/call request - execute a tool."""
    global executor
    if not executor:
        init_executor()
    
    try:
        result = executor.execute_tool(tool_name, args)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error executing '{tool_name}': {str(e)}",
                    "isError": True,
                }
            ]
        }


def handle_message(msg: dict) -> dict:
    """Route MCP messages to appropriate handlers."""
    msg_type = msg.get("type")
    
    if msg_type == "initialize":
        return handle_initialize()
    elif msg_type == "tools/list":
        return handle_list_tools()
    elif msg_type == "tools/call":
        tool_name = msg.get("params", {}).get("name")
        args = msg.get("params", {}).get("arguments", {})
        return handle_call_tool(tool_name, args)
    else:
        return {
            "type": "error",
            "message": f"Unhandled message type: {msg_type}",
        }


def main():
    """Main loop: read JSON from stdin, process, write to stdout."""
    init_executor()
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            resp = handle_message(msg)
        except json.JSONDecodeError as e:
            resp = {"type": "error", "message": f"JSON decode error: {str(e)}"}
        except Exception as e:
            resp = {
                "type": "error",
                "message": str(e),
                "trace": traceback.format_exc(),
            }
        
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
