"""MCP Tool Definitions for TipTrack Backend Integration.

Each tool represents a backend API endpoint exposed to LLMs via MCP.
"""

from typing import Any, Dict, List
from enum import Enum


class ToolRole(str, Enum):
    """User role context for tool authorization."""
    ADMIN = "admin"
    OWNER = "owner"
    WAITER = "waiter"
    CUSTOMER = "customer"


# Tool: Get Waiter Performance Stats
TOOL_GET_WAITER_STATS = {
    "name": "get_waiter_stats",
    "description": "Retrieve performance statistics for a specific waiter including total tips, average rating, and tip count.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "waiter_id": {
                "type": "string",
                "description": "Unique waiter identifier (e.g., W001, W002)",
            },
        },
        "required": ["waiter_id"],
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "waiter_id": {"type": "string"},
            "total_tips": {"type": "number", "description": "Sum of all tips in currency"},
            "avg_rating": {"type": "number", "description": "Average customer rating (1-5)"},
            "num_tips": {"type": "integer", "description": "Total number of transactions"},
            "trend": {"type": "string", "enum": ["improving", "stable", "declining"]},
        },
    },
    "requiredRole": ["admin", "owner", "waiter"],
}


# Tool: Get Owner Analytics (Team aggregates)
TOOL_GET_OWNER_ANALYTICS = {
    "name": "get_owner_analytics",
    "description": "Retrieve team-wide analytics including leaderboard, total orders, and overall performance metrics.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "date_range": {
                "type": "string",
                "description": "Date range filter (ISO format: YYYY-MM-DD to YYYY-MM-DD or 'last_7_days', 'last_month')",
            },
        },
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "total_orders": {"type": "integer"},
            "leaderboard": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "waiter_id": {"type": "string"},
                        "name": {"type": "string"},
                        "num_tips": {"type": "integer"},
                        "avg_rating": {"type": "number"},
                    },
                },
            },
            "overall_score": {"type": "number"},
            "pct_low_ratings": {"type": "number", "description": "Percentage of ratings < 3 stars"},
            "recommendations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Strategic recommendations for team improvement",
            },
        },
    },
    "requiredRole": ["admin", "owner"],
}


# Tool: Submit Tip + Feedback
TOOL_SUBMIT_TIP = {
    "name": "submit_tip",
    "description": "Record a customer tip along with rating and feedback for a waiter.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "waiter_id": {
                "type": "string",
                "description": "Target waiter identifier",
            },
            "amount": {
                "type": "number",
                "description": "Tip amount in currency",
            },
            "rating": {
                "type": "integer",
                "description": "Customer rating (1-5 stars)",
                "minimum": 1,
                "maximum": 5,
            },
            "feedback": {
                "type": "string",
                "description": "Customer feedback text (optional)",
            },
        },
        "required": ["waiter_id", "amount", "rating"],
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "description": "Transaction ID"},
            "waiter_id": {"type": "string"},
            "amount": {"type": "number"},
            "timestamp": {"type": "string", "description": "ISO timestamp"},
            "sentiment": {
                "type": "string",
                "enum": ["positive", "neutral", "negative"],
                "description": "AI sentiment analysis of feedback",
            },
        },
    },
    "requiredRole": ["customer"],  # Unauthenticated or customer role
}


# Tool: Get Feedback (retrieve historical feedback)
TOOL_GET_FEEDBACK = {
    "name": "get_feedback",
    "description": "Retrieve historical feedback and ratings for a specific waiter.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "waiter_id": {
                "type": "string",
                "description": "Target waiter identifier",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of feedback entries to return (default: 10)",
                "default": 10,
            },
        },
        "required": ["waiter_id"],
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "waiter_id": {"type": "string"},
            "feedback_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "rating": {"type": "integer"},
                        "text": {"type": "string"},
                        "sentiment": {"type": "string"},
                        "timestamp": {"type": "string"},
                    },
                },
            },
        },
    },
    "requiredRole": ["admin", "owner", "waiter"],
}


# Tool: Blockchain Verify (QR validation / integrity check)
TOOL_BLOCKCHAIN_VERIFY = {
    "name": "blockchain_verify",
    "description": "Verify the authenticity and integrity of a QR code payload using digital signatures (blockchain-style verification).",
    "inputSchema": {
        "type": "object",
        "properties": {
            "payload": {
                "type": "string",
                "description": "Base64-encoded QR payload",
            },
            "signature": {
                "type": "string",
                "description": "Digital signature for verification",
            },
        },
        "required": ["payload", "signature"],
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "valid": {"type": "boolean", "description": "Signature verification result"},
            "waiter_id": {"type": "string"},
            "amount": {"type": "number"},
            "timestamp": {"type": "string"},
            "message": {"type": "string"},
        },
    },
    "requiredRole": ["admin", "owner", "customer"],
}


# Tool: Get Waiter Insights (AI-driven insights)
TOOL_GET_WAITER_INSIGHTS = {
    "name": "get_waiter_insights",
    "description": "Get AI-driven insights, trend analysis, and personalized recommendations for a waiter.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "waiter_id": {
                "type": "string",
                "description": "Target waiter identifier",
            },
        },
        "required": ["waiter_id"],
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "score": {"type": "number", "description": "Overall performance score (0-100)"},
            "trend": {
                "type": "string",
                "enum": ["improving", "stable", "declining"],
            },
            "recommendations": {
                "type": "array",
                "items": {"type": "string"},
            },
            "encouragement": {"type": "string", "description": "Motivational message"},
        },
    },
    "requiredRole": ["admin", "owner", "waiter"],
}


# Tool: Generate Business Intelligence
TOOL_GENERATE_BI = {
    "name": "generate_business_intelligence",
    "description": "Generate comprehensive business intelligence report combining sales trends, team performance, customer sentiment, and strategic recommendations.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "report_type": {
                "type": "string",
                "enum": ["performance", "sentiment", "forecast", "all"],
                "description": "Type of BI report to generate",
            },
        },
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "report_type": {"type": "string"},
            "summary": {"type": "string"},
            "key_metrics": {"type": "object"},
            "insights": {
                "type": "array",
                "items": {"type": "string"},
            },
            "recommendations": {
                "type": "array",
                "items": {"type": "string"},
            },
            "generated_at": {"type": "string"},
        },
    },
    "requiredRole": ["admin", "owner"],
}


# MCP Tool Registry
MCP_TOOLS = [
    TOOL_GET_WAITER_STATS,
    TOOL_GET_OWNER_ANALYTICS,
    TOOL_SUBMIT_TIP,
    TOOL_GET_FEEDBACK,
    TOOL_BLOCKCHAIN_VERIFY,
    TOOL_GET_WAITER_INSIGHTS,
    TOOL_GENERATE_BI,
]


def get_tools_for_role(role: str) -> List[Dict[str, Any]]:
    """Filter tools based on user role and return authorized tools."""
    return [
        tool for tool in MCP_TOOLS
        if role in tool.get("requiredRole", [])
    ]


def get_tool_by_name(tool_name: str) -> Dict[str, Any] | None:
    """Lookup a single tool by name."""
    for tool in MCP_TOOLS:
        if tool["name"] == tool_name:
            return tool
    return None
