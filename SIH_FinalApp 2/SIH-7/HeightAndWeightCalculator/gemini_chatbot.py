import google.generativeai as genai
from PIL import Image
import io
from difflib import SequenceMatcher
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

class GeminiChatbot:
    def __init__(self, api_key):
        try:
            # Configure API with provided key
            genai.configure(api_key=api_key)
            print(f"Configuring Gemini API...")
            
            # Use correct model name
            self.text_model_name = 'gemini-2.5-flash'
            self.vision_model_name = 'gemini-2.5-flash'
            
            print(f"Initializing models...")
            print(f"Text model: {self.text_model_name}")
            print(f"Vision model: {self.vision_model_name}")
            
            # Initialize models with generation config
            generation_config = {
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
            
            self.model = genai.GenerativeModel(
                model_name=self.text_model_name,
                generation_config=generation_config
            )
            self.vision_model = genai.GenerativeModel(
                model_name=self.vision_model_name,
                generation_config=generation_config
            )
            
            # Start chat
            self.chat = self.model.start_chat(history=[])
            
            # Initialize trained data
            self.trained_data = self._load_trained_data()
            
            print("[OK] Chatbot initialized successfully")
            
        except Exception as e:
            print(f"[ERROR] Error initializing chatbot: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _load_trained_data(self):
        """Load trained Q&A data for sports assessment"""
        return {
            "what are the different types of assessment tests in sports": "Sports assessment tests include physical tests (strength, endurance, flexibility), skill-based tests (accuracy, speed, coordination), psychological tests (focus, confidence), and reaction tests (response to visual or audio signals). These tests help measure overall athletic ability.",
            
            "how can we determine if a sportsperson is fit": "A sportsperson is considered fit if they can perform physical activities efficiently without excessive fatigue, recover quickly after exertion, and maintain consistent performance during training and competition.",
            
            "what makes a person physically fit": "Physical fitness depends on regular exercise, balanced nutrition, proper rest, and mental well-being. Key components include strength, endurance, flexibility, speed, and coordination.",
            
            "how do we evaluate a sportsperson": "A sportsperson is evaluated using performance tests, observation during practice or matches, fitness assessments, and analysis of consistency, technique, and improvement over time.",
            
            "why is endurance important in sports": "Endurance allows athletes to sustain physical activity for longer periods without fatigue. It is essential for maintaining performance levels, especially in long-duration sports like running or cycling.",
            
            "how is reaction time important in sports": "Reaction time is crucial because it determines how quickly an athlete responds to stimuli such as a ball, sound, or opponent's movement. Faster reaction times improve performance and decision-making.",
            
            "what role does mental fitness play in sports": "Mental fitness helps athletes stay focused, confident, and calm under pressure. It improves decision-making, reduces stress, and enhances overall performance during competitions.",
            
            "how does flexibility impact athletic performance": "Flexibility improves the range of motion of joints, reduces the risk of injury, and enhances movement efficiency, which is important in sports like gymnastics, yoga, and athletics.",
            
            "what is the importance of strength in sports": "Strength helps athletes perform powerful movements such as jumping, lifting, and sprinting. It also supports injury prevention and overall physical stability.",
            
            "how can coaches track improvement in athletes": "Coaches track improvement by comparing test results over time, analyzing performance data, observing skill development, and monitoring consistency during training and competitions."
        }
    
    def _find_trained_answer(self, message):
        """Check if message matches trained data"""
        message_lower = message.lower().strip()
        
        # Direct match
        if message_lower in self.trained_data:
            return self.trained_data[message_lower]
        
        # Fuzzy matching for similar questions
        best_match = None
        best_ratio = 0.0
        threshold = 0.7  # 70% similarity threshold
        
        for question, answer in self.trained_data.items():
            ratio = SequenceMatcher(None, message_lower, question).ratio()
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = answer
        
        return best_match
    
    def send_message(self, message):
        """Hybrid response system: Check trained data first, then use Gemini API"""
        try:
            # Step 1: Check trained data
            trained_answer = self._find_trained_answer(message)
            if trained_answer:
                print(f"[OK] Returning trained answer for: {message[:50]}...")
                return trained_answer
            
            # Step 2: Use Gemini API
            print(f"[OK] Using Gemini API for: {message[:50]}...")
            
            # Add safety settings
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            response = self.chat.send_message(
                message,
                safety_settings=safety_settings
            )
            
            # Check if response was blocked
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                return "I couldn't process that request. Please try rephrasing your question."
            
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            print(f"Gemini API Error: {error_msg}")
            import traceback
            traceback.print_exc()
            
            # Handle specific errors
            if "quota" in error_msg.lower() or "resource_exhausted" in error_msg.lower():
                return "I apologize, but the service is currently experiencing high demand. Please try again in a moment."
            elif "api_key" in error_msg.lower() or "invalid" in error_msg.lower():
                return "There's a configuration issue with the API. Please check the API key."
            elif "permission" in error_msg.lower() or "403" in error_msg:
                return "API access denied. Please verify the API key has proper permissions."
            else:
                return f"I encountered an error: {error_msg}. Please try again."
    
    def send_message_with_image(self, message, image_data):
        """Handle image analysis with Gemini Vision"""
        try:
            if not self.vision_model:
                return "Image analysis is currently unavailable. Please try text-based questions."
            
            image = Image.open(io.BytesIO(image_data))
            
            # Resize large images
            max_size = 1024
            if image.width > max_size or image.height > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Add safety settings
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            response = self.vision_model.generate_content(
                [message, image],
                safety_settings=safety_settings
            )
            
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                return "I couldn't analyze this image. Please try a different image."
            
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            print(f"Gemini Vision API Error: {error_msg}")
            import traceback
            traceback.print_exc()
            return f"Unable to analyze image: {error_msg}"
    
    def analyze_file(self, message, file_path):
        """Analyze uploaded files"""
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Check file size (limit to 5MB)
            if len(file_data) > 5 * 1024 * 1024:
                return "The file is too large. Please upload files smaller than 5MB."
            
            # Handle image files
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                return self.send_message_with_image(message, file_data)
            
            # Handle text files
            else:
                try:
                    file_content = file_data.decode('utf-8', errors='ignore')
                    if len(file_content) > 10000:
                        file_content = file_content[:10000] + "\n\n[Content truncated...]"
                    
                    full_message = f"{message}\n\nFile content:\n```\n{file_content}\n```"
                    return self.send_message(full_message)
                except Exception as decode_error:
                    return "Unable to read the file content. Please ensure it's a valid text or image file."
                    
        except Exception as e:
            return "Error analyzing the file. Please try again with a different file."
    
    def reset_chat(self):
        """Reset the chat history"""
        try:
            self.chat = self.model.start_chat(history=[])
            return True
        except Exception as e:
            print(f"Error resetting chat: {e}")
            return False
