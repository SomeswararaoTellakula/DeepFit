#!/usr/bin/env python3
"""
Test script for situp features
Tests the timer, submit, and database functionality
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def test_situp_submission():
    """Test situp result submission"""
    print("Testing situp result submission...")
    
    # Test data
    test_data = {
        'reps_completed': 25,
        'form_quality': 88,
        'timer_time': '2:45'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit_situp_result", 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Submission successful: {result}")
            return True
        else:
            print(f"✗ Submission failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error during submission: {e}")
        return False

def test_get_latest_result():
    """Test getting latest situp result"""
    print("Testing get latest result...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/get_latest_situp_result")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Retrieved result: {result}")
            return True
        else:
            print(f"✗ Retrieval failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error during retrieval: {e}")
        return False

def test_displaysitup_page():
    """Test displaysitup page accessibility"""
    print("Testing displaysitup page...")
    
    try:
        response = requests.get(f"{BASE_URL}/displaysitup")
        
        if response.status_code == 200:
            print("✓ Displaysitup page accessible")
            return True
        else:
            print(f"✗ Page access failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error accessing page: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("SITUP FEATURES TEST")
    print("=" * 50)
    
    tests = [
        test_situp_submission,
        test_get_latest_result,
        test_displaysitup_page
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print("-" * 30)
    
    print("\nTEST SUMMARY:")
    print(f"Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the Flask app is running.")

if __name__ == "__main__":
    main()