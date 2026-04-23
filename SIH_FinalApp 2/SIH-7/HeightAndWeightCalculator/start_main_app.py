#!/usr/bin/env python3
import os
import sys

def main():
    print("🚀 Starting DeepFit Main Application...")
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from app import app
        print("✅ App loaded successfully")
        print("🌐 Open browser to: http://127.0.0.1:5000")
        print("🏋️ Click 'Exercise Analysis' to access situps counter")
        print("⏹️  Press Ctrl+C to stop")
        app.run(debug=False, host='127.0.0.1', port=5000)
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Run: pip install flask opencv-python mediapipe numpy pymongo flask-cors bcrypt")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()