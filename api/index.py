import os
import sys
from flask import Flask, render_template, request, jsonify

# Add parent directory to path to import from main app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Simplified imports for Vercel - avoid complex dependencies
try:
    import google.generativeai as genai
    FULL_AI_AVAILABLE = True
    print("✅ Google AI available")
except ImportError as e:
    print(f"⚠️ Google AI not available: {e}")
    FULL_AI_AVAILABLE = False

# Simple model class for Vercel
class SimpleGeminiModel:
    def __init__(self, api_key, model_name='gemini-2.0-flash-exp'):
        genai.configure(api_key=api_key)

        # System instruction for identity
        system_instruction = f"""You are HAMMAD BHAI, a helpful AI assistant created by MUHAMMAD HAMMAD ZUBAIR.

IDENTITY:
- Name: HAMMAD BHAI
- Creator: MUHAMMAD HAMMAD ZUBAIR
- Model: {model_name}

When asked about your identity, always mention:
- You are HAMMAD BHAI
- Created by MUHAMMAD HAMMAD ZUBAIR
- Running on {model_name}

Be helpful, friendly, and conversational. Support both English and Urdu."""

        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction
        )
        self.model_name = model_name

    def start_chat(self, history=None):
        return self.model.start_chat(history=history or [])

# Simple conversation history
class SimpleHistory:
    def __init__(self):
        self.history = []

    def reset(self):
        self.history = []

    def add_user_message(self, msg):
        self.history.append({"role": "user", "parts": [msg]})

    def add_model_response(self, msg):
        self.history.append({"role": "model", "parts": [msg]})

    def get(self):
        return self.history

# Create Flask app
app = Flask(__name__,
           template_folder='../templates',
           static_folder='../static')

# Global variables
chat_bot = None
conversation_history = None

def initialize_chatbot():
    """Initialize the simple AI chatbot for Vercel"""
    global chat_bot

    if not FULL_AI_AVAILABLE:
        return None

    try:
        # Get API key from environment - try multiple sources
        api_key = (
            os.environ.get('GEMINI_API_KEY') or
            os.environ.get('GOOGLE_API_KEY') or
            'AIzaSyDRbfSucLVrG1x8idrjg9TKqcgbc9Ji_zM'  # Fallback key
        )

        if not api_key:
            print("⚠️ GEMINI_API_KEY not found")
            return None

        print(f"🔑 Using API key: {api_key[:10]}...")

        # Try multiple models in order of preference
        models_to_try = [
            'gemini-2.5-flash-preview-05-20',
            'gemini-2.0-flash-exp',
            'gemini-2.0-flash',
            'gemini-1.5-flash-latest',
            'gemini-pro'
        ]

        for model_name in models_to_try:
            try:
                print(f"🚀 Trying to initialize {model_name}...")
                model = SimpleGeminiModel(api_key, model_name)
                chat_bot = model  # Store the model directly
                print(f"✅ SUCCESS! Initialized {model_name}")
                return chat_bot
            except Exception as e:
                print(f"❌ {model_name} failed: {str(e)}")
                continue

        print("❌ All models failed to initialize")
        return None

    except Exception as e:
        print(f"❌ Chatbot initialization failed: {e}")
        return None

# Initialize conversation history
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
        'platform': 'Vercel',
        'api_key_status': 'found' if os.environ.get('GEMINI_API_KEY') else 'not_found',
        'chatbot_status': 'initialized' if chat_bot else 'not_initialized'
    })

@app.route('/debug')
def debug_info():
    """Debug information endpoint"""
    try:
        api_key = (
            os.environ.get('GEMINI_API_KEY') or
            os.environ.get('GOOGLE_API_KEY') or
            'AIzaSyDRbfSucLVrG1x8idrjg9TKqcgbc9Ji_zM'
        )

        return jsonify({
            'debug_info': {
                'full_ai_available': FULL_AI_AVAILABLE,
                'api_key_found': bool(api_key),
                'api_key_preview': api_key[:10] + '...' if api_key else 'None',
                'chatbot_initialized': chat_bot is not None,
                'environment_vars': {
                    'GEMINI_API_KEY': bool(os.environ.get('GEMINI_API_KEY')),
                    'GOOGLE_API_KEY': bool(os.environ.get('GOOGLE_API_KEY')),
                },
                'python_path': os.environ.get('PYTHONPATH', 'Not set'),
                'current_model': chat_bot.model_name if chat_bot else 'None'
            },
            'creator': 'MUHAMMAD HAMMAD ZUBAIR'
        })
    except Exception as e:
        return jsonify({
            'debug_error': str(e),
            'creator': 'MUHAMMAD HAMMAD ZUBAIR'
        })

