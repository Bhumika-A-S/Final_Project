"""Data models for TipTrack API."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WaiterBase(BaseModel):
    waiter_id: str
    name: Optional[str] = None
    phone: Optional[str] = None


class WaiterResponse(WaiterBase):
    id: int


class RatingBase(BaseModel):
    value: int


class RatingResponse(RatingBase):
    id: int
    transaction_id: int


class FeedbackBase(BaseModel):
    text: Optional[str] = None
    sentiment: Optional[str] = None


class FeedbackResponse(FeedbackBase):
    id: int
    transaction_id: int


class TransactionBase(BaseModel):
    waiter_id: str
    amount: float


class TransactionRequest(TransactionBase):
    rating: int
    feedback: Optional[str] = None
    customer_id: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: int
    timestamp: datetime
    payment_id: Optional[str] = None
    payment_status: str = "pending"
    payment_method: Optional[str] = None
    customer_hash: Optional[str] = None
    rating: Optional[RatingResponse] = None
    feedback: Optional[FeedbackResponse] = None


class PaymentOrderRequest(BaseModel):
    waiter_id: str
    amount: float
    payment_provider: str = "razorpay"  # razorpay or stripe


class PaymentOrderResponse(BaseModel):
    order_id: str
    waiter_id: str
    amount: float
    payment_url: Optional[str] = None
    key_id: Optional[str] = None  # For Razorpay client SDK


class PaymentWebhookRequest(BaseModel):
    order_id: str
    payment_id: str
    signature: str


class PaymentConfirmationResponse(BaseModel):
    success: bool
    transaction_id: Optional[int] = None
    message: str


class WaiterSummary(BaseModel):
    waiter_id: str
    total_tips: float
    avg_rating: float
    num_tips: int


class UserBase(BaseModel):
    username: str
    role: str


class UserResponse(UserBase):
    id: int


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class AuthRequest(BaseModel):
    username: str
    password: str


class InsightResponse(BaseModel):
    score: float
    trend: str
    recommendations: list
    encouragement: str


class LeaderboardEntry(BaseModel):
    waiter_id: str
    name: Optional[str] = None
    num_tips: int
    avg_rating: float


class TeamInsightsResponse(BaseModel):
    total_orders: int
    leaderboard: list[LeaderboardEntry]
    overall_score: float
    pct_low_ratings: float
    recommendations: list[str]


# Models for AI queries
class AIQueryRequest(BaseModel):
    question: str


class AIQueryResponse(BaseModel):
    answer: str
    tools_used: list[dict]
    success: bool


__all__ = [
    "WaiterBase",
    "WaiterResponse",
    "RatingBase",
    "RatingResponse",
    "FeedbackBase",
    "FeedbackResponse",
    "TransactionBase",
    "TransactionRequest",
    "TransactionResponse",
    "PaymentOrderRequest",
    "PaymentOrderResponse",
    "PaymentWebhookRequest",
    "PaymentConfirmationResponse",
    "WaiterSummary",
    "UserBase",
    "UserResponse",
    "AuthToken",
    "AuthRequest",
    "InsightResponse",
    "LeaderboardEntry",
    "TeamInsightsResponse",
    "AIQueryRequest",
    "AIQueryResponse",
]
