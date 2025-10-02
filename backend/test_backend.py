#!/usr/bin/env python3
"""
Simple test script to verify the backend functionality.

This script tests the basic functionality of the backend without
requiring external dependencies like pytest.
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

def test_health_endpoint(base_url):
    """Test the health endpoint."""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_chat_endpoint(base_url):
    """Test the chat endpoint."""
    print("🔍 Testing chat endpoint...")
    try:
        payload = {
            "query": "Hello, how are you?",
            "session_id": "test_session"
        }
        response = requests.post(
            f"{base_url}/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "data" in data:
                print("✅ Chat endpoint working")
                print(f"📝 Response: {data['data']['response'][:100]}...")
                return True
            else:
                print(f"❌ Chat endpoint returned error: {data}")
                return False
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return False

def test_search_endpoint(base_url):
    """Test the search endpoint."""
    print("🔍 Testing search endpoint...")
    try:
        payload = {
            "query": "What is Python programming?",
            "search_type": "simple"
        }
        response = requests.post(
            f"{base_url}/api/search",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "data" in data:
                print("✅ Search endpoint working")
                return True
            else:
                print(f"❌ Search endpoint returned error: {data}")
                return False
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Search endpoint error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Nayay Backend Test Suite")
    print("=" * 50)
    
    # Check if server is running
    base_url = "http://localhost:5000"
    
    print(f"🌐 Testing server at: {base_url}")
    print("💡 Make sure the backend server is running before running tests!")
    print()
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    tests = [
        test_health_endpoint,
        test_chat_endpoint,
        test_search_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test(base_url):
                passed += 1
        except KeyboardInterrupt:
            print("\n⏹️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ Test error: {e}")
        
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the server logs for details.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
