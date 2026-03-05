"""Simple sentiment and insights helpers for TipTrack.
Provides fallback implementations so the backend endpoints don't fail when LLM models
or advanced analysis aren't available during development.
"""
from typing import Dict, List, Any


def analyze_feedback_advanced(text: str, provider: str = "local") -> Dict[str, Any]:
    """Lightweight placeholder for advanced analysis.
    Returns a dict with `sentiment` and `tags`.
    """
    txt = (text or "").strip().lower()
    if not txt:
        return {"sentiment": "neutral", "tags": []}
    # naive rules
    if any(w in txt for w in ("great", "excellent", "love", "fantastic", "good")):
        return {"sentiment": "positive", "tags": ["praise"]}
    if any(w in txt for w in ("slow", "long", "rude", "terrible", "bad")):
        return {"sentiment": "negative", "tags": ["complaint"]}
    return {"sentiment": "neutral", "tags": []}


def analyze_sentiment(text: str, rating: int = 0) -> str:
    """Fallback sentiment based on rating first, otherwise simple keyword match."""
    if rating >= 4:
        return "positive"
    if rating <= 2:
        return "negative"
    txt = (text or "").strip().lower()
    if not txt:
        return "neutral"
    return analyze_feedback_advanced(txt).get("sentiment", "neutral")


def generate_insights(df, waiter_id: str = None) -> Dict[str, Any]:
    """Generate simple numeric score, trend and recommendations from a pandas DataFrame.
    Expects columns: timestamp (ISO), amount, rating, feedback, sentiment
    """
    try:
        import pandas as pd
    except Exception:
        return {"score": 0.0, "trend": "stable", "recommendations": [], "encouragement": ""}

    if df is None or df.empty:
        return {"score": 0.0, "trend": "stable", "recommendations": ["No data yet"], "encouragement": "Be the first to get a tip!"}

    # ensure rating numeric
    df = df.copy()
    df["rating"] = pd.to_numeric(df.get("rating", []), errors="coerce").fillna(0)
    avg_rating = float(df["rating"].mean()) if not df.empty else 0.0
    total_tips = float(df["amount"].sum()) if "amount" in df.columns else 0.0

    # simple score: normalize avg_rating (out of 5) and total tips influence
    score = (avg_rating / 5.0) * 100.0
    if total_tips > 0:
        score += min(total_tips / 10.0, 20.0)
    score = round(min(score, 100.0), 2)

    # trend: compare last 7 days avg vs previous 7 days
    trend = "stable"
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"]) if "timestamp" in df.columns else pd.to_datetime(pd.Series([]))
        now = pd.Timestamp.utcnow()
        last_week = df[df["timestamp"] >= (now - pd.Timedelta(days=7))]
        prev_week = df[(df["timestamp"] < (now - pd.Timedelta(days=7))) & (df["timestamp"] >= (now - pd.Timedelta(days=14)))]
        if not last_week.empty and not prev_week.empty:
            if last_week["rating"].mean() > prev_week["rating"].mean():
                trend = "improving"
            elif last_week["rating"].mean() < prev_week["rating"].mean():
                trend = "declining"
    except Exception:
        trend = "stable"

    recommendations: List[str] = []
    if avg_rating < 3.5:
        recommendations.append("Focus on customer interaction training to improve ratings.")
    if total_tips < 50:
        recommendations.append("Consider upselling or friendly prompts to increase tips.")
    if not recommendations:
        recommendations.append("Keep up the great work!")

    encouragement = "You're doing well—keep it up!" if score >= 60 else "Small changes can lead to better tips."

    return {"score": score, "trend": trend, "recommendations": recommendations, "encouragement": encouragement}


def generate_team_insights(df) -> Dict[str, Any]:
    """Aggregate-level insights for team dashboards."""
    try:
        import pandas as pd
    except Exception:
        return {"overall_score": 0.0, "pct_low_ratings": 0.0, "recommendations": []}

    if df is None or df.empty:
        return {"overall_score": 0.0, "pct_low_ratings": 0.0, "recommendations": ["No data available"]}

    df = df.copy()
    df["rating"] = pd.to_numeric(df.get("rating", []), errors="coerce").fillna(0)
    overall_score = float(df["rating"].mean()) / 5.0 * 100.0
    pct_low = float((df["rating"] <= 2).sum()) / float(len(df)) * 100.0
    recs = []
    if pct_low > 10:
        recs.append("Investigate training for waiters with low ratings.")
    if overall_score < 60:
        recs.append("Run a customer service workshop to boost scores.")
    if not recs:
        recs.append("Team performing well. Reward high performers.")

    return {"overall_score": round(overall_score, 2), "pct_low_ratings": round(pct_low, 2), "recommendations": recs}
