from mcp.server import Server
from backend.database import SessionLocal, Waiter, Transaction

# Create MCP server
mcp = Server(
    name="TipTrack MCP Server",
    version="1.0.0"
)

@mcp.call_tool()
def get_waiter_summary(waiter_id: str):
    """Return waiter summary including tips and ratings"""

    db = SessionLocal()

    waiter = db.query(Waiter).filter(Waiter.waiter_id == waiter_id).first()
    if not waiter:
        return {"error": "Waiter not found"}

    tx = db.query(Transaction).filter(Transaction.waiter_id == waiter.id).all()

    if not tx:
        return {
            "waiter_id": waiter_id,
            "total_tips": 0,
            "avg_rating": 0,
            "num_tips": 0
        }

    total_tips = sum(t.amount for t in tx)

    ratings = [
        t.rating.value
        for t in tx
        if t.rating and getattr(t.rating, "value", None) is not None
    ]

    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    return {
        "waiter_id": waiter_id,
        "total_tips": total_tips,
        "avg_rating": avg_rating,
        "num_tips": len(tx)
    }