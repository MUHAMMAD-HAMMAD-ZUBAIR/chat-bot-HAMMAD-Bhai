import os
import sys
from flask import Flask, render_template, request, jsonify

# Add parent directory to path to import from main app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import from main app.py with fallback
try:
    from app import (
        get_comprehensive_realtime_info,
        GeminiModel,
        ChatBot,
        ConversationHistory
    )
    FULL_AI_AVAILABLE = True
    print("✅ Full AI functionality loaded")
except ImportError as e:
    print(f"⚠️ Full AI not available: {e}")
    FULL_AI_AVAILABLE = False

# Create Flask app
app = Flask(__name__,
           template_folder='../templates',
           static_folder='../static')

# Global variables
chat_bot = None
conversation_history = None

def initialize_chatbot():
    """Initialize the full AI chatbot"""
    global chat_bot

    if not FULL_AI_AVAILABLE:
        return None

    try:
        # Get API key from environment
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("⚠️ GEMINI_API_KEY not found")
            return None

        # Initialize with the most powerful model
        model = GeminiModel(api_key, 'gemini-2.0-flash-exp')
        chat_bot = ChatBot(model)
        print("✅ Full AI chatbot initialized")
        return chat_bot
    except Exception as e:
        print(f"❌ Chatbot initialization failed: {e}")
        return None

# Initialize conversation history
if FULL_AI_AVAILABLE:
    conversation_history = ConversationHistory()
else:
    # Simple fallback
    class SimpleHistory:
        def __init__(self):
            self.history = []
        def reset(self):
            self.history = []
        def add_user_message(self, msg):
            self.history.append({"role": "user", "content": msg})
        def add_model_response(self, msg):
            self.history.append({"role": "model", "content": msg})
    conversation_history = SimpleHistory()

@app.route('/')
def home():
    """Serve the main chat interface"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>HAMMAD BHAI Chatbot</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; text-align: center; }}
                .status {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .error {{ background: #ffe8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .endpoint {{ background: #f8f9fa; padding: 10px; margin: 10px 0; border-left: 4px solid #007bff; }}
                code {{ background: #f1f1f1; padding: 2px 5px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 HAMMAD BHAI AI Chatbot</h1>
                <p><strong>Created by MUHAMMAD HAMMAD ZUBAIR</strong></p>

                <div class="status">
                    ✅ <strong>Deployment Successful!</strong><br>
                    🚀 Vercel deployment working properly
                </div>

                <div class="error">
                    ⚠️ Template loading issue: {str(e)}<br>
                    Using fallback interface
                </div>

                <h3>🔗 Available Endpoints:</h3>
                <div class="endpoint">
                    <strong>GET /health</strong> - Health check
                </div>
                <div class="endpoint">
                    <strong>POST /chat</strong> - Chat with HAMMAD BHAI<br>
                    <code>{{"message": "Hello"}}</code>
                </div>
                <div class="endpoint">
                    <strong>GET /api/info</strong> - API information
                </div>

                <h3>🧪 Quick Test:</h3>
                <p>Send POST request to <code>/chat</code> with JSON:</p>
                <code>{{"message": "Assalam-o-Alaikum HAMMAD BHAI"}}</code>

                <div style="margin-top: 30px; text-align: center; color: #666;">
                    <p>Powered by Google Gemini 2.0 Flash Experimental</p>
                    <p>© 2025 MUHAMMAD HAMMAD ZUBAIR</p>
                </div>
            </div>
        </body>
        </html>
        """

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'HAMMAD BHAI Chatbot',
        'creator': 'MUHAMMAD HAMMAD ZUBAIR',
        'deployment': 'vercel_success',
        'ai_status': 'available' if FULL_AI_AVAILABLE else 'fallback_mode',
        'platform': 'Vercel'
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        global chat_bot

        # Get user message
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        user_message = data['message'].strip()
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        # Try to use full AI if available
        if FULL_AI_AVAILABLE:
            # Initialize chatbot if not already done
            if chat_bot is None:
                chat_bot = initialize_chatbot()

            if chat_bot is not None:
                try:
                    # Get real-time context
                    realtime_context = get_comprehensive_realtime_info()

                    # Enhanced message with context
                    enhanced_message = f"""
{realtime_context}

User Question: {user_message}

Please provide a helpful, accurate response using the real-time information above when relevant.
"""

                    # Add to conversation history
                    conversation_history.add_user_message(enhanced_message)

                    # Start chat session
                    chat_session = chat_bot.model.start_chat(history=conversation_history.get())

                    # Get AI response
                    response = chat_session.send_message(enhanced_message)
                    ai_response = response.text

                    # Add to history
                    conversation_history.add_model_response(ai_response)

                    return jsonify({
                        'response': ai_response,
                        'status': 'success',
                        'mode': 'full_ai',
                        'creator': 'MUHAMMAD HAMMAD ZUBAIR'
                    })

                except Exception as e:
                    print(f"AI chat error: {e}")
                    # Fall through to fallback mode

        # Fallback mode response
        conversation_history.add_user_message(user_message)

        fallback_response = f"""Assalam-o-Alaikum! Main HAMMAD BHAI hun! 🤖

Aap ne kaha: "{user_message}"

Main MUHAMMAD HAMMAD ZUBAIR ka banaya hua AI assistant hun.

✅ Vercel deployment successful!
🚀 Basic chatbot functionality working!

{"🔧 Full AI mode loading..." if FULL_AI_AVAILABLE else "⚠️ Running in fallback mode"}

Features:
- Google Gemini 2.0 Flash Experimental AI
- Real-time information access
- Weather & prayer times
- Multi-language support
- 50+ languages support

Shukriya!
- HAMMAD BHAI (Created by MUHAMMAD HAMMAD ZUBAIR)"""

        conversation_history.add_model_response(fallback_response)

        return jsonify({
            'response': fallback_response,
            'status': 'success',
            'mode': 'fallback',
            'creator': 'MUHAMMAD HAMMAD ZUBAIR'
        })

    except Exception as e:
        return jsonify({
            'error': f'Chat error: {str(e)}',
            'response': 'Sorry, please try again.',
            'creator': 'MUHAMMAD HAMMAD ZUBAIR'
        }), 500

@app.route('/reset', methods=['POST'])
def reset_chat():
    """Reset conversation history"""
    try:
        conversation_history.reset()
        return jsonify({
            'status': 'Chat history reset successfully',
            'creator': 'MUHAMMAD HAMMAD ZUBAIR'
        })
    except Exception as e:
        return jsonify({'error': f'Reset failed: {str(e)}'}), 500

@app.route('/api/info')
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'HAMMAD BHAI AI Chatbot',
        'version': '2.0',
        'creator': 'MUHAMMAD HAMMAD ZUBAIR',
        'status': 'Deployment Successful',
        'platform': 'Vercel',
        'ai_mode': 'Full AI' if FULL_AI_AVAILABLE else 'Fallback Mode',
        'model': 'Google Gemini 2.0 Flash Experimental',
        'features': [
            'Real-time information access',
            'Multi-language support (50+ languages)',
            'Weather and prayer times',
            'Currency and crypto prices',
            'News and sports updates',
            'Advanced AI conversations'
        ],
        'endpoints': {
            '/': 'Main chat interface',
            '/chat': 'Chat API (POST)',
            '/reset': 'Reset conversation (POST)',
            '/health': 'Health check',
            '/api/info': 'API information'
        }
    })

# Add CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
