"""
Security utilities for authentication and authorization.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password[:72], hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash (bcrypt 72-byte limit enforced)."""
    # bcrypt truncates after 72 bytes; truncate preemptively for consistency
    truncated = password[:72]
    return pwd_context.hash(truncated)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Payload to encode in token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current authenticated user from token.

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        User information from token

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = decode_token(token)

    user_id: str = payload.get("sub")
    role: str = payload.get("role")

    if user_id is None or role is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": user_id,
        "role": role,
        "session_id": payload.get("session_id"),
    }


async def require_physician(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require physician role for endpoint access.

    Args:
        current_user: Current authenticated user

    Returns:
        User information if physician

    Raises:
        HTTPException: If user is not a physician
    """
    if current_user["role"] != "physician":
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: physician role required"
        )

    return current_user


async def require_patient(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require patient role for endpoint access.

    Args:
        current_user: Current authenticated user

    Returns:
        User information if patient

    Raises:
        HTTPException: If user is not a patient
    """
    if current_user["role"] != "patient":
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: patient role required"
        )

    return current_user


def verify_session_ownership(session_id: str, current_user: Dict[str, Any]) -> None:
    """
    Verify that the current user owns the session.

    Args:
        session_id: Session ID to verify
        current_user: Current authenticated user

    Raises:
        HTTPException: If user doesn't own the session
    """
    if current_user["role"] == "patient" and current_user.get("session_id") != session_id:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: you can only access your own session"
        )
