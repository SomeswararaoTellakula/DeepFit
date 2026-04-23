#!/usr/bin/env python3
"""
Direct test of save functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_situp import save_results, situps_detector, RESULTS_DIR
import json
from pathlib import Path

def test_save_function():
    """Test the save_results function directly"""
    
    print("Testing save_results function directly...")
    
    # Set some test data in the detector
    situps_detector.count = 24  # From the screenshot
    situps_detector.form_feedback = "Go Up"
    situps_detector.last_angle = 120
    
    # Test save
    result = save_results(180, is_manual_stop=False)
    
    if result:
        print("✓ Save function returned True")
        
        # Check if file was created
        json_files = list(RESULTS_DIR.glob("situp_result_*.json"))
        if json_files:
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            print(f"✓ File created: {latest_file.name}")
            
            # Read and display contents
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            print("File contents:")
            print(json.dumps(data, indent=2))
            
            return True
        else:
            print("✗ No files found in results directory")
            return False
    else:
        print("✗ Save function returned False")
        return False

if __name__ == "__main__":
    print("Direct Save Test")
    print("=" * 20)
    
    success = test_save_function()
    
    if success:
        print("\n🎉 Save functionality is working!")
    else:
        print("\n❌ Save functionality failed!")