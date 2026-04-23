#!/usr/bin/env python3
"""
Setup script to create test users in MongoDB for situp exercise testing
"""

from pymongo import MongoClient
from datetime import datetime
import sys

def setup_test_users():
    """Create test users in MongoDB"""
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['sih2573']
        users_collection = db['users']
        
        print("✓ Connected to MongoDB")
        
        # Test users to create
        test_users = [
            {
                'email': 'test_user_001@example.com',
                'name': 'Test User 001',
                'age': 25,
                'gender': 'male',
                'created_at': datetime.utcnow()
            },
            {
                'email': 'demo_user@fitness.com',
                'name': 'Demo Fitness User',
                'age': 30,
                'gender': 'female',
                'created_at': datetime.utcnow()
            }
        ]
        
        for user_data in test_users:
            # Check if user already exists
            existing = users_collection.find_one({'email': user_data['email']})
            if existing:
                print(f"⚠️  User {user_data['email']} already exists")
            else:
                result = users_collection.insert_one(user_data)
                print(f"✓ Created user: {user_data['email']} (ID: {result.inserted_id})")
        
        # Show current users
        total_users = users_collection.count_documents({})
        print(f"\n✓ Total users in database: {total_users}")
        
        # Show most recent user (this is what the app will use)
        recent_user = users_collection.find_one(sort=[('created_at', -1)])
        if recent_user:
            print(f"✓ Most recent user (will be used by app): {recent_user['email']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error setting up users: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Setting up test users for situp exercise system")
    print("=" * 50)
    
    success = setup_test_users()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("✅ You can now run the situp application with user context")
    else:
        print("\n❌ Setup failed - check MongoDB connection")
        sys.exit(1)