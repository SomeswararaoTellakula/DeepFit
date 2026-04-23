#!/usr/bin/env python3
"""
Test script to verify frontend integration with enhanced situp functionality
"""

import webbrowser
import time
import subprocess
import sys
import os

def test_frontend_integration():
    """Test the frontend integration"""
    
    print("Testing Frontend Integration")
    print("=" * 40)
    
    # Check if app_situp.py exists
    if not os.path.exists('app_situp.py'):
        print("ERROR: app_situp.py not found")
        return False
    
    # Check if template exists
    template_path = 'templates/index_situp.html'
    if not os.path.exists(template_path):
        print("ERROR: index_situp.html template not found")
        return False
    
    # Check if JavaScript file exists
    js_path = 'static/situp_script.js'
    if not os.path.exists(js_path):
        print("ERROR: situp_script.js not found")
        return False
    
    # Check if CSS file exists
    css_path = 'static/style.css'
    if not os.path.exists(css_path):
        print("ERROR: style.css not found")
        return False
    
    print("✓ All required files found")
    
    # Start the Flask app
    print("\nStarting Flask app...")
    print("Navigate to: http://localhost:5001")
    print("\nTest the following features:")
    print("1. Timer display (03:00 initially)")
    print("2. Start Camera button (starts timer)")
    print("3. Timer countdown (real-time updates)")
    print("4. Stop Camera button (shows success popup)")
    print("5. Success popup with green checkmark")
    print("6. Start New Session button")
    print("7. Session status indicators")
    
    # Try to open browser automatically
    try:
        webbrowser.open('http://localhost:5001')
        print("\n✓ Browser opened automatically")
    except:
        print("\n⚠ Could not open browser automatically")
    
    # Start the Flask app
    try:
        subprocess.run([sys.executable, 'app_situp.py'], check=True)
    except KeyboardInterrupt:
        print("\n\nFlask app stopped by user")
    except Exception as e:
        print(f"\nError running Flask app: {e}")
    
    return True

if __name__ == "__main__":
    test_frontend_integration()