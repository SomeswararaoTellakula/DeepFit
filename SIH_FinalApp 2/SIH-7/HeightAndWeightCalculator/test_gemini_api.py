"""
Test script to verify Gemini API configuration and connectivity
"""
import google.generativeai as genai

API_KEY = "AIzaSyDT59Dd9UJvR1NlCLYamS8pVriOEQs3gRY"

def test_api_connection():
    print("=" * 60)
    print("Testing Gemini API Connection")
    print("=" * 60)
    
    try:
        # Configure API
        genai.configure(api_key=API_KEY)
        print("✓ API key configured successfully")
        
        # List available models
        print("\n📋 Available Models:")
        print("-" * 60)
        models = genai.list_models()
        
        text_models = []
        vision_models = []
        
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                model_name = model.name.replace('models/', '')
                print(f"  • {model_name}")
                
                if 'vision' in model_name.lower():
                    vision_models.append(model_name)
                else:
                    text_models.append(model_name)
        
        print("\n" + "=" * 60)
        print("Recommended Models:")
        print("=" * 60)
        
        if text_models:
            print(f"\n✓ Text Model: {text_models[0]}")
        if vision_models:
            print(f"✓ Vision Model: {vision_models[0]}")
        
        # Test text generation
        print("\n" + "=" * 60)
        print("Testing Text Generation")
        print("=" * 60)
        
        if text_models:
            model = genai.GenerativeModel(text_models[0])
            response = model.generate_content("Say hello in one sentence")
            print(f"\n✓ Test successful!")
            print(f"Response: {response.text}")
        else:
            print("\n✗ No text models available")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Verify your API key is correct")
        print("2. Check your internet connection")
        print("3. Ensure google-generativeai is installed: pip install google-generativeai")
        return False

if __name__ == "__main__":
    test_api_connection()
    input("\nPress Enter to exit...")
