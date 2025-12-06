#!/usr/bin/env python3
"""Quick setup script for the User API."""
import os
import sys
import subprocess
from pathlib import Path

# Colors
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'


def print_section(title):
    """Print a section header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def run_command(command, description):
    """Run a command and print description."""
    print(f"\n{YELLOW}→ {description}...{RESET}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{GREEN}✓ Success{RESET}")
            return True
        else:
            print(f"{RED}✗ Failed{RESET}")
            if result.stderr:
                print(f"{RED}{result.stderr}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error: {str(e)}{RESET}")
        return False


def check_postgres():
    """Check if PostgreSQL is available."""
    print(f"\n{YELLOW}→ Checking PostgreSQL...{RESET}")
    try:
        result = subprocess.run("psql --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{GREEN}✓ PostgreSQL found: {result.stdout.strip()}{RESET}")
            return True
        else:
            print(f"{YELLOW}⚠ PostgreSQL not found in PATH{RESET}")
            print(f"{YELLOW}  Please install PostgreSQL or ensure it's in your PATH{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error checking PostgreSQL: {str(e)}{RESET}")
        return False


def check_env_file():
    """Check if .env file exists."""
    env_path = Path(".env")
    if env_path.exists():
        print(f"{GREEN}✓ .env file found{RESET}")
        return True
    else:
        print(f"{YELLOW}⚠ .env file not found{RESET}")
        print(f"{YELLOW}  Creating .env from .env.example...{RESET}")
        try:
            if Path(".env.example").exists():
                with open(".env.example", "r") as src:
                    with open(".env", "w") as dst:
                        dst.write(src.read())
                print(f"{YELLOW}  Created .env - please update it with your settings{RESET}")
                return True
            else:
                print(f"{RED}  .env.example not found{RESET}")
                return False
        except Exception as e:
            print(f"{RED}  Error creating .env: {str(e)}{RESET}")
            return False


def main():
    """Main setup function."""
    print_section("VISA User API - Quick Setup")
    
    print(f"\n{GREEN}This script will help you set up the User API.{RESET}")
    print(f"\n{YELLOW}Prerequisites:{RESET}")
    print("  • Python 3.8+")
    print("  • PostgreSQL 12+")
    print("  • pip package manager")
    
    # Check Python version
    print(f"\n{YELLOW}→ Checking Python version...{RESET}")
    version_info = sys.version_info
    if version_info.major >= 3 and version_info.minor >= 8:
        print(f"{GREEN}✓ Python {version_info.major}.{version_info.minor}.{version_info.micro}{RESET}")
    else:
        print(f"{RED}✗ Python 3.8+ required (found {version_info.major}.{version_info.minor}){RESET}")
        return False
    
    # Check PostgreSQL
    if not check_postgres():
        print(f"\n{YELLOW}⚠ PostgreSQL setup skipped - you'll need to set it up manually{RESET}")
    
    # Check/create .env file
    if not check_env_file():
        print(f"{RED}✗ Failed to create .env file{RESET}")
        return False
    
    # Install dependencies
    print_section("Installing Dependencies")
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        print(f"{RED}✗ Failed to install dependencies{RESET}")
        return False
    
    # Create database (optional)
    print_section("Database Setup")
    print(f"\n{YELLOW}To create the PostgreSQL database, run:{RESET}")
    print(f"{BLUE}  psql -U postgres -c 'CREATE DATABASE visa_db;'{RESET}")
    
    print(f"\n{YELLOW}Or use the following SQL:{RESET}")
    print(f"{BLUE}  CREATE DATABASE visa_db;{RESET}")
    
    # Summary
    print_section("Setup Complete!")
    print(f"\n{GREEN}Next steps:{RESET}")
    print(f"  1. Update .env file with your database credentials:")
    print(f"     {BLUE}DATABASE_URL=postgresql://username:password@localhost:5432/visa_db{RESET}")
    print(f"\n  2. Create PostgreSQL database (if not already created)")
    print(f"\n  3. Start the API server:")
    print(f"     {BLUE}uvicorn api.server:app --reload{RESET}")
    print(f"\n  4. Visit {BLUE}http://localhost:8000/docs{RESET} for API documentation")
    print(f"\n  5. Run tests (in another terminal):")
    print(f"     {BLUE}python test_user_api.py{RESET}")
    
    print(f"\n{GREEN}API Endpoints:{RESET}")
    print(f"  • POST   /api/users/register      - Register new user")
    print(f"  • POST   /api/users/login         - Login user")
    print(f"  • GET    /api/users/me            - Get current user")
    print(f"  • GET    /api/users               - List all users")
    print(f"  • GET    /api/users/{{id}}         - Get user by ID")
    print(f"  • PUT    /api/users/{{id}}         - Update user")
    print(f"  • DELETE /api/users/{{id}}         - Delete user")
    print(f"  • POST   /api/users/{{id}}/deactivate - Deactivate user")
    
    print(f"\n{YELLOW}For more information, see README_USER_API.md{RESET}\n")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{RED}Setup cancelled by user.{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Setup error: {str(e)}{RESET}")
        sys.exit(1)
