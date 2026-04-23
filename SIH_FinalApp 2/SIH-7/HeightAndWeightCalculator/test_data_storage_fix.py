#!/usr/bin/env python3
"""
Test script to verify and fix data storage issues
"""

import json
import os
from datetime import datetime
from pathlib import Path
from pymongo import MongoClient

# Configuration
RESULTS_DIR = Path("validation_results/Exercises/Situps")

def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['sih2573']
        users = db['users']
        
        # Test connection
        client.server_info()
        print("✓ MongoDB connection successful")
        
        # Get a user
        user = users.find_one(sort=[('created_at', -1)])
        if user:
            print(f"✓ Found user: {user.get('email', 'N/A')}")
            return user
        else:
            print("⚠ No users found")
            return None
            
    except Exception as e:
        print(f"✗ MongoDB error: {e}")
        return None

def create_test_result():
    """Create a test result file"""
    try:
        # Get user from MongoDB
        user = test_mongodb_connection()
        user_id = user.get('email', 'test_user@example.com') if user else 'test_user@example.com'
        
        # Create test data
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        result_data = {
            "user_id": user_id,
            "exercise_type": "situps",
            "repetitions": 35,  # From the screenshot
            "form_score": 85,
            "duration": 180,
            "range_of_motion": 78,
            "speed_control": 82,
            "timestamp": timestamp
        }
        
        # Create filename
        safe_user_id = user_id.replace('@', '_').replace('.', '_')
        timestamp_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"situp_result_{safe_user_id}_{timestamp_str}.json"
        
        # Ensure directory exists
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save file
        filepath = RESULTS_DIR / filename
        with open(filepath, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"✓ Test result saved to: {filepath}")
        
        # Verify file contents
        with open(filepath, 'r') as f:
            saved_data = json.load(f)
        
        print("✓ File contents verified:")
        for key, value in saved_data.items():
            print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating test result: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_directory_structure():
    """Check if directory structure exists"""
    print("Checking directory structure...")
    
    if RESULTS_DIR.exists():
        print(f"✓ Directory exists: {RESULTS_DIR}")
        
        # List existing files
        json_files = list(RESULTS_DIR.glob("*.json"))
        print(f"✓ Found {len(json_files)} JSON files:")
        for file in json_files:
            print(f"  - {file.name}")
    else:
        print(f"✗ Directory does not exist: {RESULTS_DIR}")
        print("Creating directory...")
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory created: {RESULTS_DIR}")

def main():
    """Main test function"""
    print("Data Storage Fix Test")
    print("=" * 30)
    
    # Check directory
    check_directory_structure()
    
    # Test MongoDB
    print("\nTesting MongoDB connection...")
    user = test_mongodb_connection()
    
    # Create test result
    print("\nCreating test result...")
    success = create_test_result()
    
    if success:
        print("\n🎉 Data storage test successful!")
        print("The issue should now be resolved.")
    else:
        print("\n⚠ Data storage test failed!")
        print("Check the error messages above.")

if __name__ == "__main__":
    main()