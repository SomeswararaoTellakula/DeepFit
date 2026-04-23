#!/usr/bin/env python3
"""
Test MongoDB data fetching for dynamic benchmarks
"""

from dynamic_benchmarks import DynamicBenchmarkSystem
from pymongo import MongoClient

def test_mongodb_connection():
    """Test MongoDB connection and data fetching"""
    
    print("=== TESTING MONGODB DATA FETCHING ===\n")
    
    try:
        # Test MongoDB connection
        client = MongoClient("mongodb://localhost:27017/")
        db = client["sih2573"]
        
        print("1. MongoDB Connection: SUCCESS")
        
        # List collections
        collections = db.list_collection_names()
        print(f"2. Available Collections: {collections}")
        
        # Test user data
        users = list(db.users.find().limit(3))
        print(f"3. Sample Users Found: {len(users)}")
        for user in users:
            print(f"   - Email: {user.get('email')}, Age: {user.get('age')}, Gender: {user.get('gender')}")
        
        # Test measurement collections
        measurement_collections = [
            'Final_Estimated_Height_and_Weight',
            'Height and Weight', 
            'measurements'
        ]
        
        for collection_name in measurement_collections:
            try:
                count = db[collection_name].count_documents({})
                print(f"4. {collection_name}: {count} records")
                
                if count > 0:
                    sample = db[collection_name].find_one()
                    print(f"   Sample fields: {list(sample.keys())}")
            except Exception as e:
                print(f"4. {collection_name}: Error - {e}")
        
        # Test dynamic benchmark system
        print("\n5. Testing Dynamic Benchmark System:")
        system = DynamicBenchmarkSystem()
        
        # Get a test user email
        test_user = db.users.find_one()
        if test_user:
            user_email = test_user.get('email')
            print(f"   Testing with user: {user_email}")
            
            # Test biometric fetching
            biometrics = system.get_user_biometrics(user_email)
            if biometrics:
                print(f"   User biometrics: {biometrics}")
                
                # Test benchmark generation
                benchmarks = system.get_dynamic_benchmarks(user_email)
                if 'error' not in benchmarks:
                    print(f"   Dynamic benchmarks: {benchmarks}")
                    print("   SUCCESS: Complete system working")
                else:
                    print(f"   ERROR: {benchmarks['error']}")
            else:
                print("   ERROR: No biometric data found")
        else:
            print("   ERROR: No users found in database")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_mongodb_connection()