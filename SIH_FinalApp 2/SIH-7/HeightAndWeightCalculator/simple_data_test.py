#!/usr/bin/env python3
"""
Simple test to create situp result file
"""

import json
import os
from datetime import datetime
from pathlib import Path
from pymongo import MongoClient

# Configuration
RESULTS_DIR = Path("validation_results/Exercises/Situps")

def create_situp_result():
    """Create a situp result file with proper format"""
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['sih2573']
        users = db['users']
        
        # Get user
        user = users.find_one(sort=[('created_at', -1)])
        user_id = user.get('email', 'test_user@example.com') if user else 'test_user@example.com'
        
        print(f"Using user ID: {user_id}")
        
        # Create result data
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        result_data = {
            "user_id": user_id,
            "exercise_type": "situps",
            "repetitions": 35,
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
        
        print(f"Result saved to: {filepath}")
        
        # Verify file
        with open(filepath, 'r') as f:
            saved_data = json.load(f)
        
        print("File contents:")
        print(json.dumps(saved_data, indent=2))
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Creating situp result file...")
    success = create_situp_result()
    if success:
        print("SUCCESS: File created successfully!")
    else:
        print("FAILED: Could not create file!")