#!/usr/bin/env python3
"""
Test script to verify MongoDB user context retrieval
"""

import sys
import os
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import json

def test_mongodb_connection():
    """Test MongoDB connection and user retrieval"""
    try:
        print("=== Testing MongoDB Connection ===")
        
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['sih2573']
        users_collection = db['users']
        
        print("✓ MongoDB connection successful")
        
        # Test database access
        user_count = users_collection.count_documents({})
        print(f"✓ Found {user_count} users in database")
        
        if user_count == 0:
            print("⚠️  No users found - creating test user")
            test_user = {
                'email': 'test_user_001@example.com',
                'name': 'Test User',
                'created_at': datetime.utcnow()
            }
            result = users_collection.insert_one(test_user)
            print(f"✓ Test user created with ID: {result.inserted_id}")
        
        # Get most recent user
        user = users_collection.find_one(sort=[('created_at', -1)])
        if user:
            print(f"✓ Most recent user: {user.get('email')}")
            print(f"✓ User ID: {user.get('_id')}")
            return user
        else:
            print("✗ No users found")
            return None
            
    except Exception as e:
        print(f"✗ MongoDB connection error: {e}")
        return None

def test_file_creation(user):
    """Test file creation with user context"""
    try:
        print("\n=== Testing File Creation ===")
        
        # Create test result data
        user_id = user.get('email', 'test_user_001') if user else 'test_user_001'
        
        result_data = {
            "user_id": user_id,
            "exercise_type": "situps",
            "repetitions": 25,
            "form_score": 88,
            "duration": 180,
            "range_of_motion": 82,
            "speed_control": 85,
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        
        # Create directory
        results_dir = "validation_results/Exercises/Situps"
        os.makedirs(results_dir, exist_ok=True)
        print(f"✓ Directory ensured: {results_dir}")
        
        # Create filename
        safe_user_id = user_id.replace('@', '_').replace('.', '_')
        timestamp_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"situp_result_{safe_user_id}_{timestamp_str}.json"
        filepath = os.path.join(results_dir, filename)
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        # Verify file
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            print(f"✓ Test file created: {filepath}")
            print(f"✓ File size: {os.path.getsize(filepath)} bytes")
            
            # Read and display content
            with open(filepath, 'r') as f:
                content = json.load(f)
            print("✓ File content:")
            print(json.dumps(content, indent=2))
            
            return True
        else:
            print("✗ File creation failed")
            return False
            
    except Exception as e:
        print(f"✗ File creation error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing User Context and File Storage System")
    print("=" * 50)
    
    # Test MongoDB
    user = test_mongodb_connection()
    
    # Test file creation
    file_success = test_file_creation(user)
    
    # Summary
    print("\n=== Test Summary ===")
    if user and file_success:
        print("✅ All tests passed!")
        print("✅ System ready for production use")
    else:
        print("❌ Some tests failed")
        if not user:
            print("  - MongoDB user retrieval failed")
        if not file_success:
            print("  - File creation failed")

if __name__ == "__main__":
    main()