"""Utility functions for TipTrack - wrapper around backend database."""
from datetime import datetime
from backend.database import (
    SessionLocal,
    Base,
    engine,
    Waiter,
    Transaction,
    Rating,
    Feedback,
)


def create_db_if_missing():
    """Create all database tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def append_tip(waiter_id: str, amount: float, rating: int, feedback_text: str, sentiment: str):
    """Add a tip transaction with rating and feedback for a waiter."""
    db = SessionLocal()
    try:
        # Find waiter by waiter_id
        waiter = db.query(Waiter).filter_by(waiter_id=waiter_id).one_or_none()
        if not waiter:
            return None

        # Create transaction
        transaction = Transaction(
            waiter_id=waiter.id,
            amount=amount,
            timestamp=datetime.utcnow(),
            payment_status="completed",
            payment_method="cash",
        )
        db.add(transaction)
        db.flush()  # Flush to get transaction.id

        # Create rating
        rating_obj = Rating(transaction_id=transaction.id, value=rating)
        db.add(rating_obj)

        # Create feedback
        feedback_obj = Feedback(
            transaction_id=transaction.id,
            text=feedback_text,
            sentiment=sentiment,
        )
        db.add(feedback_obj)

        db.commit()
        return transaction
    except Exception as e:
        db.rollback()
        print(f"Error appending tip: {e}")
        return None
    finally:
        db.close()


# Re-export for convenience
__all__ = [
    "SessionLocal",
    "Base",
    "engine",
    "Waiter",
    "Transaction",
    "Rating",
    "Feedback",
    "create_db_if_missing",
    "append_tip",
]
