from flask import Blueprint, request, jsonify, session, render_template
from gemini_chatbot import GeminiChatbot
import os
from werkzeug.utils import secure_filename
import traceback

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chatbot')
def chatbot_ui():
    """Render the chatbot UI page"""
    return render_template('chatbot.html')

# Use the provided Gemini API key from environment or fallback to default
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDxS5tdSLWiHp894erNzRq6tvcWJRmhkYw")
UPLOAD_FOLDER = 'uploads/chatbot'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

chatbot_instances = {}

def get_chatbot(session_id):
    if session_id not in chatbot_instances:
        try:
            chatbot_instances[session_id] = GeminiChatbot(GEMINI_API_KEY)
        except Exception as e:
            print(f"Error creating chatbot instance: {e}")
            raise
    return chatbot_instances[session_id]

@chatbot_bp.route('/api/chatbot/message', methods=['POST'])
def send_message():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': 'Message is required'}), 400
            
        session_id = session.get('user_id', 'default')
        
        chatbot = get_chatbot(session_id)
        response = chatbot.send_message(message)
        
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error in send_message: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to get response: {str(e)}'}), 500

@chatbot_bp.route('/api/chatbot/image', methods=['POST'])
def send_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image = request.files['image']
        if image.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
            
        message = request.form.get('message', 'What is in this image?')
        session_id = session.get('user_id', 'default')
        
        chatbot = get_chatbot(session_id)
        image_data = image.read()
        response = chatbot.send_message_with_image(message, image_data)
        
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error in send_image: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to analyze image: {str(e)}'}), 500

@chatbot_bp.route('/api/chatbot/file', methods=['POST'])
def send_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
            
        message = request.form.get('message', 'Analyze this file')
        session_id = session.get('user_id', 'default')
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        chatbot = get_chatbot(session_id)
        response = chatbot.analyze_file(message, filepath)
        
        # Clean up the file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error in send_file: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to analyze file: {str(e)}'}), 500

@chatbot_bp.route('/api/chatbot/reset', methods=['POST'])
def reset_chat():
    try:
        session_id = session.get('user_id', 'default')
        if session_id in chatbot_instances:
            del chatbot_instances[session_id]
        return jsonify({'status': 'success', 'message': 'Chat history cleared'})
    except Exception as e:
        print(f"Error in reset_chat: {e}")
        return jsonify({'error': str(e)}), 500
