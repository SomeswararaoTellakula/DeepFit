#!/usr/bin/env python3
"""
Test script to verify data storage functionality
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_system import DataStorageManager, MeasurementResult, DetectionStatus

def test_data_storage():
    """Test the data storage functionality"""
    
    print("Testing Data Storage Functionality")
    print("=" * 50)
    
    # Initialize data manager
    data_manager = DataStorageManager()
    
    # Create test measurement result
    test_result = MeasurementResult(
        height_cm=175.5,
        weight_kg=70.2,
        confidence_score=0.85,
        uncertainty_height=2.1,
        uncertainty_weight=3.5,
        processing_time_ms=150.0,
        detection_status=DetectionStatus.GOOD_POSITION,
        calibration_quality=0.5
    )
    
    # Test user data
    test_user_data = {
        "user_id": "test_user_001",
        "age": 25,
        "gender": "M",
        "height": 175.0,
        "weight": 70.0
    }
    
    print("Saving height/weight measurement...")
    saved_file = data_manager.save_height_weight_measurement(test_result, test_user_data)
    print(f"Saved to: {saved_file}")
    
    # Test exercise data
    exercise_data = {
        "exercise_type": "situps",
        "repetitions": 25,
        "form_score": 85,
        "duration": 120,
        "range_of_motion": 90,
        "speed_control": 88
    }
    
    print("\nSaving exercise data...")
    exercise_file = data_manager.save_exercise_data("situps", exercise_data, test_user_data)
    print(f"Saved to: {exercise_file}")
    
    # Verify directory structure
    print("\nVerifying directory structure...")
    base_dir = Path("validation_results")
    
    expected_dirs = [
        base_dir / "Height and Weight",
        base_dir / "Exercises" / "Situps"
    ]
    
    for dir_path in expected_dirs:
        if dir_path.exists():
            print(f"OK {dir_path} - EXISTS")
            
            # List files in directory
            files = list(dir_path.glob("*.json"))
            for file in files:
                print(f"   FILE {file.name}")
        else:
            print(f"ERROR {dir_path} - MISSING")
    
    print("\nData storage test completed!")

if __name__ == "__main__":
    test_data_storage()