import os
import sys
from flask import Flask, render_template, request, jsonify

# Add the parent directory to the Python path to import from app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules with error handling
try:
    import google.generativeai as genai
    from datetime import datetime
    import pytz
    import requests
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Dependency import error: {e}")
    DEPENDENCIES_AVAILABLE = False

try:
    # Import all the functions and classes from the main app.py
    from app import (
        get_comprehensive_realtime_info,
        GeminiModel,
        ChatBot,
        ConversationHistory
    )
    APP_IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"App import error: {e}")
    APP_IMPORTS_AVAILABLE = False

# Create Flask app for Vercel
app = Flask(__name__,
           template_folder='../templates',
           static_folder='../static')

# Global variables for chat functionality
chat_bot = None
conversation_history = None

# Initialize conversation history if imports are available
if APP_IMPORTS_AVAILABLE:
    conversation_history = ConversationHistory()
else:
    # Create a simple fallback conversation history
    class SimpleConversationHistory:
        def __init__(self):
            self.history = []
        def reset(self):
            self.history = []
    conversation_history = SimpleConversationHistory()

def initialize_chatbot():
    """Initialize the chatbot with error handling"""
    global chat_bot

    # Check if dependencies are available
    if not DEPENDENCIES_AVAILABLE:
        print("Error: Required dependencies not available")
        return None

    if not APP_IMPORTS_AVAILABLE:
        print("Error: App imports not available")
        return None

    try:
        # Get API key from environment variable
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables")
            return None

        # Initialize the model with the most powerful Gemini model
        model = GeminiModel(api_key, 'gemini-2.0-flash-exp')
        chat_bot = ChatBot(model)
        return chat_bot
    except Exception as e:
        print(f"Error initializing chatbot: {e}")
        return None

@app.route('/')
def index():
    """Serve the main chat interface"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading page: {str(e)}", 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        global chat_bot

        # Initialize chatbot if not already done
        if chat_bot is None:
            chat_bot = initialize_chatbot()
            if chat_bot is None:
                return jsonify({
                    'error': 'Chatbot initialization failed. Please check API key configuration.',
                    'response': 'Sorry, I am currently unavailable. Please try again later.'
                }), 500

        # Get user message
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        user_message = data['message'].strip()
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        # Get real-time information context if available
        if APP_IMPORTS_AVAILABLE:
            try:
                realtime_context = get_comprehensive_realtime_info()
            except Exception as e:
                print(f"Error getting real-time info: {e}")
                realtime_context = "Real-time information temporarily unavailable."
        else:
            realtime_context = "Real-time information not available in this deployment."

        # Prepare the enhanced message with context
        enhanced_message = f"""
{realtime_context}

User Question: {user_message}

Please provide a helpful, accurate response using the real-time information above when relevant.
"""

        # Add user message to history
        conversation_history.add_user_message(enhanced_message)

        # Start chat session with history
        chat_session = chat_bot.model.start_chat(history=conversation_history.get())

        # Get response from AI
        response = chat_session.send_message(enhanced_message)
        ai_response = response.text

        # Add AI response to history
        conversation_history.add_model_response(ai_response)

        return jsonify({
            'response': ai_response,
            'status': 'success'
        })

    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            'error': f'Chat processing failed: {str(e)}',
            'response': 'Sorry, I encountered an error. Please try again.'
        }), 500

@app.route('/reset', methods=['POST'])
def reset_chat():
    """Reset the conversation history"""
    try:
        global conversation_history
        conversation_history.reset()
        return jsonify({'status': 'Chat history reset successfully'})
    except Exception as e:
        return jsonify({'error': f'Reset failed: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'Hammad Bhai Chatbot',
            'version': '2.0',
            'creator': 'MUHAMMAD HAMMAD ZUBAIR'
        })
    except Exception as e:
        return jsonify({'error': f'Health check failed: {str(e)}'}), 500

@app.route('/api/info')
def api_info():
    """API information endpoint"""
    try:
        return jsonify({
            'name': 'Hammad Bhai AI Chatbot',
            'version': '2.0',
            'creator': 'MUHAMMAD HAMMAD ZUBAIR',
            'model': 'Google Gemini 2.0 Flash Experimental',
            'features': [
                'Real-time information access',
                'Multi-language support',
                'Advanced AI conversations',
                'Weather and prayer times',
                'Currency and crypto prices',
                'News and sports updates'
            ],
            'endpoints': {
                '/': 'Main chat interface',
                '/chat': 'Chat API (POST)',
                '/reset': 'Reset conversation (POST)',
                '/health': 'Health check',
                '/api/info': 'API information'
            }
        })
    except Exception as e:
        return jsonify({'error': f'API info failed: {str(e)}'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'details': str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'details': str(error)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

# Configure Flask for production
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# Add CORS headers for Vercel
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# For Vercel serverless deployment - simplified approach
# Vercel will automatically handle the WSGI interface

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
