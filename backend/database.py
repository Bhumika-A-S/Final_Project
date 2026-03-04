"""Database setup and models for FastAPI backend."""
from datetime import datetime
from typing import Optional
from pathlib import Path

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker, relationship

# Use same DB as app/utils.py - absolute path to ensure consistency
BACKEND_DIR = Path(__file__).resolve().parent
DB_PATH = BACKEND_DIR.parent / "data" / "app.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=True)
    role = Column(String(32), nullable=False)


class Waiter(Base):
    __tablename__ = "waiters"
    id = Column(Integer, primary_key=True, index=True)
    waiter_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=True)
    phone = Column(String(32), nullable=True)
    transactions = relationship("Transaction", back_populates="waiter")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    waiter_id = Column(Integer, ForeignKey("waiters.id"), nullable=False)
    amount = Column(Float, default=0.0)
    # Optional payment/provider fields (store provider references only)
    payment_id = Column(String(128), nullable=True)
    payment_status = Column(String(64), nullable=True)
    payment_method = Column(String(64), nullable=True)
    # Privacy-preserving customer identifier (hashed)
    customer_hash = Column(String(128), nullable=True, index=True)
    waiter = relationship("Waiter", back_populates="transactions")
    rating = relationship("Rating", uselist=False, back_populates="transaction")
    feedback = relationship("Feedback", uselist=False, back_populates="transaction")


class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), unique=True, nullable=False)
    value = Column(Integer)
    transaction = relationship("Transaction", back_populates="rating")


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), unique=True, nullable=False)
    text = Column(String, nullable=True)
    sentiment = Column(String(32), nullable=True)
    transaction = relationship("Transaction", back_populates="feedback")


class SessionModel(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    """Dependency for FastAPI to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


__all__ = ["SessionLocal", "get_db", "init_db", "User", "Waiter", "Transaction", "Rating", "Feedback", "SessionModel"]
