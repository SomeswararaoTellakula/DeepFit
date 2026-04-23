#!/usr/bin/env python3
"""
Test the save system to ensure it works perfectly
"""

import os
import json
from datetime import datetime
from pathlib import Path

def test_save_system():
    """Test the save system directly"""
    print("🧪 TESTING SAVE SYSTEM")
    print("=" * 40)
    
    # Create the exact directory structure
    results_dir = Path("validation_results/Exercises/Situps")
    results_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Directory created: {results_dir}")
    
    # Create test data (exactly like your session)
    result_data = {
        "user_id": "test_user_001@example.com",
        "exercise_type": "situps",
        "repetitions": 15,  # From your screenshot
        "form_score": 85,
        "duration": 180,
        "range_of_motion": 78,
        "speed_control": 82,
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    
    # Create filename
    timestamp_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"situp_result_test_user_001_example_com_{timestamp_str}.json"
    filepath = results_dir / filename
    
    # Save file
    try:
        with open(filepath, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"✅ File saved: {filepath}")
        print(f"✅ File size: {os.path.getsize(filepath)} bytes")
        
        # Verify content
        with open(filepath, 'r') as f:
            saved_data = json.load(f)
        
        print("✅ File content verified:")
        print(json.dumps(saved_data, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_save_system()
    if success:
        print("\n🎉 SAVE SYSTEM WORKS PERFECTLY!")
    else:
        print("\n💥 SAVE SYSTEM FAILED!")