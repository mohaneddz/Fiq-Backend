"""
Quick test script to verify both services are working.
"""
import requests
import json
import time
import sys

# Service URLs
CHAT_URL = "http://localhost:5001"
RELAPSE_URL = "http://localhost:5002"

def test_service(service_name: str, base_url: str, tests: list) -> bool:
    """Test a service with a list of endpoint tests."""
    print(f"\n{'=' * 60}")
    print(f"Testing {service_name} Service ({base_url})")
    print('=' * 60)
    
    all_passed = True
    
    for test in tests:
        method = test['method']
        endpoint = test['endpoint']
        data = test.get('data')
        expected_status = test.get('expected_status', 200)
        test_name = test['name']
        
        print(f"\n▶ {test_name}")
        print(f"  {method} {endpoint}")
        
        try:
            url = f"{base_url}{endpoint}"
            
            if method == 'GET':
                response = requests.get(url, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=10)
            else:
                print(f"  ✗ Unsupported method: {method}")
                all_passed = False
                continue
            
            # Check status code
            if response.status_code == expected_status:
                print(f"  ✓ Status: {response.status_code}")
            else:
                print(f"  ✗ Status: {response.status_code} (expected {expected_status})")
                all_passed = False
                continue
            
            # Parse and display response
            try:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"  ✓ Response: success")
                    if test.get('show_data'):
                        print(f"  Data: {json.dumps(result.get('data'), indent=2)[:200]}...")
                elif result.get('status') == 'error':
                    print(f"  ✗ Error: {result.get('error')}")
                    all_passed = False
                else:
                    print(f"  ? Unknown status: {result.get('status')}")
            except json.JSONDecodeError:
                print(f"  ✗ Invalid JSON response")
                all_passed = False
        
        except requests.exceptions.ConnectionError:
            print(f"  ✗ Connection failed - is the service running?")
            all_passed = False
            return False
        except requests.exceptions.Timeout:
            print(f"  ✗ Request timeout")
            all_passed = False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            all_passed = False
    
    return all_passed

def main():
    print("\n🧪 Backend Services Test Suite")
    print("Ensure both services are running before testing!")
    print("  Chat: python backend/Chat/run.py")
    print("  Relapse: python backend/Relapse/run.py")
    
    time.sleep(2)
    
    # Chat service tests
    chat_tests = [
        {
            'name': 'Health Check',
            'method': 'GET',
            'endpoint': '/health',
            'expected_status': 200
        },
        {
            'name': 'Drug Lookup - Oxycodone',
            'method': 'POST',
            'endpoint': '/chat/tools/drug_lookup',
            'data': {'drug_name': 'Oxycodone'},
            'expected_status': 200,
            'show_data': True
        },
        {
            'name': 'User History Lookup',
            'method': 'POST',
            'endpoint': '/chat/tools/history_lookup',
            'data': {'user_id': 'user_001'},
            'expected_status': 200,
            'show_data': True
        },
        {
            'name': 'Web Search',
            'method': 'POST',
            'endpoint': '/chat/websearch',
            'data': {'drug_name': 'Fentanyl'},
            'expected_status': 200
        }
    ]
    
    # Relapse service tests
    relapse_tests = [
        {
            'name': 'Health Check',
            'method': 'GET',
            'endpoint': '/health',
            'expected_status': 200
        },
        {
            'name': 'Train Model',
            'method': 'POST',
            'endpoint': '/relapse/train',
            'expected_status': 200,
            'show_data': True
        },
        {
            'name': 'Model Info',
            'method': 'GET',
            'endpoint': '/relapse/model/info',
            'expected_status': 200,
            'show_data': True
        },
        {
            'name': 'Feature Engineering',
            'method': 'POST',
            'endpoint': '/relapse/features',
            'data': {
                'days_clean': 30,
                'craving_scores': [2, 3, 2, 3, 2],
                'sleep_hours': [7, 8, 6.5, 7, 7.5],
                'trigger_events': [],
                'support_sessions': 2,
                'medication_adherence': {
                    'doses_taken': 10,
                    'doses_prescribed': 10
                }
            },
            'expected_status': 200,
            'show_data': True
        },
        {
            'name': 'Predict Relapse',
            'method': 'POST',
            'endpoint': '/relapse/predict',
            'data': {
                'days_clean': 35,
                'craving_scores': [3, 2, 4, 3, 2, 3, 2],
                'sleep_hours': [7, 6.5, 7, 8, 6, 7.5, 7],
                'trigger_events': [],
                'support_sessions': 3,
                'medication_adherence': {
                    'doses_taken': 13,
                    'doses_prescribed': 14
                }
            },
            'expected_status': 200,
            'show_data': True
        }
    ]
    
    # Run tests
    chat_passed = test_service("Chat", CHAT_URL, chat_tests)
    relapse_passed = test_service("Relapse", RELAPSE_URL, relapse_tests)
    
    # Summary
    print(f"\n{'=' * 60}")
    print("Test Summary")
    print('=' * 60)
    print(f"Chat Service:    {'✓ PASSED' if chat_passed else '✗ FAILED'}")
    print(f"Relapse Service: {'✓ PASSED' if relapse_passed else '✗ FAILED'}")
    print('=' * 60)
    
    if chat_passed and relapse_passed:
        print("\n🎉 All tests passed! Services are ready.")
        sys.exit(0)
    else:
        print("\n⚠ Some tests failed. Check output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
