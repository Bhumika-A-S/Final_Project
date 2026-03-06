"""FastAPI main application and routes."""
from typing import List, Dict

import os
from fastapi import Depends, FastAPI, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.auth import (
    authenticate_user,
    get_current_user,
    init_demo_users,
    create_access_token,
    hash_identifier,
    get_optional_current_user,
)
from fastapi import Request
from backend.database import Feedback, Rating, Transaction, User, Waiter, get_db, init_db
from backend.payment import RazorpayClient
from backend.recommendations import (
    generate_waiter_recommendations,
    generate_owner_recommendations,
    train_models,
)
from backend.qr import verify_payload, sign_payload
from backend.schemas import (
    AuthRequest,
    AuthToken,
    FeedbackResponse,
    InsightResponse,
    PaymentConfirmationResponse,
    PaymentOrderRequest,
    PaymentOrderResponse,
    PaymentWebhookRequest,
    RatingResponse,
    TransactionRequest,
    TransactionResponse,
    WaiterResponse,
    WaiterSummary,
    TeamInsightsResponse,
    AIQueryRequest,
    AIQueryResponse,
)

app = FastAPI(title="TipTrack API", version="1.0.0")

# CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize database and demo users."""
    init_db()
    db = next(get_db())
    init_demo_users(db)


@app.get("/")
def read_root():
    return {"message": "TipTrack  - Ai driven Application with sentiment analysis"}


