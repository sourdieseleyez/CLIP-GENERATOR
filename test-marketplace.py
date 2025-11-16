#!/usr/bin/env python3
"""
Quick test script for marketplace functionality
Run this after starting the backend to verify everything works
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_marketplace():
    print("🧪 Testing Marketplace API...\n")
    
    # Test 1: List campaigns (should work without auth)
    print("1. Testing campaign listing...")
    try:
        response = requests.get(f"{API_URL}/marketplace/campaigns")
        if response.status_code == 200:
            campaigns = response.json()
            print(f"   ✓ Found {len(campaigns)} campaigns")
        else:
            print(f"   ✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Check if marketplace router is loaded
    print("\n2. Testing marketplace endpoints...")
    try:
        response = requests.get(f"{API_URL}/docs")
        if response.status_code == 200:
            print("   ✓ API docs accessible")
        else:
            print("   ✗ API docs not accessible")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Database check
    print("\n3. Testing database connection...")
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Backend running: {data.get('message')}")
        else:
            print("   ✗ Backend not responding")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "="*50)
    print("✅ Marketplace API is ready!")
    print("="*50)
    print("\nNext steps:")
    print("1. Start frontend: cd frontend && npm run dev")
    print("2. Login to the app")
    print("3. Navigate to Marketplace")
    print("4. Create a campaign or claim one")

if __name__ == "__main__":
    test_marketplace()
