"""
Test script for Chat service /chat endpoint.

Tests three scenarios:
1. Drug question: "risks of fentanyl" - should call lookup_drug/rag_query
2. History question with user_id - should call lookup_history
3. Unknown drug: "Xylazine-XYZ" - should return "Drug not found" message
"""
import sys
import os
import json
import requests
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Configuration
CHAT_SERVICE_URL = os.getenv("CHAT_SERVICE_URL", "http://localhost:5001")
CHAT_ENDPOINT = f"{CHAT_SERVICE_URL}/chat"


def validate_response_schema(response: Dict[str, Any]) -> bool:
    """Validate response matches required JSON schema."""
    try:
        # Check top-level structure
        if "response" not in response:
            print("  ❌ Missing 'response' key")
            return False
        
        data = response["response"]
        
        # Check required fields
        required_fields = ["summary", "risks", "what_to_do", "safety"]
        for field in required_fields:
            if field not in data:
                print(f"  ❌ Missing field: {field}")
                return False
        
        # Validate types
        if not isinstance(data["summary"], str):
            print(f"  ❌ 'summary' is not a string")
            return False
        
        if not isinstance(data["risks"], list):
            print(f"  ❌ 'risks' is not a list")
            return False
        
        if not isinstance(data["what_to_do"], list):
            print(f"  ❌ 'what_to_do' is not a list")
            return False
        
        # Validate safety object
        safety = data["safety"]
        if not isinstance(safety, dict):
            print(f"  ❌ 'safety' is not a dict")
            return False
        
        if "urgent_signs" not in safety or not isinstance(safety["urgent_signs"], list):
            print(f"  ❌ 'safety.urgent_signs' missing or not a list")
            return False
        
        if "hotlines" not in safety or not isinstance(safety["hotlines"], list):
            print(f"  ❌ 'safety.hotlines' missing or not a list")
            return False
        
        print("  ✅ Response schema valid")
        return True
    
    except Exception as e:
        print(f"  ❌ Validation error: {e}")
        return False


def test_drug_query():
    """Test 1: Drug question - should use lookup_drug/rag_query."""
    print("\n" + "="*70)
    print("TEST 1: Drug Query - 'risks of fentanyl'")
    print("="*70)
    
    payload = {
        "message": "What are the risks of fentanyl?",
        "user_id": "test_user_123"
    }
    
    try:
        print(f"\n📤 Sending request to {CHAT_ENDPOINT}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(CHAT_ENDPOINT, json=payload, timeout=30)
        
        print(f"\n📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📋 Response preview:")
            if "data" in data and "response" in data["data"]:
                resp = data["data"]["response"]
                print(f"   Summary: {resp.get('summary', 'N/A')[:100]}...")
                print(f"   Risks count: {len(resp.get('risks', []))}")
                print(f"   What to do count: {len(resp.get('what_to_do', []))}")
                print(f"   Urgent signs count: {len(resp.get('safety', {}).get('urgent_signs', []))}")
                print(f"   Hotlines: {resp.get('safety', {}).get('hotlines', [])}")
                
                # Validate schema
                print("\n🔍 Validating response schema...")
                is_valid = validate_response_schema(data["data"])
                
                if is_valid:
                    print("\n✅ TEST 1 PASSED: Drug query returned valid JSON")
                else:
                    print("\n❌ TEST 1 FAILED: Response schema invalid")
            else:
                print("   ❌ Unexpected response structure")
                print(f"   Full response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ TEST 1 FAILED: Status {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")


def test_history_query():
    """Test 2: History question with user_id - should use lookup_history."""
    print("\n" + "="*70)
    print("TEST 2: History Query - 'summarize my progress'")
    print("="*70)
    
    payload = {
        "message": "Can you summarize my progress?",
        "user_id": "user_456"
    }
    
    try:
        print(f"\n📤 Sending request to {CHAT_ENDPOINT}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(CHAT_ENDPOINT, json=payload, timeout=30)
        
        print(f"\n📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📋 Response preview:")
            if "data" in data and "response" in data["data"]:
                resp = data["data"]["response"]
                print(f"   Summary: {resp.get('summary', 'N/A')[:100]}...")
                
                # Validate schema
                print("\n🔍 Validating response schema...")
                is_valid = validate_response_schema(data["data"])
                
                if is_valid:
                    print("\n✅ TEST 2 PASSED: History query returned valid JSON")
                else:
                    print("\n❌ TEST 2 FAILED: Response schema invalid")
            else:
                print("   ❌ Unexpected response structure")
                print(f"   Full response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ TEST 2 FAILED: Status {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")


def test_unknown_drug():
    """Test 3: Unknown drug - should return 'Drug not found' message."""
    print("\n" + "="*70)
    print("TEST 3: Unknown Drug - 'Xylazine-XYZ'")
    print("="*70)
    
    payload = {
        "message": "What are the risks of Xylazine-XYZ?",
        "user_id": "test_user_789"
    }
    
    try:
        print(f"\n📤 Sending request to {CHAT_ENDPOINT}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(CHAT_ENDPOINT, json=payload, timeout=30)
        
        print(f"\n📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📋 Response preview:")
            if "data" in data and "response" in data["data"]:
                resp = data["data"]["response"]
                summary = resp.get('summary', '')
                print(f"   Summary: {summary}")
                print(f"   Risks: {resp.get('risks', [])}")
                
                # Validate schema
                print("\n🔍 Validating response schema...")
                is_valid = validate_response_schema(data["data"])
                
                # Check for "not found" message
                not_found_detected = (
                    "not found" in summary.lower() or
                    "unable to verify" in summary.lower() or
                    "unknown" in summary.lower()
                )
                
                if is_valid and not_found_detected:
                    print("\n✅ TEST 3 PASSED: Unknown drug returned 'not found' message with valid JSON")
                elif is_valid:
                    print(f"\n⚠️  TEST 3 WARNING: Valid JSON but no 'not found' message detected")
                    print(f"   Summary: {summary}")
                else:
                    print("\n❌ TEST 3 FAILED: Response schema invalid")
            else:
                print("   ❌ Unexpected response structure")
                print(f"   Full response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ TEST 3 FAILED: Status {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("🧪 CHAT SERVICE TEST SUITE")
    print("="*70)
    print(f"Target: {CHAT_ENDPOINT}")
    print(f"Timestamp: {os.popen('echo %date% %time%').read().strip()}")
    
    # Check if service is reachable
    try:
        health_url = f"{CHAT_SERVICE_URL}/health"
        print(f"\n🔍 Checking service health: {health_url}")
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print("✅ Service is healthy")
        else:
            print(f"⚠️  Service returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach service: {e}")
        print("   Make sure the Chat service is running on the expected port.")
        return
    
    # Run tests
    test_drug_query()
    test_history_query()
    test_unknown_drug()
    
    # Summary
    print("\n" + "="*70)
    print("🎯 TEST SUITE COMPLETE")
    print("="*70)
    print("\nReview results above. Check:")
    print("  1. All responses have valid JSON schema")
    print("  2. Tool calls are logged (check logs/chat.log)")
    print("  3. Unknown drug returns 'not found' message")
    print("\n")


if __name__ == "__main__":
    main()
