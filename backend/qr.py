"""QR signing and verification utilities for dynamic QR codes."""
from __future__ import annotations

import base64
import hmac
import json
import os
from hashlib import sha256
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional

QR_SECRET = os.getenv("QR_SECRET", "default_dev_secret_change_me")
QR_EXPIRY_HOURS = int(os.getenv("QR_EXPIRY_HOURS", "24"))


def sign_payload(payload: Dict) -> Dict[str, str]:
    """Sign a JSON payload and return base64 payload and hex signature."""
    payload_copy = payload.copy()
    # Ensure timestamp is in ISO format (UTC)
    if "ts" not in payload_copy:
        payload_copy["ts"] = datetime.now(timezone.utc).isoformat()
    raw = json.dumps(payload_copy, separators=(",", ":"), sort_keys=True).encode("utf-8")
    b64 = base64.urlsafe_b64encode(raw).decode("utf-8")
    sig = hmac.new(QR_SECRET.encode(), b64.encode(), sha256).hexdigest()
    return {"payload": b64, "signature": sig}


def verify_payload(b64: str, signature: str) -> Optional[Dict]:
    """Verify signature and expiry; return decoded payload dict if valid, else None."""
    try:
        expected = hmac.new(QR_SECRET.encode(), b64.encode(), sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            return None
        raw = base64.urlsafe_b64decode(b64.encode())
        payload = json.loads(raw.decode("utf-8"))
        # Validate timestamp
        ts = payload.get("ts")
        if ts:
            dt = datetime.fromisoformat(ts)
            now = datetime.now(timezone.utc)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if now - dt > timedelta(hours=QR_EXPIRY_HOURS):
                return None
        return payload
    except Exception:
        return None


__all__ = ["sign_payload", "verify_payload"]
