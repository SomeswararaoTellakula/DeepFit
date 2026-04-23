#!/usr/bin/env python3
"""
Simple startup script for the Situps Counter application
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'opencv-python', 
        'mediapipe',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Main function to start the situps app"""
    print("🏋️ Starting Situps Counter Application...")
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Missing dependencies. Please install required packages.")
        sys.exit(1)
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("✅ Dependencies OK")
    print("🚀 Starting Flask server...")
    print("📱 Open your browser to: http://127.0.0.1:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    
    try:
        # Import and run the app
        from app_situp import app
        app.run(debug=True, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()