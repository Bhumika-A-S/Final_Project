"""OpenAI Integration Guide for TipTrack MCP

Quick Start:

1. Install dependencies:
   pip install -r requirements.txt

2. Set up environment variables:
   export OPENAI_API_KEY="your-openai-key"
   export TIPTRACK_BACKEND_URL="http://localhost:8000"

3. Start the backend:
   uvicorn backend.main:app --reload

4. Use the AI assistant:

   Option A - Interactive mode:
   python mcp_server/mcp_llm_bridge.py -i
   
   Option B - Single query:
   python mcp_server/mcp_llm_bridge.py "What is waiter W001's performance?"
   
   Option C - Python module:
   from mcp_server.mcp_llm_bridge import MCPLLMBridge
   bridge = MCPLLMBridge()
   result = bridge.process_query("Show team leaderboard")
   print(result['answer'])


Architecture:

┌─────────────────────────────────────────────────────────┐
│                 OpenAI Function Calling API              │
│              (gpt-4o-mini, gpt-4o, gpt-4, etc)          │
└──────────────────┬──────────────────────────────────────┘
                   │ (natural language + tools)
                   │
         ┌─────────▼──────────┐
         │  TipTrackLLMClient  │  (llm_client.py)
         │  (OpenAI wrapper)   │
         └─────────┬──────────┘
                   │ (tool execution requests)
                   │
         ┌─────────▼──────────────┐
         │  MCPToolExecutor       │  (server.py)
         │  (Backend API calls)   │
         └─────────┬──────────────┘
                   │ (HTTP requests)
                   │
         ┌─────────▼──────────────┐
         │  TipTrack FastAPI      │  (backend/main.py)
         │  Backend (port 8000)   │
         └────────────────────────┘


Usage Examples:

1. Get waiter performance insights:
   "What is waiter W001's total tips and average rating?"
   
   → MCPToolExecutor.execute_tool("get_waiter_stats", {"waiter_id": "W001"})
   → Calls /waiters/W001/summary endpoint
   → Returns structured performance data
   → LLM synthesizes human-friendly response

2. Generate business report:
   "Generate a business intelligence report for this month"
   
   → MCPToolExecutor.execute_tool("generate_business_intelligence", {...})
   → Calls /insights/team endpoint
   → Aggregates metrics and recommendations
   → LLM creates executive summary

3. Process customer feedback:
   "What are customers saying about waiter W002?"
   
   → MCPToolExecutor.execute_tool("get_feedback", {"waiter_id": "W002"})
   → Calls /transactions/waiter/W002 endpoint
   → Returns sentiment analysis of feedback
   → LLM identifies themes and improvements

4. Multi-step analysis with tool chaining:
   "Who is the top performer and what advice would you give them?"
   
   → First call: get_owner_analytics (leaderboard)
   → Second call: get_waiter_insights (for top performer)
   → LLM combines results into actionable advice


Authentication & Security:

- Backend API uses JWT tokens for auth
- Set TIPTRACK_MCP_TOKEN to pass auth token to backend
- OpenAI API key required: OPENAI_API_KEY
- All tool calls validated against role-based access control


Cost Optimization:

- Default model: gpt-4o-mini ($0.00015/1K input, $0.0006/1K output)
- Alternatives: 
  - gpt-4o ($0.003/1K input, $0.006/1K output)  
  - gpt-4-turbo ($0.01/1K input, $0.03/1K output)

Use gpt-4o-mini for demos, production queries, or batch processing.
Use gpt-4o for complex multi-step reasoning.


Environment Setup:

```bash
# macOS/Linux:
export OPENAI_API_KEY="sk-..."
export TIPTRACK_BACKEND_URL="http://localhost:8000"

# Windows PowerShell:
$env:OPENAI_API_KEY="sk-..."
$env:TIPTRACK_BACKEND_URL="http://localhost:8000"

# Or use .env file (install python-dotenv):
pip install python-dotenv
```

Then create .env file:
```
OPENAI_API_KEY=sk-...
TIPTRACK_BACKEND_URL=http://localhost:8000
TIPTRACK_MCP_TOKEN=your-jwt-token  # Optional
```


Troubleshooting:

1. "OPENAI_API_KEY not set"
   → export OPENAI_API_KEY="your-key" or use --api-key flag

2. "Connection refused" (backend not running)
   → Run: uvicorn backend.main:app --reload

3. "401 Unauthorized" from backend
   → Set valid JWT token: export TIPTRACK_MCP_TOKEN="your-token"

4. Tool execution errors
   → Check backend logs with: tail -f backend.log
   → Verify waiter_id exists in database


IEEE Academic Value:

This implementation demonstrates:
✓ Multi-agent AI systems with tool calling
✓ Control plane architecture (MCP server as I/O layer)
✓ Role-based access control in AI agents  
✓ Privacy-preserving queries (differential privacy in backend)
✓ Semantic understanding + structured tool invocation
✓ Enterprise-grade business intelligence APIs

Paper angles:
- "Tool-Augmented LLM Agents for Business Intelligence"
- "Secure Multi-Role Orchestration in Hospitality AI Systems"
- "Context-Aware Decision Support via Model Context Protocol"
"""
