"""Authentication utilities for FastAPI backend."""
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import os
import jwt
import hashlib
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.database import User, get_db

security = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)
# Demo credentials (same as Streamlit app)
DEMO_CREDENTIALS = {
    "owner": ("ownerpass", "owner"),
    "admin": ("adminpass", "admin"),
    "waiter1": ("waiterpass", "waiter"),
    "waiter2": ("waiterpass", "waiter"),
}

# Secret for JWT (use env var in production)
SECRET_KEY = os.environ.get("TIPTRACK_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def init_demo_users():
    db = SessionLocal()

    users = [
        ("admin", "password", "admin"),
        ("waiter1", "password", "waiter")
    ]

    for username, password, role in users:
        existing = db.query(User).filter(User.username == username).first()
        if not existing:
            hashed = pwd_context.hash(password)
            new_user = User(username=username, password_hash=hashed, role=role)
            db.add(new_user)

    db.commit()
    db.close()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check password against bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except Exception:
        return False


def authenticate_user(db: Session, username: str, password: str):

    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not pwd_context.verify(password, user.password_hash):
        return None

    return user
def create_access_token(username: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token for `username` with `role` claim."""
    to_encode = {"sub": username, "role": role}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Validate JWT bearer token and return User object."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        user = db.query(User).filter_by(username=username).one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


from fastapi import Request

def get_optional_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Attempt to return a User from Authorization header, or None if no/invalid token."""
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth:
        return None
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        user = db.query(User).filter_by(username=username).one_or_none()
        return user
    except Exception:
        return None


def hash_identifier(value: str) -> Optional[str]:
    """Deterministically hash an identifier using salted SHA256 (non-reversible).

    Uses SECRET_KEY as salt so hashes are environment-specific.
    """
    if value is None:
        return None
    h = hashlib.sha256()
    h.update(SECRET_KEY.encode())
    h.update(b":")
    h.update(value.encode())
    return h.hexdigest()
from fastapi import Depends, HTTPException, status

def require_role(allowed_roles: list):
    
    def role_checker(user = Depends(get_current_user)):
        
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )

        return user

    return role_checker

__all__ = ["init_demo_users", "verify_password", "authenticate_user", "get_current_user", "security", "create_access_token", "hash_identifier"]
