#!/usr/bin/env python3
"""
Verify data storage is working correctly
"""

import json
from pathlib import Path
from datetime import datetime

def verify_latest_result():
    """Verify the latest result file"""
    
    results_dir = Path("validation_results/Exercises/Situps")
    
    if not results_dir.exists():
        print("ERROR: Results directory does not exist")
        return False
    
    # Find all situp result files
    result_files = list(results_dir.glob("situp_result_*.json"))
    
    if not result_files:
        print("ERROR: No situp result files found")
        return False
    
    # Get the latest file
    latest_file = max(result_files, key=lambda x: x.stat().st_mtime)
    
    print(f"Latest result file: {latest_file.name}")
    
    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        print("File contents:")
        print(json.dumps(data, indent=2))
        
        # Verify required fields
        required_fields = ['user_id', 'exercise_type', 'repetitions', 'form_score', 
                          'duration', 'range_of_motion', 'speed_control', 'timestamp']
        
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"ERROR: Missing fields: {missing_fields}")
            return False
        
        # Verify data types and values
        if data['exercise_type'] != 'situps':
            print("ERROR: exercise_type should be 'situps'")
            return False
        
        if not isinstance(data['repetitions'], int):
            print("ERROR: repetitions should be integer")
            return False
        
        if not isinstance(data['duration'], int):
            print("ERROR: duration should be integer")
            return False
        
        if not data['timestamp'].endswith('Z'):
            print("ERROR: timestamp should be in UTC format ending with 'Z'")
            return False
        
        if data['user_id'] == 'unknown_user':
            print("WARNING: user_id is 'unknown_user' - MongoDB connection may have failed")
        
        print("SUCCESS: All validations passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: Could not read file: {e}")
        return False

def main():
    print("Data Storage Verification")
    print("=" * 30)
    
    success = verify_latest_result()
    
    if success:
        print("\n✓ Data storage is working correctly!")
        print("✓ JSON format is correct")
        print("✓ All required fields are present")
        print("✓ File is saved in correct directory")
    else:
        print("\n✗ Data storage verification failed!")
        print("Check the errors above and fix the issues.")

if __name__ == "__main__":
    main()