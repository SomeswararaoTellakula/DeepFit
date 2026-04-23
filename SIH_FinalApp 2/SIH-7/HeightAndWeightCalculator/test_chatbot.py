"""Test script to verify Gemini chatbot is working correctly"""
from gemini_chatbot import GeminiChatbot

def test_chatbot():
    print("=" * 60)
    print("Testing Gemini Chatbot")
    print("=" * 60)
    
    # Initialize chatbot
    api_key = "AIzaSyAMr2HcsBfccN71gXRjPrSn_P-1hGmVmWs"
    
    try:
        print("\n1. Initializing chatbot...")
        chatbot = GeminiChatbot(api_key)
        print("[OK] Chatbot initialized successfully\n")
        
        # Test trained data
        print("2. Testing trained data responses...")
        test_questions = [
            "What are the different types of assessment tests in sports?",
            "How can we determine if a sportsperson is fit?",
            "Why is endurance important in sports?"
        ]
        
        for question in test_questions:
            print(f"\nQ: {question}")
            response = chatbot.send_message(question)
            print(f"A: {response[:100]}...")
        
        # Test Gemini API
        print("\n\n3. Testing Gemini API with general question...")
        general_question = "What is the capital of France?"
        print(f"\nQ: {general_question}")
        response = chatbot.send_message(general_question)
        print(f"A: {response}")
        
        print("\n" + "=" * 60)
        print("[OK] All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chatbot()
