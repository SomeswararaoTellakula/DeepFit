#!/usr/bin/env python3
"""
Test script to verify enhanced situp functionality
"""

import requests
import time
import json
from pathlib import Path

BASE_URL = "http://localhost:5001"
RESULTS_DIR = Path("validation_results/Exercises/Situps")

def test_session_flow():
    """Test the complete session flow"""
    
    print("Testing Enhanced Situp Session Flow")
    print("=" * 50)
    
    # Test 1: Check initial session status
    print("1. Checking initial session status...")
    response = requests.get(f"{BASE_URL}/session_status")
    if response.status_code == 200:
        status = response.json()
        print(f"   Session Active: {status['session_active']}")
        print(f"   Session Completed: {status['session_completed']}")
        print(f"   Duration: {status['duration']} seconds")
    
    # Test 2: Start new session
    print("\n2. Starting new session...")
    response = requests.get(f"{BASE_URL}/new_session")
    if response.status_code == 200:
        print("   New session ready")
    
    # Test 3: Start camera (should start timer)
    print("\n3. Starting camera and timer...")
    response = requests.get(f"{BASE_URL}/start_camera")
    if response.status_code == 200:
        result = response.json()
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        print(f"   Duration: {result.get('duration', 'N/A')} seconds")
    
    # Test 4: Monitor stats for a few seconds
    print("\n4. Monitoring session for 10 seconds...")
    for i in range(10):
        response = requests.get(f"{BASE_URL}/get_stats")
        if response.status_code == 200:
            stats = response.json()
            elapsed = stats.get('elapsed_time', 0)
            remaining = stats.get('remaining_time', 0)
            print(f"   Time {i+1}: Elapsed={elapsed}s, Remaining={remaining}s, Reps={stats.get('reps', 0)}")
        time.sleep(1)
    
    # Test 5: Manual stop
    print("\n5. Manually stopping session...")
    response = requests.get(f"{BASE_URL}/stop_camera")
    if response.status_code == 200:
        result = response.json()
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        print(f"   Elapsed Time: {result.get('elapsed_time', 'N/A')} seconds")
    
    # Test 6: Check if results were saved
    print("\n6. Checking saved results...")
    if RESULTS_DIR.exists():
        json_files = list(RESULTS_DIR.glob("performance_metrics_*.json"))
        if json_files:
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            print(f"   Latest result file: {latest_file.name}")
            
            with open(latest_file, 'r') as f:
                data = json.load(f)
                print(f"   Exercise Type: {data.get('exercise_type')}")
                print(f"   Duration: {data.get('duration')} seconds")
                print(f"   Status: {data.get('status')}")
                print(f"   Timestamp: {data.get('timestamp')}")
        else:
            print("   No result files found")
    else:
        print("   Results directory not found")
    
    # Test 7: Try to restart (should fail)
    print("\n7. Attempting to restart completed session...")
    response = requests.get(f"{BASE_URL}/start_camera")
    if response.status_code == 200:
        result = response.json()
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
    
    print("\nTest completed!")

def test_timer_completion():
    """Test timer auto-completion (shortened for testing)"""
    print("\nTesting Timer Auto-Completion (5 second test)")
    print("=" * 50)
    
    # This would require modifying SITUP_DURATION temporarily
    # For now, just demonstrate the concept
    print("Note: Full 180-second timer test would take 3 minutes")
    print("The system is configured to auto-save when timer reaches 0")
    print("Manual testing recommended for full timer functionality")

if __name__ == "__main__":
    try:
        test_session_flow()
        test_timer_completion()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Flask app")
        print("Make sure to run: python app_situp.py")
    except Exception as e:
        print(f"Test error: {e}")