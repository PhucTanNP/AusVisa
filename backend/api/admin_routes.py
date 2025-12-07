"""Admin API routes for user management and system administration"""
from __future__ import annotations

from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel

from services.auth import decode_token
from models.database import get_db
from services.user_service import UserService
from services.admin_service import AdminService
from models.user import UserResponse


router = APIRouter(prefix="/api/admin", tags=["admin"])


class UserStats(BaseModel):
    """Statistics about users"""
    total_users: int
    active_users: int
    pending_users: int
    suspended_users: int


class UserWithStats(BaseModel):
    """User information with session statistics"""
    id: int
    email: str
    username: str
    full_name: str | None
    role: str
    is_active: bool
    created_at: str
    updated_at: str | None
    last_login: str | None
    session_count: int


class UpdateStatusRequest(BaseModel):
    """Request to update user status"""
    is_active: bool


class UpdateRoleRequest(BaseModel):
    """Request to update user role"""
    role: str


def get_current_admin_user(
    authorization: str = Header(None),
    db: Any = Depends(get_db)
) -> Any:
    """
    Dependency to verify admin authentication
    
    Args:
        authorization: Authorization header with Bearer token
        db: Database session
        
    Returns:
        Current admin user
        
    Raises:
        HTTPException: If not authenticated or not admin
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
    
    # Check if user is admin
    if not hasattr(user, 'role') or user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user


@router.get("/users", response_model=List[UserWithStats])
def get_all_users(
    current_user: Any = Depends(get_current_admin_user),
    db: Any = Depends(get_db)
) -> List[UserWithStats]:
    """
    Get all users with statistics (admin only)
    
    Args:
        current_user: Current authenticated admin user
        db: Database session
        
    Returns:
        List of all users with stats
    """
    users = UserService.get_all_users_with_stats(db)
    
    return [
        UserWithStats(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=getattr(user, 'full_name', None),
            role=getattr(user, 'role', 'user'),
            is_active=bool(getattr(user, 'is_active', 1)),
            created_at=user.created_at.isoformat() if user.created_at else "",
            updated_at=user.updated_at.isoformat() if hasattr(user, 'updated_at') and user.updated_at else None,
            last_login=user.last_login.isoformat() if hasattr(user, 'last_login') and user.last_login else None,
            session_count=getattr(user, 'session_count', 0)
        )
        for user in users
    ]


@router.get("/stats", response_model=UserStats)
def get_user_stats(
    current_user: Any = Depends(get_current_admin_user),
    db: Any = Depends(get_db)
) -> UserStats:
    """
    Get user statistics (admin only)
    
    Args:
        current_user: Current authenticated admin user
        db: Database session
        
    Returns:
        User statistics
    """
    stats = UserService.get_user_stats(db)
    return UserStats(**stats)


@router.put("/users/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: int,
    request: UpdateStatusRequest,
    current_user: Any = Depends(get_current_admin_user),
    db: Any = Depends(get_db)
) -> UserResponse:
    """
    Update user active status (admin only)
    
    Args:
        user_id: User ID to update
        request: Status update request
        current_user: Current authenticated admin user
        db: Database session
        
    Returns:
        Updated user information
    """
    user = UserService.update_user_status(db, user_id, request.is_active)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_orm(user)


@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    request: UpdateRoleRequest,
    current_user: Any = Depends(get_current_admin_user),
    db: Any = Depends(get_db)
) -> UserResponse:
    """
    Update user role (admin only)
    
    Args:
        user_id: User ID to update
        request: Role update request
        current_user: Current authenticated admin user
        db: Database session
        
    Returns:
        Updated user information
    """
    # Validate role
    valid_roles = ['admin', 'editor', 'reviewer', 'support', 'user']
    if request.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    user = UserService.update_user_role(db, user_id, request.role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_orm(user)


@router.get("/neo4j/graph")
def get_neo4j_graph(
    current_user: Any = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Get Neo4j graph data for visualization (admin only)
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        Graph data with nodes and edges
    """
    return AdminService.get_neo4j_graph_data()


@router.get("/neo4j/stats")
def get_neo4j_stats(
    current_user: Any = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Get Neo4j graph statistics (admin only)
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        Graph statistics (node/rel counts)
    """
    return AdminService.get_neo4j_stats()
