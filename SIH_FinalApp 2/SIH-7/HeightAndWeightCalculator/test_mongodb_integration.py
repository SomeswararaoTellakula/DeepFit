#!/usr/bin/env python3
"""
Test script to verify MongoDB integration and user data retrieval
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_system import MongoDBManager, IntegratedHeightWeightSystem

def test_mongodb_integration():
    """Test MongoDB integration and user data retrieval"""
    
    print("Testing MongoDB Integration")
    print("=" * 50)
    
    # Test MongoDB connection
    mongo_manager = MongoDBManager()
    
    if not mongo_manager.client:
        print("ERROR: MongoDB connection failed")
        return False
    
    print("OK: MongoDB connection successful")
    
    # Test user retrieval (using the email from the active file)
    test_email = "afridpasha1976@gmail.com"
    
    print(f"Testing user retrieval for: {test_email}")
    user = mongo_manager.get_user_by_email(test_email)
    
    if user:
        print("OK: User found in database")
        print(f"   Name: {user.get('name', 'N/A')}")
        print(f"   Age: {user.get('age', 'N/A')}")
        print(f"   Gender: {user.get('gender', 'N/A')}")
        print(f"   Email: {user.get('email', 'N/A')}")
        
        # Test integrated system initialization with user email
        print(f"\nTesting integrated system with user email...")
        try:
            system = IntegratedHeightWeightSystem(
                use_gpu=False,  # Disable GPU for testing
                user_email=test_email
            )
            
            if system.current_user_data:
                print("OK: User data retrieved successfully")
                print(f"   User ID: {system.current_user_data.get('user_id')}")
                print(f"   Age: {system.current_user_data.get('age')}")
                print(f"   Gender: {system.current_user_data.get('gender')}")
                print(f"   Name: {system.current_user_data.get('name')}")
            else:
                print("ERROR: No user data retrieved")
                return False
                
        except Exception as e:
            print(f"ERROR: Failed to initialize system: {e}")
            return False
    else:
        print("ERROR: User not found in database")
        print("Make sure the user exists in MongoDB")
        return False
    
    print("\nMongoDB integration test completed successfully!")
    return True

def test_anonymous_mode():
    """Test system without user authentication"""
    
    print("\nTesting Anonymous Mode")
    print("=" * 30)
    
    try:
        system = IntegratedHeightWeightSystem(
            use_gpu=False,
            user_email=None
        )
        
        if system.current_user_data is None:
            print("OK: Anonymous mode working correctly")
        else:
            print("ERROR: Should be in anonymous mode")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to initialize anonymous mode: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_mongodb_integration()
    success = test_anonymous_mode() and success
    
    if success:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed!")
        sys.exit(1)