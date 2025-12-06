"""Example script for testing the User API."""
import requests
import json

BASE_URL = "http://localhost:8000/api/users"

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def test_register():
    """Test user registration."""
    print(f"\n{GREEN}Testing User Registration...{RESET}")
    
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    print_response("POST /api/users/register", response)
    
    return response.json() if response.status_code == 201 else None


def test_login():
    """Test user login."""
    print(f"\n{GREEN}Testing User Login...{RESET}")
    
    login_data = {
        "email": "test@example.com",
        "password": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print_response("POST /api/users/login", response)
    
    return response.json().get("access_token") if response.status_code == 200 else None


def test_get_current_user(token):
    """Test get current user."""
    print(f"\n{GREEN}Testing Get Current User...{RESET}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    print_response("GET /api/users/me", response)
    
    return response.json() if response.status_code == 200 else None


def test_list_users():
    """Test list all users."""
    print(f"\n{GREEN}Testing List All Users...{RESET}")
    
    response = requests.get(f"{BASE_URL}?skip=0&limit=10")
    print_response("GET /api/users", response)


def test_get_user_by_id(user_id):
    """Test get user by ID."""
    print(f"\n{GREEN}Testing Get User by ID...{RESET}")
    
    response = requests.get(f"{BASE_URL}/{user_id}")
    print_response(f"GET /api/users/{user_id}", response)


def test_update_user(user_id):
    """Test update user."""
    print(f"\n{GREEN}Testing Update User...{RESET}")
    
    update_data = {
        "full_name": "Updated Name",
        "username": "updateduser"
    }
    
    response = requests.put(f"{BASE_URL}/{user_id}", json=update_data)
    print_response(f"PUT /api/users/{user_id}", response)


def test_deactivate_user(user_id):
    """Test deactivate user."""
    print(f"\n{GREEN}Testing Deactivate User...{RESET}")
    
    response = requests.post(f"{BASE_URL}/{user_id}/deactivate")
    print_response(f"POST /api/users/{user_id}/deactivate", response)


def test_delete_user(user_id):
    """Test delete user."""
    print(f"\n{GREEN}Testing Delete User...{RESET}")
    
    response = requests.delete(f"{BASE_URL}/{user_id}")
    print_response(f"DELETE /api/users/{user_id}", response)


def test_error_cases():
    """Test error cases."""
    print(f"\n{RED}Testing Error Cases...{RESET}")
    
    # Test duplicate email
    print(f"\n{RED}Testing Duplicate Email...{RESET}")
    user_data = {
        "email": "test@example.com",
        "username": "anotheruser",
        "password": "123456"
    }
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    print_response("POST /api/users/register (Duplicate Email)", response)
    
    # Test invalid login
    print(f"\n{RED}Testing Invalid Login...{RESET}")
    login_data = {
        "email": "test@example.com",
        "password": "WrongPassword"
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print_response("POST /api/users/login (Invalid Password)", response)
    
    # Test missing required fields
    print(f"\n{RED}Testing Missing Required Fields...{RESET}")
    user_data = {
        "email": "another@example.com",
        "username": "anotheruser"
    }
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    print_response("POST /api/users/register (Missing Password)", response)


def main():
    """Run all tests."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}User API Testing Script{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    print(f"\n{RED}Make sure the API server is running on http://localhost:8000{RESET}")
    input("Press Enter to continue...")
    
    # Test user registration
    user = test_register()
    if not user:
        print(f"\n{RED}Registration failed. Exiting tests.{RESET}")
        return
    
    user_id = user.get("id")
    
    # Test login
    token = test_login()
    if not token:
        print(f"\n{RED}Login failed. Exiting tests.{RESET}")
        return
    
    # Test get current user
    test_get_current_user(token)
    
    # Test list users
    test_list_users()
    
    # Test get user by ID
    test_get_user_by_id(user_id)
    
    # Test update user
    test_update_user(user_id)
    
    # Test error cases
    test_error_cases()
    
    # Test deactivate user
    test_deactivate_user(user_id)
    
    # Test delete user (commented out to preserve test user)
    # test_delete_user(user_id)
    
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}Testing Complete!{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(f"\n{RED}Error: Cannot connect to the API server.{RESET}")
        print(f"{RED}Make sure the server is running on http://localhost:8000{RESET}")
    except KeyboardInterrupt:
        print(f"\n{RED}Tests interrupted by user.{RESET}")
    except Exception as e:
        print(f"\n{RED}Error: {str(e)}{RESET}")