# Auth routes
@app.post("/auth/login", response_model=AuthToken)
def login(req: AuthRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT bearer token."""
    user = authenticate_user(db, req.username, req.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.username, user.role)
    return AuthToken(access_token=token, role=user.role)


# Waiter routes
@app.get("/waiters", response_model=List[WaiterResponse])
def list_waiters(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all waiters (admin only)."""

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    waiters = db.query(Waiter).all()

    return [
        WaiterResponse(
            id=w.id,
            waiter_id=w.waiter_id,
            name=w.name,
            phone=w.phone
        )
        for w in waiters
    ]

@app.get("/waiters/{waiter_id}", response_model=WaiterResponse)
def get_waiter(waiter_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get waiter by waiter_id."""

    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Only admin or owner can access waiter details")

    w = db.query(Waiter).filter_by(waiter_id=waiter_id).one_or_none()

    if not w:
        raise HTTPException(status_code=404, detail="Waiter not found")

    return WaiterResponse(
        id=w.id,
        waiter_id=w.waiter_id,
        name=w.name,
        phone=w.phone
    )

# Waiter routes
@app.get("/waiters/{waiter_id}/summary", response_model=WaiterSummary)
def get_waiter_summary(
    waiter_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get waiter summary (total tips, avg rating, count)."""

    # Find waiter
    w = db.query(Waiter).filter_by(waiter_id=waiter_id).one_or_none()
    if not w:
        raise HTTPException(status_code=404, detail="Waiter not found")

    # ---------------- RBAC RULES ----------------

    # Waiters can only access their own summary
    if current_user.role == "waiter" and current_user.username != waiter_id:
        raise HTTPException(
            status_code=403,
            detail="Waiters can only access their own summary"
        )

    # Only allow waiter, owner, admin roles
    if current_user.role not in ["waiter", "owner", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized role"
        )

    # --------------------------------------------

    # Fetch transactions
    txs = db.query(Transaction).filter_by(waiter_id=w.id).all()

    if not txs:
        return WaiterSummary(
            waiter_id=waiter_id,
            total_tips=0.0,
            avg_rating=0.0,
            num_tips=0
        )

    total = sum(t.amount or 0.0 for t in txs)

    ratings = [
        t.rating.value
        for t in txs
        if t.rating and getattr(t.rating, "value", None) is not None
    ]

    avg = sum(ratings) / len(ratings) if ratings else 0.0

    return WaiterSummary(
        waiter_id=waiter_id,
        total_tips=round(total, 2),
        avg_rating=round(avg, 2),
        num_tips=len(txs)
    )


# Transaction routes
@app.post("/transactions", response_model=TransactionResponse)
def create_transaction(
    req: TransactionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    """Create a transaction (tip + rating + feedback)."""
    # Disallow staff-authenticated clients from creating customer payments/tips
    if current_user and current_user.role in ("waiter", "owner", "admin"):
        raise HTTPException(status_code=403, detail="Staff users cannot submit customer payments via this endpoint")

    # Get or create waiter
    w = db.query(Waiter).filter_by(waiter_id=req.waiter_id).one_or_none()
    if not w:
        w = Waiter(waiter_id=req.waiter_id, name=None, phone=None)
        db.add(w)
        db.flush()
    
    # Create transaction with advanced sentiment analysis
    from legacy_streamlit.sentiment import analyze_feedback_advanced
    try:
        # Use advanced LLM-based analysis (local BERT by default)
        feedback_analysis = analyze_feedback_advanced(req.feedback or "", provider="local")
        sentiment = feedback_analysis.get("sentiment", "neutral")
        tags = ",".join(feedback_analysis.get("tags", []))
    except Exception:
        # Fallback to simple sentiment
        from legacy_streamlit.sentiment import analyze_sentiment
        sentiment = analyze_sentiment(req.feedback or "", rating=req.rating)
        tags = ""
    
    # Hash customer identifier (privacy-preserving)
    cust_hash = None
    try:
        if getattr(req, "customer_id", None):
            cust_hash = hash_identifier(req.customer_id)
    except Exception:
        cust_hash = None

    tx = Transaction(waiter_id=w.id, amount=req.amount, customer_hash=cust_hash)
    db.add(tx)
    db.flush()
    
    # Add rating
    rating = Rating(transaction_id=tx.id, value=req.rating)
    db.add(rating)
    
    # Add feedback
    feedback = Feedback(transaction_id=tx.id, text=req.feedback, sentiment=sentiment)
    db.add(feedback)
    
    db.commit()
    db.refresh(tx)
    
    return TransactionResponse(
        id=tx.id,
        waiter_id=req.waiter_id,
        amount=tx.amount,
        timestamp=tx.timestamp,
        customer_hash=tx.customer_hash,
        rating=RatingResponse(id=rating.id, transaction_id=rating.transaction_id, value=rating.value),
        feedback=FeedbackResponse(id=feedback.id, transaction_id=feedback.transaction_id, text=feedback.text, sentiment=feedback.sentiment),
    )


@app.get("/transactions/waiter/{waiter_id}", response_model=List[TransactionResponse])
def get_waiter_transactions(waiter_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all transactions for a waiter."""
    w = db.query(Waiter).filter_by(waiter_id=waiter_id).one_or_none()
    if not w:
        raise HTTPException(status_code=404, detail="Waiter not found")
    if current_user.role == "waiter" and current_user.username != waiter_id:
        raise HTTPException(status_code=403, detail="Waiters can only access their own transactions")
    
    txs = db.query(Transaction).filter_by(waiter_id=w.id).all()
    return [
        TransactionResponse(
            id=t.id,
            waiter_id=waiter_id,
            amount=t.amount,
            timestamp=t.timestamp,
            rating=RatingResponse(id=t.rating.id, transaction_id=t.rating.transaction_id, value=t.rating.value) if t.rating else None,
            feedback=(FeedbackResponse(id=t.feedback.id, transaction_id=t.feedback.transaction_id, text=(t.feedback.text if current_user.role in ("waiter", "admin") else None), sentiment=t.feedback.sentiment) if t.feedback else None),
        )
        for t in txs
    ]


# Insights route
@app.get("/insights/waiter/{waiter_id}", response_model=InsightResponse)
def get_waiter_insights(
    waiter_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-driven insights for a waiter."""

    import pandas as pd
    from legacy_streamlit.sentiment import generate_insights

    # Find waiter
    w = db.query(Waiter).filter_by(waiter_id=waiter_id).one_or_none()
    if not w:
        raise HTTPException(status_code=404, detail="Waiter not found")

    # ---------------- RBAC RULES ----------------

    # Waiters can only see their own insights
    if current_user.role == "waiter" and current_user.username != waiter_id:
        raise HTTPException(
            status_code=403,
            detail="Waiters can only access their own insights"
        )

    # Only allow these roles
    if current_user.role not in ["waiter", "owner", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized role"
        )

    # --------------------------------------------

    # Build DataFrame from transactions
    txs = db.query(Transaction).filter_by(waiter_id=w.id).all()

    data = []
    for t in txs:
        data.append({
            "timestamp": t.timestamp.isoformat(),
            "waiter_id": waiter_id,
            "amount": t.amount,
            "rating": t.rating.value if t.rating else 0,
            "feedback": t.feedback.text if t.feedback else "",
            "sentiment": t.feedback.sentiment if t.feedback else "",
        })

    df = pd.DataFrame(data) if data else pd.DataFrame()

    insights = generate_insights(df, waiter_id)

    return InsightResponse(
        score=round(float(insights.get("score", 0)), 3),
        trend=insights.get("trend", "stable"),
        recommendations=insights.get("recommendations", []),
        encouragement=insights.get("encouragement", ""),
    )

    # Differential privacy: add small noise to scores for non-admin users
    try:
        import random, math

        def laplace_noise(scale: float) -> float:
            u = random.random() - 0.5
            return -scale * math.copysign(1.0, u) * math.log(1 - 2 * abs(u))

        score = float(insights.get("score", 0.0))
        # Apply noise unless admin or owner
        if current_user.role not in ("admin", "owner"):
            # epsilon determines privacy; smaller epsilon => more noise
            epsilon = 0.8
            sensitivity = 1.0
            scale = sensitivity / epsilon
            score += laplace_noise(scale)
    except Exception:
        score = insights.get("score", 0.0)

    return InsightResponse(
        score=round(float(score), 3),
        trend=insights.get("trend", "stable"),
        recommendations=insights.get("recommendations", []),
        encouragement=insights.get("encouragement", ""),
    )


# new endpoints below

@app.get("/transactions", response_model=List[TransactionResponse])
def list_all_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Admin/owner-only: list every tip/transaction in the system.

    This endpoint powers owner dashboards and any external analytics tooling.
    """
    if current_user.role not in ("admin", "owner"):
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    txs = db.query(Transaction).all()
    out = []
    for t in txs:
        waiter_code = db.query(Waiter).get(t.waiter_id).waiter_id if t.waiter_id else None
        out.append(TransactionResponse(
            id=t.id,
            waiter_id=waiter_code,
            amount=t.amount,
            timestamp=t.timestamp,
            payment_id=t.payment_id,
            payment_status=t.payment_status,
            payment_method=t.payment_method,
            customer_hash=t.customer_hash,
            rating=RatingResponse(id=t.rating.id, transaction_id=t.rating.transaction_id, value=t.rating.value) if t.rating else None,
            feedback=FeedbackResponse(id=t.feedback.id, transaction_id=t.feedback.transaction_id, text=t.feedback.text, sentiment=t.feedback.sentiment) if t.feedback else None,
        ))
    return out


@app.get("/insights/team", response_model=TeamInsightsResponse)
def get_team_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Owner/admin analytics: aggregate metrics, leaderboard, and team recommendations.

    Returns total orders, a sorted leaderboard, and the same insights produced
    by :func:`app.sentiment.generate_team_insights`.
    """
    if current_user.role not in ("admin", "owner"):
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    
    try:
        import pandas as pd
        from legacy_streamlit.sentiment import generate_team_insights

        txs = db.query(Transaction).outerjoin(Rating).outerjoin(Feedback).join(Waiter).all()
        data = []
        for t in txs:
            data.append({
                "timestamp": t.timestamp.isoformat(),
                "waiter_id": t.waiter.waiter_id,
                "amount": t.amount,
                "rating": t.rating.value if t.rating else 0,
                "feedback": t.feedback.text if t.feedback else "",
                "sentiment": t.feedback.sentiment if t.feedback else "",
            })
        df = pd.DataFrame(data) if data else pd.DataFrame()

        total_orders = int(df.shape[0])
        leaderboard = []
        if not df.empty:
            agg = (
                df.groupby("waiter_id").agg(NumTips=("rating", "count"), avg_rating=("rating", "mean")).reset_index()
            )
            waiter_map = {w.waiter_id: (w.name or f"Waiter {w.waiter_id}") for w in db.query(Waiter).all()}
            agg["name"] = agg["waiter_id"].map(waiter_map).fillna("Unknown")
            agg = agg.sort_values("NumTips", ascending=False)
            for _, row in agg.iterrows():
                leaderboard.append({
                    "waiter_id": str(row.waiter_id),
                    "name": str(row["name"]),
                    "num_tips": int(row["NumTips"]),
                    "avg_rating": float(row["avg_rating"] or 0),
                })

        team_ins = generate_team_insights(df)
        return TeamInsightsResponse(
            total_orders=total_orders,
            leaderboard=leaderboard,
            overall_score=team_ins.get("overall_score", 0),
            pct_low_ratings=team_ins.get("pct_low_ratings", 0),
            recommendations=team_ins.get("recommendations", []),
        )
    except Exception as e:
        import traceback
        print(f"ERROR in /insights/team: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)[:200]}")



@app.post("/qr/sign")
def sign_qr(payload: Dict, current_user: User = Depends(get_current_user)):
    """Admin-only: sign a payload for QR generation."""
    if not current_user or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    try:
        signed = sign_payload(payload)
        return signed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ML recommendation endpoints
@app.get("/ml/waiter/{waiter_id}/recommendations")
def ml_waiter_recommendations(waiter_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Personalized ML recommendations for a waiter."""
    # RBAC: allow waiter to fetch only their recommendations
    if current_user.role == "waiter" and current_user.username != waiter_id:
        raise HTTPException(status_code=403, detail="Waiters can only access their own recommendations")
    try:
        rec = generate_waiter_recommendations(db, waiter_id)
        return rec
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML recommendations failed: {str(e)}")


@app.get("/ml/owner/recommendations")
def ml_owner_recommendations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Owner-level ML recommendations."""

    if current_user.role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Owner or admin required")

    try:
        rec = generate_owner_recommendations(db)
        return rec
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML owner recommendations failed: {str(e)}")


# Payment routes
@app.post("/payments/order", response_model=PaymentOrderResponse)
def create_payment_order(req: PaymentOrderRequest, db: Session = Depends(get_db), current_user: User = Depends(get_optional_current_user)):
    """Create a payment order for Razorpay or Stripe.
    
    This initiates a secured payment flow. Customer completes payment,
    then webhook confirms and records the tip transaction.
    """
    # Only allow unauthenticated (customer) clients to create payment orders here
    if current_user and current_user.role in ("waiter", "owner", "admin"):
        raise HTTPException(status_code=403, detail="Staff users cannot create customer payment orders")

    try:
        if req.payment_provider.lower() == "razorpay":
            client = RazorpayClient()
            order = client.create_order(
                amount=req.amount,
                waiter_id=req.waiter_id,
                notes={"waiter_id": req.waiter_id},
            )
            return PaymentOrderResponse(
                order_id=order["id"],
                waiter_id=req.waiter_id,
                amount=req.amount,
                key_id=client.key_id,  # For frontend SDK
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported payment provider")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment order creation failed: {str(e)}")


@app.post("/payments/webhook", response_model=PaymentConfirmationResponse)
def payment_webhook(req: PaymentWebhookRequest, db: Session = Depends(get_db)):
    """Webhook endpoint for payment confirmation.
    
    Razorpay/Stripe calls this after successful payment.
    Records the transaction immutably with confirmed payment status.
    """
    try:
        client = RazorpayClient()
        
        # Verify payment signature (security check)
        if not client.verify_payment(req.order_id, req.payment_id, req.signature):
            return PaymentConfirmationResponse(
                success=False,
                message="Payment signature verification failed"
            )
        
        # Fetch payment details
        payment = client.fetch_payment(req.payment_id)
        
        if payment.get("status") != "captured":
            return PaymentConfirmationResponse(
                success=False,
                message="Payment not captured"
            )
        
        # Extract waiter_id from payment notes
        waiter_id_str = payment.get("notes", {}).get("waiter_id", "unknown")
        amount = float(payment.get("amount", 0)) / 100  # Convert from paise
        
        # Find or create waiter
        waiter = db.query(Waiter).filter_by(waiter_id=waiter_id_str).one_or_none()
        if not waiter:
            waiter = Waiter(waiter_id=waiter_id_str, name=None, phone=None)
            db.add(waiter)
            db.flush()
        
        # Create immutable transaction record
        # Hash any customer identifier present in payment notes for privacy
        cust_note = payment.get("notes", {}).get("customer_id") or payment.get("notes", {}).get("customer_hash")
        try:
            cust_hash = hash_identifier(cust_note) if cust_note else None
        except Exception:
            cust_hash = None

        tx = Transaction(
            waiter_id=waiter.id,
            amount=amount,
            payment_id=req.payment_id,
            payment_status="completed",
            payment_method="razorpay",
            customer_hash=cust_hash,
        )
        db.add(tx)
        db.flush()
        
        # Default rating (5 stars for paid transactions)
        rating = Rating(transaction_id=tx.id, value=5)
        db.add(rating)
        
        # Default feedback
        feedback = Feedback(
            transaction_id=tx.id,
            text="Thank you!",
            sentiment="positive",
        )
        db.add(feedback)
        
        db.commit()
        
        return PaymentConfirmationResponse(
            success=True,
            transaction_id=tx.id,
            message=f"Payment confirmed and tip recorded for {waiter_id_str}"
        )
    except Exception as e:
        return PaymentConfirmationResponse(
            success=False,
            message=f"Webhook processing failed: {str(e)}"
        )


@app.get("/payments/status/{payment_id}")
def get_payment_status(payment_id: str):
    """Check payment status by Razorpay payment ID."""
    try:
        client = RazorpayClient()
        payment = client.fetch_payment(payment_id)
        return {
            "payment_id": payment_id,
            "status": payment.get("status"),
            "amount": float(payment.get("amount", 0)) / 100,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@app.post("/qr/validate")
def validate_qr(payload: Dict[str, str]):
    """Validate a QR payload+signature posted from frontend (server-side verification)."""
    b64 = payload.get("payload") or payload.get("p")
    sig = payload.get("signature") or payload.get("s")
    if not b64 or not sig:
        raise HTTPException(status_code=400, detail="Missing payload or signature")
    decoded = verify_payload(b64, sig)
    if not decoded:
        raise HTTPException(status_code=400, detail="Invalid or expired QR")
    return decoded


@app.post("/ai/query", response_model=AIQueryResponse)

def ai_query(
    body: AIQueryRequest = Body(...),
    current_user: User = Depends(get_optional_current_user),
):
    """Process a natural language question via MCP/LLM and return the answer."""
    from mcp_server.mcp_llm_bridge import MCPLLMBridge

    # Allow unauthenticated customers or any staff
    try:
        bridge = MCPLLMBridge(
            backend_url=os.getenv("TIPTRACK_BACKEND_URL", "http://localhost:8000"),
            auth_token=os.getenv("TIPTRACK_MCP_TOKEN", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
        result = bridge.process_query(body.question)
        return AIQueryResponse(
            answer=result.get("answer", ""),
            tools_used=result.get("tools_used", []),
            success=result.get("success", False),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