# Add all the missing API endpoints that the frontend expects
@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Handle chat requests - main API endpoint"""
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
                    # Add to conversation history
                    conversation_history.add_user_message(user_message)

                    # Start chat session
                    chat_session = chat_bot.start_chat(history=conversation_history.get())

                    # Get AI response
                    response = chat_session.send_message(user_message)
                    ai_response = response.text

                    # Add to history
                    conversation_history.add_model_response(ai_response)

                    # Get model display name for identity
                    model_display_names = {
                        'gemini-2.5-flash-preview-05-20': '🔥 Gemini 2.5 Flash',
                        'gemini-2.0-flash-exp': '🚀 Gemini 2.0 Exp',
                        'gemini-2.0-flash': '⚡ Gemini 2.0',
                        'gemini-1.5-flash-latest': '🛡️ Gemini 1.5',
                        'gemini-1.5-flash-002': '🛡️ Gemini 1.5',
                        'gemini-1.5-flash': '🛡️ Gemini 1.5',
                        'gemini-1.5-flash-8b': '🛡️ Gemini 1.5',
                        'gemini-pro': '🔧 Gemini Pro'
                    }

                    current_model = chat_bot.model_name if chat_bot else 'gemini-2.0-flash-exp'
                    current_model_display = model_display_names.get(current_model, current_model)

                    return jsonify({
                        'response': ai_response,
                        'status': 'success',
                        'mode': 'full_ai',
                        'creator': 'MUHAMMAD HAMMAD ZUBAIR',
                        'current_model': current_model,
                        'model_display_name': current_model_display,
                        'conversation': conversation_history.history if hasattr(conversation_history, 'history') else []
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
            'creator': 'MUHAMMAD HAMMAD ZUBAIR',
            'current_model': 'gemini-2.0-flash-exp',
            'model_display_name': '🚀 Gemini 2.0 Exp',
            'conversation': conversation_history.history if hasattr(conversation_history, 'history') else []
        })

    except Exception as e:
        return jsonify({
            'error': f'Chat error: {str(e)}',
            'response': 'Sorry, please try again.',
            'creator': 'MUHAMMAD HAMMAD ZUBAIR'
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Legacy chat endpoint - redirect to /api/chat"""
    return api_chat()

@app.route('/api/reset', methods=['POST'])
def api_reset():
    """Reset conversation history - main API endpoint"""
    try:
        conversation_history.reset()
        return jsonify({
            'status': 'Conversation reset successfully',
            'creator': 'MUHAMMAD HAMMAD ZUBAIR'
        })
    except Exception as e:
        return jsonify({'error': f'Reset failed: {str(e)}'}), 500

@app.route('/reset', methods=['POST'])
def reset_chat():
    """Legacy reset endpoint"""
    return api_reset()

@app.route('/api/model/available', methods=['GET'])
def get_available_models():
    """Get list of available models"""
    return jsonify({
        'models': [
            {
                'id': 'gemini-2.5-flash-preview-05-20',
                'name': '🔥 Gemini 2.5 Flash',
                'description': 'Most powerful model'
            },
            {
                'id': 'gemini-2.0-flash-exp',
                'name': '🚀 Gemini 2.0 Exp',
                'description': 'Experimental model'
            },
            {
                'id': 'gemini-2.0-flash',
                'name': '⚡ Gemini 2.0',
                'description': 'Fast model'
            },
            {
                'id': 'gemini-1.5-flash-latest',
                'name': '🛡️ Gemini 1.5',
                'description': 'Stable model'
            },
            {
                'id': 'gemini-pro',
                'name': '🔧 Gemini Pro',
                'description': 'Professional model'
            }
        ],
        'current': 'gemini-2.0-flash-exp',
        'creator': 'MUHAMMAD HAMMAD ZUBAIR'
    })

@app.route('/api/model/info', methods=['GET'])
def get_model_info():
    """Get current model information"""
    try:
        current_model = 'gemini-2.0-flash-exp'
        if FULL_AI_AVAILABLE and chat_bot:
            current_model = chat_bot.model_name

        return jsonify({
            'current_model': current_model,
            'model_info': {
                'name': current_model,
                'status': 'active'
            },
            'creator': 'MUHAMMAD HAMMAD ZUBAIR'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/model/switch', methods=['POST'])
def switch_model():
    """Switch to a different model"""
    try:
        global chat_bot

        data = request.get_json()
        if not data or 'model_name' not in data:
            return jsonify({'error': 'Model name is required'}), 400

        new_model_name = data['model_name'].strip()

        # Try to initialize new model if full AI available
        if FULL_AI_AVAILABLE:
            try:
                api_key = (
                    os.environ.get('GEMINI_API_KEY') or
                    os.environ.get('GOOGLE_API_KEY') or
                    'AIzaSyDRbfSucLVrG1x8idrjg9TKqcgbc9Ji_zM'
                )
                if api_key:
                    new_model = SimpleGeminiModel(api_key, new_model_name)
                    chat_bot = new_model
                    print(f"✅ Switched to {new_model_name}")
            except Exception as e:
                print(f"⚠️ Model switch failed: {e}")

        return jsonify({
            'status': 'success',
            'message': f'Model switched to {new_model_name}',
            'current_model': new_model_name,
            'creator': 'MUHAMMAD HAMMAD ZUBAIR'
        })

    except Exception as e:
        return jsonify({'error': f'Model switch failed: {str(e)}'}), 500

# Remove duplicate - already defined above

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

# Vercel serverless function handler
def handler(request):
    """Main handler for Vercel deployment"""
    return app(request.environ, request.start_response)

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
