"""User service for database operations (CRUD) using SQLAlchemy."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import User
from .auth import hash_password, verify_password
from models.user import UserCreate, UserUpdate


class UserService:
    """Service class for user-related database operations (SQLAlchemy)."""

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        # Check duplicates
        existing = db.execute(select(User).filter_by(email=user.email)).scalar_one_or_none()
        if existing:
            raise ValueError("Email already exists")
        existing = db.execute(select(User).filter_by(username=user.username)).scalar_one_or_none()
        if existing:
            raise ValueError("Username already exists")

        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hash_password(user.password),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.execute(select(User).filter_by(email=email)).scalar_one_or_none()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.execute(select(User).filter_by(username=username)).scalar_one_or_none()

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        try:
            uid = int(user_id)
        except Exception:
            return None
        return db.get(User, uid)

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def update_user(db: Session, user_id: str, user_update: UserUpdate) -> Optional[User]:
        try:
            uid = int(user_id)
        except Exception:
            return None
        user = db.get(User, uid)
        if not user:
            return None

        # Duplicates
        if user_update.email and user_update.email != user.email:
            existing = db.execute(select(User).filter_by(email=user_update.email)).scalar_one_or_none()
            if existing and existing.id != user.id:
                raise ValueError("Email already exists")
        if user_update.username and user_update.username != user.username:
            existing = db.execute(select(User).filter_by(username=user_update.username)).scalar_one_or_none()
            if existing and existing.id != user.id:
                raise ValueError("Username already exists")

        if user_update.email:
            user.email = user_update.email
        if user_update.username:
            user.username = user_update.username
        if user_update.full_name:
            user.full_name = user_update.full_name
        if user_update.password:
            user.hashed_password = hash_password(user_update.password)

        user.updated_at = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        try:
            uid = int(user_id)
        except Exception:
            return False
        user = db.get(User, uid)
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 10) -> list[User]:
        stmt = select(User).offset(skip).limit(limit)
        result = db.execute(stmt).scalars().all()
        return result

    @staticmethod
    def deactivate_user(db: Session, user_id: str) -> Optional[User]:
        try:
            uid = int(user_id)
        except Exception:
            return None
        user = db.get(User, uid)
        if not user:
            return None
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
