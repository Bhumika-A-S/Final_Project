"""Simple ML recommendation engine for TipTrack.

This module provides lightweight, explainable models and heuristics:
- Regression: predict tip amount from rating and hour
- Classification: predict service quality (good/bad)
- Clustering: group waiters by avg tip and avg rating
- Recommendation generation: produce short actionable tips

The implementations are intentionally small and runnable offline.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import NotFittedError
from joblib import dump, load

from backend.database import Transaction, Rating, Waiter, Feedback, get_db
from sqlalchemy.orm import Session


MODEL_DIR = "data/models"


def _ensure_model_dir():
    from pathlib import Path
    Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)


def _build_features(transactions: List[Dict]) -> (np.ndarray, np.ndarray):
    # transactions: list of dicts with keys: hour, rating, waiter_id, amount
    X = []
    y_reg = []
    y_clf = []
    for t in transactions:
        hour = t.get("hour", 0)
        rating = t.get("rating", 0)
        waiter = t.get("waiter_id", "unknown")
        amt = t.get("amount", 0.0)
        X.append([hour, rating, waiter])
        y_reg.append(amt)
        y_clf.append(1 if rating >= 4 else 0)
    return np.array(X, dtype=object), np.array(y_reg, dtype=float), np.array(y_clf, dtype=int)


def collect_transactions(db: Session) -> List[Dict]:
    rows = db.query(Transaction).outerjoin(Rating).join(Waiter).all()
    out = []
    for t in rows:
        hour = t.timestamp.hour if isinstance(t.timestamp, datetime) else 0
        rating = int(t.rating.value) if t.rating and getattr(t.rating, "value", None) is not None else 0
        out.append({"hour": hour, "rating": rating, "waiter_id": t.waiter.waiter_id, "amount": float(t.amount or 0.0)})
    return out


def train_models(db: Session) -> Dict[str, str]:
    """Train or retrain models and persist to disk. Returns paths."""
    _ensure_model_dir()
    transactions = collect_transactions(db)
    if not transactions:
        return {}
    X, y_reg, y_clf = _build_features(transactions)

    # Column transformer: hour and rating numeric, waiter_id one-hot
    preproc = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), [2]),
            ("num", "passthrough", [0, 1]),
        ],
        remainder="drop",
    )

    reg_pipe = make_pipeline(preproc, LinearRegression())
    clf_pipe = make_pipeline(preproc, RandomForestClassifier(n_estimators=50, random_state=42))

    # Fit
    reg_pipe.fit(X, y_reg)
    clf_pipe.fit(X, y_clf)

    # Clustering on waiter aggregates
    import pandas as pd
    df = pd.DataFrame(transactions)
    agg = df.groupby("waiter_id").agg(avg_tip=("amount", "mean"), avg_rating=("rating", "mean")).fillna(0)
    kmeans = KMeans(n_clusters=min(4, max(1, len(agg))), random_state=42).fit(agg.values)

    # Persist
    reg_path = f"{MODEL_DIR}/regression.joblib"
    clf_path = f"{MODEL_DIR}/classifier.joblib"
    km_path = f"{MODEL_DIR}/kmeans.joblib"
    dump(reg_pipe, reg_path)
    dump(clf_pipe, clf_path)
    dump((kmeans, agg.reset_index().to_dict(orient='records')), km_path)

    return {"regression": reg_path, "classifier": clf_path, "kmeans": km_path}


def _load_model(path: str):
    try:
        return load(path)
    except Exception:
        return None


def predict_tip(waiter_id: str, hour: int, rating: int) -> Optional[float]:
    from pathlib import Path
    reg_path = Path(MODEL_DIR) / "regression.joblib"
    if not reg_path.exists():
        return None
    model = _load_model(str(reg_path))
    if model is None:
        return None
    X = np.array([[hour, rating, waiter_id]], dtype=object)
    try:
        return float(model.predict(X)[0])
    except Exception:
        return None


def classify_quality(waiter_id: str, hour: int, rating: int) -> Optional[int]:
    from pathlib import Path
    clf_path = Path(MODEL_DIR) / "classifier.joblib"
    if not clf_path.exists():
        return None
    model = _load_model(str(clf_path))
    X = np.array([[hour, rating, waiter_id]], dtype=object)
    try:
        return int(model.predict(X)[0])
    except Exception:
        return None


def cluster_waiter(waiter_id: str) -> Optional[int]:
    from pathlib import Path
    km_path = Path(MODEL_DIR) / "kmeans.joblib"
    if not km_path.exists():
        return None
    kmeans, agg = _load_model(str(km_path))
    # find record
    rec = next((r for r in agg if r.get("waiter_id") == waiter_id), None)
    if rec is None:
        return None
    vec = [[rec.get("avg_tip", 0.0), rec.get("avg_rating", 0.0)]]
    try:
        return int(kmeans.predict(vec)[0])
    except Exception:
        return None


def generate_waiter_recommendations(db: Session, waiter_id: str) -> Dict:
    """Return personalized recommendations for a waiter."""
    # Basic stats
    df = collect_transactions(db)
    waiter_tx = [t for t in df if t.get("waiter_id") == waiter_id]
    avg_rating = float(np.mean([t.get("rating", 0) for t in waiter_tx])) if waiter_tx else 0.0
    avg_tip = float(np.mean([t.get("amount", 0.0) for t in waiter_tx])) if waiter_tx else 0.0

    # Train models if not present (lightweight)
    from pathlib import Path
    Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)

    # Simple heuristics
    tips = []
    if avg_rating < 3.5:
        tips.append("Focus on customer friendliness and communication training.")
    if avg_tip < 50:
        tips.append("Try polite upsell suggestions for higher-value items.")
    if not tips:
        tips.append("Keep up the great service — maintain consistency.")

    # Predictions
    hour = datetime.utcnow().hour
    predicted = predict_tip(waiter_id, hour, int(round(avg_rating)))
    quality = classify_quality(waiter_id, hour, int(round(avg_rating)))
    cluster = cluster_waiter(waiter_id)

    return {
        "waiter_id": waiter_id,
        "avg_rating": avg_rating,
        "avg_tip": avg_tip,
        "predicted_tip": predicted,
        "quality_label": quality,
        "cluster": cluster,
        "recommendations": tips,
    }


def generate_owner_recommendations(db: Session) -> Dict:
    """Return owner-level recommendations: staffing, training, peak hours."""
    # Aggregate by hour
    tx = db.query(Transaction).all()
    hours = {}
    for t in tx:
        h = t.timestamp.hour if isinstance(t.timestamp, datetime) else 0
        hours[h] = hours.get(h, 0) + 1
    # find peaks
    peak_hours = sorted(hours.items(), key=lambda x: x[1], reverse=True)[:3]

    # Staffing suggestion (very naive)
    suggestions = []
    if peak_hours:
        suggestions.append(f"Consider increasing staff presence during hours: {', '.join(str(h) for h,_ in peak_hours)}")

    # Training hotspots: find waiters with low avg rating
    df = collect_transactions(db)
    waiter_stats = {}
    for t in df:
        w = t.get("waiter_id")
        waiter_stats.setdefault(w, []).append(t.get("rating", 0))
    low_perf = [w for w,s in waiter_stats.items() if (sum(s)/len(s)) < 3.5]
    if low_perf:
        suggestions.append(f"Offer customer-service training for: {', '.join(low_perf)}")

    return {"peak_hours": peak_hours, "suggestions": suggestions}


__all__ = [
    "train_models",
    "generate_waiter_recommendations",
    "generate_owner_recommendations",
]
