"""User models for database and API operations."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User model for registration."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User model for updating user information."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    """User model for API responses."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """User model stored in database."""
    id: int
    hashed_password: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    """Token payload data."""
    email: Optional[str] = None
    exp: Optional[int] = None
