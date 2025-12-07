"""
Initialize PostgreSQL database and create admin user
Run this after starting docker-compose
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.database import init_db, SessionLocal, User
from services.auth import hash_password
from datetime import datetime


def create_admin_user(email: str, username: str, password: str, full_name: str = "Administrator"):
    """Create an admin user"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"⚠️  User with email {email} already exists!")
            
            # Update to admin if not already
            if existing_user.role != 'admin':
                existing_user.role = 'admin'
                db.commit()
                print(f"✓ Updated {email} to admin role")
            else:
                print(f"✓ {email} is already an admin")
            return existing_user
        
        # Create new admin user
        admin_user = User(
            email=email,
            username=username,
            full_name=full_name,
            password_hash=hash_password(password),
            role='admin',
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            session_count=0
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"\n✓ Admin user created successfully!")
        print(f"  Email: {email}")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print(f"  ⚠️  IMPORTANT: Change this password after first login!")
        
        return admin_user
        
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    print("=" * 60)
    print("AusVisa Database Initialization")
    print("=" * 60)
    
    # Initialize database tables
    print("\n1. Creating database tables...")
    try:
        init_db()
        print("✓ Database tables created successfully!")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return
    
    # Create admin user
    print("\n2. Creating admin user...")
    
    # Default admin credentials
    admin_email = "admin@ausvisa.ai"
    admin_username = "admin"
    admin_password = "admin123"
    admin_fullname = "Administrator"
    
    # Ask if user wants custom credentials
    custom = input("\nUse default admin credentials? (y/n) [y]: ").strip().lower()
    
    if custom == 'n':
        admin_email = input("Enter admin email: ").strip()
        admin_username = input("Enter admin username: ").strip()
        admin_password = input("Enter admin password: ").strip()
        admin_fullname = input("Enter admin full name [Administrator]: ").strip() or "Administrator"
    
    create_admin_user(admin_email, admin_username, admin_password, admin_fullname)
    
    print("\n" + "=" * 60)
    print("✓ Database initialization complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start the backend server: python -m api.server")
    print("2. Access pgAdmin at: http://localhost:5050")
    print("3. Login to frontend and test admin page")
    print("\n")


if __name__ == "__main__":
    main()
