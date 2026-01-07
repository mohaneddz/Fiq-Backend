"""
Test script for Blog service routes.
Run this after starting the Blog service.
"""
import requests
import json

BASE_URL = "http://localhost:5003"


def test_health():
    """Test health check endpoint."""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_get_posts():
    """Test getting all posts."""
    print("\n=== Testing Get All Posts ===")
    response = requests.get(f"{BASE_URL}/posts")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return response.status_code == 200


def test_get_posts_with_pagination():
    """Test pagination."""
    print("\n=== Testing Pagination ===")
    response = requests.get(f"{BASE_URL}/posts?page=1&limit=2")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return response.status_code == 200


def test_get_posts_by_category():
    """Test filtering by category."""
    print("\n=== Testing Category Filter ===")
    response = requests.get(f"{BASE_URL}/posts?category=Recovery")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return response.status_code == 200


def test_search_posts():
    """Test search functionality."""
    print("\n=== Testing Search ===")
    response = requests.get(f"{BASE_URL}/posts?search=recovery")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return response.status_code == 200


def test_get_single_post():
    """Test getting a single post by ID."""
    print("\n=== Testing Get Single Post ===")
    # First get all posts to get an ID
    response = requests.get(f"{BASE_URL}/posts")
    if response.status_code == 200:
        data = response.json()
        if data.get('data', {}).get('posts'):
            post_id = data['data']['posts'][0]['id']
            print(f"Fetching post with ID: {post_id}")
            response = requests.get(f"{BASE_URL}/posts/{post_id}")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
    return False


def test_get_categories():
    """Test getting all categories."""
    print("\n=== Testing Get Categories ===")
    response = requests.get(f"{BASE_URL}/categories")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return response.status_code == 200


def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("BLOG SERVICE TESTS")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Get All Posts", test_get_posts),
        ("Pagination", test_get_posts_with_pagination),
        ("Category Filter", test_get_posts_by_category),
        ("Search", test_search_posts),
        ("Get Single Post", test_get_single_post),
        ("Get Categories", test_get_categories),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "PASSED" if success else "FAILED"))
        except Exception as e:
            print(f"Error: {e}")
            results.append((test_name, "ERROR"))
    
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    for test_name, result in results:
        print(f"{test_name}: {result}")


if __name__ == "__main__":
    run_all_tests()
