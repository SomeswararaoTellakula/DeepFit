#!/usr/bin/env python3
"""
Test script to verify enhanced situp functionality with MongoDB integration
"""

import requests
import time
import json
from pathlib import Path
from pymongo import MongoClient

BASE_URL = "http://localhost:5001"
RESULTS_DIR = Path("validation_results/Exercises/Situps")

def test_mongodb_connection():
    """Test MongoDB connection and user retrieval"""
    print("Testing MongoDB Connection")
    print("-" * 30)
    
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['sih2573']
        users = db['users']
        
        # Test connection
        client.server_info()
        print("✓ MongoDB connection successful")
        
        # Check for users
        user_count = users.count_documents({})
        print(f"✓ Found {user_count} users in database")
        
        if user_count > 0:
            latest_user = users.find_one(sort=[('created_at', -1)])
            print(f"✓ Latest user: {latest_user.get('email', 'N/A')}")
            return True
        else:
            print("⚠ No users found in database")
            return False
            
    except Exception as e:
        print(f"✗ MongoDB error: {e}")
        return False

def test_enhanced_session():
    """Test enhanced session with timer and user data"""
    print("\nTesting Enhanced Session Flow")
    print("-" * 30)
    
    # Start new session
    response = requests.get(f"{BASE_URL}/new_session")
    if response.status_code == 200:
        print("✓ New session initialized")
    
    # Start camera (should start timer)
    response = requests.get(f"{BASE_URL}/start_camera")
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Camera started: {result['message']}")
    
    # Monitor for 5 seconds
    print("✓ Monitoring session for 5 seconds...")
    for i in range(5):
        response = requests.get(f"{BASE_URL}/get_stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"  Time {i+1}: Remaining={stats.get('remaining_time', 'N/A')}s")
        time.sleep(1)
    
    # Stop session
    response = requests.get(f"{BASE_URL}/stop_camera")
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Session stopped: {result['message']}")
    
    return True

def test_result_storage():
    """Test result storage with user data"""
    print("\nTesting Result Storage")
    print("-" * 30)
    
    if not RESULTS_DIR.exists():
        print("✗ Results directory not found")
        return False
    
    # Find latest result file
    json_files = list(RESULTS_DIR.glob("situp_result_*.json"))
    if not json_files:
        print("✗ No result files found")
        return False
    
    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
    print(f"✓ Latest result file: {latest_file.name}")
    
    # Verify JSON structure
    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        required_fields = ['user_id', 'exercise_type', 'repetitions', 'form_score', 
                          'duration', 'range_of_motion', 'speed_control', 'timestamp']
        
        for field in required_fields:
            if field in data:
                print(f"✓ {field}: {data[field]}")
            else:
                print(f"✗ Missing field: {field}")
                return False
        
        # Verify timestamp format
        timestamp = data['timestamp']
        if timestamp.endswith('Z') and 'T' in timestamp:
            print("✓ Timestamp format is ISO-8601 UTC")
        else:
            print(f"⚠ Timestamp format may be incorrect: {timestamp}")
        
        # Verify user_id is not hardcoded
        if data['user_id'] != 'test_user_001' and data['user_id'] != 'unknown_user':
            print("✓ User ID appears to be fetched from MongoDB")
        else:
            print("⚠ User ID may be hardcoded or fallback value")
        
        return True
        
    except Exception as e:
        print(f"✗ Error reading result file: {e}")
        return False

def main():
    """Run all tests"""
    print("Enhanced Situp Functionality Test")
    print("=" * 50)
    
    # Test MongoDB
    mongodb_ok = test_mongodb_connection()
    
    # Test session flow
    session_ok = test_enhanced_session()
    
    # Test result storage
    storage_ok = test_result_storage()
    
    print("\nTest Summary")
    print("-" * 20)
    print(f"MongoDB Connection: {'✓' if mongodb_ok else '✗'}")
    print(f"Session Flow: {'✓' if session_ok else '✗'}")
    print(f"Result Storage: {'✓' if storage_ok else '✗'}")
    
    if mongodb_ok and session_ok and storage_ok:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠ Some tests failed - check implementation")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Flask app")
        print("Make sure to run: python app_situp.py")
    except Exception as e:
        print(f"Test error: {e}")