"""HTTP client for TipTrack FastAPI backend (used by Streamlit)."""
from typing import List, Optional

import httpx


class TipTrackAPIClient:
    """Client for TipTrack FastAPI backend."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.role: Optional[str] = None
    
    def _headers(self) -> dict:
        """Build request headers with auth token if available."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate and store token."""
        try:
            with httpx.Client() as client:
                resp = client.post(
                    f"{self.base_url}/auth/login",
                    json={"username": username, "password": password},
                    timeout=5.0,
                )
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access_token")
                self.role = data.get("role")
                return True
        except Exception:
            pass
        return False
    
    def logout(self):
        """Clear token."""
        self.token = None
        self.role = None
    
    def get_waiters(self) -> List[dict]:
        """List all waiters."""
        try:
            with httpx.Client() as client:
                resp = client.get(f"{self.base_url}/waiters", headers=self._headers(), timeout=5.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return []
    
    def get_waiter(self, waiter_id: str) -> Optional[dict]:
        """Get waiter by ID."""
        try:
            with httpx.Client() as client:
                resp = client.get(f"{self.base_url}/waiters/{waiter_id}", headers=self._headers(), timeout=5.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None
    
    def get_waiter_summary(self, waiter_id: str) -> Optional[dict]:
        """Get waiter summary (tips, rating, count)."""
        try:
            with httpx.Client() as client:
                resp = client.get(f"{self.base_url}/waiters/{waiter_id}/summary", headers=self._headers(), timeout=5.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None
    
    def create_transaction(self, waiter_id: str, amount: float, rating: int, feedback: str = "") -> Optional[dict]:
        """Create a transaction (tip + rating + feedback)."""
        try:
            with httpx.Client() as client:
                resp = client.post(
                    f"{self.base_url}/transactions",
                    json={"waiter_id": waiter_id, "amount": amount, "rating": rating, "feedback": feedback},
                    headers=self._headers(),
                    timeout=5.0,
                )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None
    
    def get_waiter_transactions(self, waiter_id: str) -> List[dict]:
        """Get all transactions for a waiter."""
        try:
            with httpx.Client() as client:
                resp = client.get(f"{self.base_url}/transactions/waiter/{waiter_id}", headers=self._headers(), timeout=5.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return []
    
    def get_waiter_insights(self, waiter_id: str) -> Optional[dict]:
        """Get AI-driven insights for a waiter."""
        try:
            with httpx.Client() as client:
                resp = client.get(f"{self.base_url}/insights/waiter/{waiter_id}", headers=self._headers(), timeout=5.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None
    
    def get_waiter_recommendations(self, waiter_id: str) -> Optional[dict]:
        """Fetch ML-based personalized recommendations for a waiter."""
        try:
            with httpx.Client() as client:
                resp = client.get(f"{self.base_url}/ml/waiter/{waiter_id}/recommendations", headers=self._headers(), timeout=10.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"Failed to fetch waiter recommendations: {e}")
        return None

    def get_owner_recommendations(self) -> Optional[dict]:
        """Fetch owner-level ML recommendations."""
        try:
            with httpx.Client() as client:
                resp = client.get(f"{self.base_url}/ml/owner/recommendations", headers=self._headers(), timeout=10.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"Failed to fetch owner recommendations: {e}")
        return None

    def list_all_transactions(self) -> List[dict]:
        """Retrieve every recorded transaction (owner/admin only)."""
        try:
            with httpx.Client() as client:
                resp = client.get(f"{self.base_url}/transactions", headers=self._headers(), timeout=10.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"Failed to list transactions: {e}")
        return []

    def get_team_insights(self) -> Optional[dict]:
        """Fetch aggregated team analytics and leaderboard."""
        try:
            with httpx.Client() as client:
                resp = client.get(f"{self.base_url}/insights/team", headers=self._headers(), timeout=10.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"Failed to fetch team insights: {e}")
        return None

    def validate_qr(self, payload_b64: str, signature: str) -> Optional[dict]:
        """Server-side validation of QR payload/signature via API."""
        try:
            with httpx.Client() as client:
                resp = client.post(
                    f"{self.base_url}/qr/validate",
                    json={"payload": payload_b64, "signature": signature},
                    headers=self._headers(),
                    timeout=5.0,
                )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"QR validation failed: {e}")
        return None

    def sign_payload(self, payload: dict) -> Optional[dict]:
        """Request server to sign a payload for QR generation (admin only)."""
        try:
            with httpx.Client() as client:
                resp = client.post(
                    f"{self.base_url}/qr/sign",
                    json=payload,
                    headers=self._headers(),
                    timeout=5.0,
                )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"QR signing failed: {e}")
        return None
    
    def create_payment_order(self, waiter_id: str, amount: float, provider: str = "razorpay") -> Optional[dict]:
        """Create a payment order for secure payment processing."""
        try:
            with httpx.Client() as client:
                resp = client.post(
                    f"{self.base_url}/payments/order",
                    json={"waiter_id": waiter_id, "amount": amount, "payment_provider": provider},
                    headers=self._headers(),
                    timeout=10.0,
                )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"Payment order creation failed: {e}")
        return None
    
    def confirm_payment(self, order_id: str, payment_id: str, signature: str) -> Optional[dict]:
        """Confirm payment via webhook (typically called by backend)."""
        try:
            with httpx.Client() as client:
                resp = client.post(
                    f"{self.base_url}/payments/webhook",
                    json={"order_id": order_id, "payment_id": payment_id, "signature": signature},
                    headers=self._headers(),
                    timeout=10.0,
                )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"Payment confirmation failed: {e}")
        return None
    
    def get_payment_status(self, payment_id: str) -> Optional[dict]:
        """Check payment status."""
        try:
            with httpx.Client() as client:
                resp = client.get(f"{self.base_url}/payments/status/{payment_id}", headers=self._headers(), timeout=5.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None


__all__ = ["TipTrackAPIClient"]
