#!/usr/bin/env python3
"""
Setup script for situps database collection
Creates the situps collection in MongoDB if it doesn't exist
"""

from db_config import connect_mongodb
from datetime import datetime

def setup_situps_collection():
    """Create situps collection with proper indexes"""
    try:
        client, db = connect_mongodb()
        
        if db is None:
            print("[ERROR] Failed to connect to MongoDB")
            return False
        
        # Create situps collection
        situps_collection = db['situps']
        
        # Create indexes for better performance
        situps_collection.create_index([("user_email", 1), ("submission_time", -1)])
        situps_collection.create_index([("submission_time", -1)])
        
        print("[SUCCESS] Situps collection setup complete")
        print(f"Database: {db.name}")
        print(f"Collection: situps")
        
        # Insert a sample record if collection is empty
        if situps_collection.count_documents({}) == 0:
            sample_data = {
                'user_email': 'test_user@example.com',
                'reps_completed': 15,
                'form_quality': 85,
                'timer_time': '3:00',
                'submission_time': datetime.utcnow(),
                'created_at': datetime.utcnow()
            }
            situps_collection.insert_one(sample_data)
            print("Sample record inserted")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error setting up situps collection: {e}")
        return False

if __name__ == "__main__":
    setup_situps_collection()