"""Payment integration module for Razorpay and Stripe."""

import hashlib
import hmac
import os
from typing import Dict, Optional

import requests


class RazorpayClient:
    """Razorpay payment client."""

    def __init__(self, key_id: Optional[str] = None, key_secret: Optional[str] = None):
        """Initialize Razorpay client with API credentials."""
        self.key_id = key_id or os.getenv("RAZORPAY_KEY_ID")
        self.key_secret = key_secret or os.getenv("RAZORPAY_KEY_SECRET")
        self.base_url = "https://api.razorpay.com/v1"

        if not self.key_id or not self.key_secret:
            raise ValueError("Razorpay credentials not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.")

    def create_order(
        self, amount: float, waiter_id: str, currency: str = "INR", notes: Optional[Dict] = None
    ) -> Dict:
        """Create a Razorpay order for the tip amount."""
        # Amount in smallest currency unit (paise for INR)
        amount_paise = int(amount * 100)

        payload = {
            "amount": amount_paise,
            "currency": currency,
            "notes": notes or {"waiter_id": waiter_id},
        }

        try:
            response = requests.post(
                f"{self.base_url}/orders",
                json=payload,
                auth=(self.key_id, self.key_secret),
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to create Razorpay order: {str(e)}") from e

    def verify_payment(self, order_id: str, payment_id: str, signature: str) -> bool:
        """Verify payment signature from webhook."""
        data = f"{order_id}|{payment_id}"
        generated_signature = hmac.new(
            self.key_secret.encode(), data.encode(), hashlib.sha256
        ).hexdigest()
        return generated_signature == signature

    def fetch_payment(self, payment_id: str) -> Dict:
        """Fetch payment details from Razorpay."""
        try:
            response = requests.get(
                f"{self.base_url}/payments/{payment_id}",
                auth=(self.key_id, self.key_secret),
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch payment details: {str(e)}") from e


class StripeClient:
    """Stripe payment client (alternative to Razorpay)."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Stripe client with API key."""
        try:
            import stripe

            self.stripe = stripe
        except ImportError:
            raise ImportError("stripe package required. Install: pip install stripe")

        self.api_key = api_key or os.getenv("STRIPE_API_KEY")
        if not self.api_key:
            raise ValueError("Stripe API key not configured. Set STRIPE_API_KEY.")

        stripe.api_key = self.api_key

    def create_checkout_session(self, amount: float, waiter_id: str, return_url: str) -> Dict:
        """Create a Stripe checkout session."""
        try:
            session = self.stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "inr",
                            "product_data": {"name": f"Tip for {waiter_id}"},
                            "unit_amount": int(amount * 100),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=f"{return_url}?status=success&session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{return_url}?status=cancel",
                metadata={"waiter_id": waiter_id},
            )
            return {"session_id": session.id, "url": session.url}
        except Exception as e:
            raise RuntimeError(f"Failed to create Stripe session: {str(e)}") from e

    def retrieve_session(self, session_id: str) -> Dict:
        """Retrieve checkout session details."""
        try:
            return self.stripe.checkout.Session.retrieve(session_id).__dict__
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve session: {str(e)}") from e


# Default provider: Razorpay
def get_payment_client(provider: str = "razorpay") -> RazorpayClient | StripeClient:
    """Get payment client instance."""
    if provider.lower() == "stripe":
        return StripeClient()
    else:
        return RazorpayClient()
