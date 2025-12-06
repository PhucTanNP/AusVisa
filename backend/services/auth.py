"""Utility functions for password hashing and JWT token management."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from passlib.context import CryptContext
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from dotenv import load_dotenv

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    # Bcrypt has a 72-byte input limit. Truncate UTF-8 bytes safely to avoid
    # underlying bcrypt errors when callers provide long passwords.
    b = password.encode("utf-8")
    if len(b) > 72:
        # Truncate bytes and decode ignoring incomplete characters at the end.
        password = b[:72].decode("utf-8", errors="ignore")
    try:
        return pwd_context.hash(password)
    except AttributeError as e:
        # Passlib internal bcrypt backend error (e.g. broken/incorrect 'bcrypt' package)
        raise RuntimeError(
            "bcrypt backend error: the 'bcrypt' dependency appears broken or missing. "
            "Install the correct package with `pip install bcrypt` (or `pip install passlib[bcrypt]`)."
        ) from e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    # Ensure we apply the same truncation rule as when hashing so verification
    # behaves consistently for passwords longer than 72 bytes.
    b = plain_password.encode("utf-8")
    if len(b) > 72:
        plain_password = b[:72].decode("utf-8", errors="ignore")
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except AttributeError as e:
        raise RuntimeError(
            "bcrypt backend error during password verification: the 'bcrypt' dependency appears broken or missing. "
            "Install the correct package with `pip install bcrypt` (or `pip install passlib[bcrypt]`)."
        ) from e


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token data or None if invalid/expired
    """
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except (ExpiredSignatureError, InvalidTokenError):
        return None
