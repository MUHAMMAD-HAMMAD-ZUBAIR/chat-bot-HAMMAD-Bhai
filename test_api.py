#!/usr/bin/env python3
"""
Quick test script to check if the API is working
"""

import requests
import json

def test_api():
    print("🧪 Testing HAMMAD BHAI API...")
    
    # Test the test endpoint first
    try:
        print("\n1️⃣ Testing /api/test endpoint...")
        response = requests.get("http://localhost:5000/api/test", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test endpoint working!")
            print(f"Model: {data.get('model', 'Unknown')}")
        else:
            print(f"❌ Test endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Test endpoint error: {e}")
    
    # Test the chat endpoint
    try:
        print("\n2️⃣ Testing /api/chat endpoint...")
        chat_data = {
            "message": "Hello, are you working?"
        }
        response = requests.post(
            "http://localhost:5000/api/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat endpoint working!")
            print(f"Response: {data.get('response', 'No response')[:100]}...")
        else:
            print(f"❌ Chat endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")

if __name__ == "__main__":
    test_api()
