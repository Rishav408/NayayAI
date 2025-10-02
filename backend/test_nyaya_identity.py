#!/usr/bin/env python3
"""
Test script to verify NyayaAI identity and responses.
"""

import requests
import json

def test_nyaya_identity():
    """Test if NyayaAI responds with correct identity."""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing NyayaAI Identity")
    print("=" * 50)
    
    # Test health endpoint first
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    # Test questions to verify NyayaAI identity
    test_questions = [
        "Who are you?",
        "What is your purpose?",
        "What is defamation under Indian law?",
        "Can you explain the Indian Penal Code?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 Test {i}: {question}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={"query": question},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    answer = data["data"]["response"]
                    print(f"✅ Response received:")
                    print(f"📝 {answer[:200]}...")
                    
                    # Check if response contains NyayaAI identity markers
                    if "NyayaAI" in answer or "Indian Legal" in answer or "legal" in answer.lower():
                        print("✅ Identity markers found in response")
                    else:
                        print("⚠️ No clear identity markers found")
                else:
                    print(f"❌ API returned error: {data.get('error')}")
            else:
                print(f"❌ HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 NyayaAI Identity Test Complete")

if __name__ == "__main__":
    test_nyaya_identity()
