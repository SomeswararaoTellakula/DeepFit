"""
Quick test to verify Gemini API key works
"""
import google.generativeai as genai

API_KEY = "AIzaSyDT59Dd9UJvR1NlCLYamS8pVriOEQs3gRY"

print("=" * 60)
print("Testing Gemini API Key")
print("=" * 60)

try:
    genai.configure(api_key=API_KEY)
    print("✓ API key configured")
    
    # Try different models
    models_to_test = [
        'gemini-1.5-flash',
        'gemini-1.5-pro', 
        'gemini-pro',
        'gemini-1.0-pro'
    ]
    
    working_model = None
    
    for model_name in models_to_test:
        try:
            print(f"\nTesting: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello")
            print(f"✓ {model_name} WORKS!")
            print(f"Response: {response.text}")
            working_model = model_name
            break
        except Exception as e:
            print(f"✗ {model_name} failed: {str(e)}")
    
    if working_model:
        print("\n" + "=" * 60)
        print(f"SUCCESS! Use this model: {working_model}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("ERROR: No working model found")
        print("Please check:")
        print("1. API key is valid")
        print("2. Gemini API is enabled in Google Cloud Console")
        print("3. You have quota available")
        print("=" * 60)
        
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    print("\nPlease verify:")
    print("1. API key is correct")
    print("2. Internet connection is working")
    print("3. google-generativeai package is installed")

input("\nPress Enter to exit...")
