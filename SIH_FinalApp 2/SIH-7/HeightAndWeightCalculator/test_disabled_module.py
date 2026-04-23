"""
Test script for Disabled Persons Assessment Module
This script verifies that all routes and templates are properly configured.
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    if os.path.exists(filepath):
        print(f"[OK] {description}: Found")
        return True
    else:
        print(f"[MISSING] {description}: Missing")
        return False

def main():
    print("=" * 60)
    print("Disabled Persons Assessment Module - Installation Check")
    print("=" * 60)
    print()
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    templates_path = os.path.join(base_path, 'templates')
    
    all_good = True
    
    # Check template files
    print("Checking Template Files:")
    print("-" * 60)
    
    templates = [
        ('disabled_selection.html', 'Disabled Selection Page'),
        ('blind_registration.html', 'Blind Registration Form'),
        ('blind_assessment.html', 'Blind Assessment Test Page'),
        ('blind_dashboard.html', 'Blind Dashboard Results'),
        ('other_disabled_registration.html', 'Other Disabled Registration')
    ]
    
    for template_file, description in templates:
        filepath = os.path.join(templates_path, template_file)
        if not check_file_exists(filepath, description):
            all_good = False
    
    print()
    print("Checking Main Application File:")
    print("-" * 60)
    
    app_file = os.path.join(base_path, 'app.py')
    if check_file_exists(app_file, 'Main Application (app.py)'):
        # Check if routes are added
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        routes_to_check = [
            ('disabled_selection', 'Disabled Selection Route'),
            ('blind_registration', 'Blind Registration Route'),
            ('blind_assessment', 'Blind Assessment Route'),
            ('save_blind_assessment', 'Save Assessment API'),
            ('blind_dashboard', 'Blind Dashboard Route'),
            ('other_disabled_registration', 'Other Disabled Route')
        ]
        
        print()
        print("Checking Routes in app.py:")
        print("-" * 60)
        
        for route_name, description in routes_to_check:
            if route_name in content:
                print(f"[OK] {description}: Found")
            else:
                print(f"[MISSING] {description}: Missing")
                all_good = False
    else:
        all_good = False
    
    print()
    print("=" * 60)
    
    if all_good:
        print("[SUCCESS] All components installed successfully!")
        print()
        print("Next Steps:")
        print("1. Start the Flask application: python app.py")
        print("2. Navigate to the signup page")
        print("3. Click on 'Disabled Persons' button")
        print("4. Select 'Blind Person' to test the assessment flow")
    else:
        print("[ERROR] Some components are missing. Please check the errors above.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
