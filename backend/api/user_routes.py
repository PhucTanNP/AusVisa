"""User API routes for authentication and CRUD operations."""
from __future__ import annotations

from datetime import timedelta
from typing import Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status, Header

from services.auth import create_access_token, decode_token, ACCESS_TOKEN_EXPIRE_MINUTES
from services.database import get_db
from services.user_service import UserService
from models.user import (
    UserCreate,
    UserResponse,
    LoginRequest,
    LoginResponse,
    UserUpdate,
)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Any = Depends(get_db)) -> UserResponse:
    """
    Register a new user.
    
    Args:
        user: User registration data
        db: Database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If email or username already exists
    """
    # Check if email already exists
    existing_email = UserService.get_user_by_email(db, user.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = UserService.get_user_by_username(db, user.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    try:
        # Enforce bcrypt 72-byte limit on password bytes to provide a
        # clear validation error before attempting to hash.
        if user.password:
            pw_bytes = user.password.encode("utf-8")
            if len(pw_bytes) > 72:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="password must be at most 72 bytes when encoded in UTF-8; truncate or shorten the password",
                )

        db_user = UserService.create_user(db, user)
        return UserResponse.from_orm(db_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Any = Depends(get_db)) -> LoginResponse:
    """
    Login user and return access token.
    
    Args:
        credentials: Login credentials (email and password)
        db: Database session
        
    Returns:
        Access token and user information
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user = UserService.authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user(
    authorization: str = Header(None),
    db: Any = Depends(get_db)
) -> UserResponse:
    """
    Get current authenticated user information.
    
    Args:
        authorization: Authorization header with Bearer token
        db: Database session
        
    Returns:
        Current user information
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = UserService.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Any = Depends(get_db)) -> UserResponse:
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user not found
    """
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_orm(user)


@router.get("", response_model=list[UserResponse])
def list_users(skip: int = 0, limit: int = 10, db: Any = Depends(get_db)) -> list[UserResponse]:
    """
    List all users with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of users
    """
    users = UserService.list_users(db, skip=skip, limit=limit)
    return [UserResponse.from_orm(user) for user in users]


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Any = Depends(get_db)
) -> UserResponse:
    """
    Update user information.
    
    Args:
        user_id: User ID
        user_update: User update data
        db: Database session
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If user not found or email/username already exists
    """
    try:
        user = UserService.update_user(db, user_id, user_update)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_user(user_id: str, db: Any = Depends(get_db)) -> None:
    """
    Delete a user.
    
    Args:
        user_id: User ID
        db: Database session
        
    Raises:
        HTTPException: If user not found
    """
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.post("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(user_id: str, db: Any = Depends(get_db)) -> UserResponse:
    """
    Deactivate a user account.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If user not found
    """
    user = UserService.deactivate_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_orm(user)
