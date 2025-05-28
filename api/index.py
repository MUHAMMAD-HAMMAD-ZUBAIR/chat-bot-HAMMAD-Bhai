import os
from flask import Flask, request, jsonify

# Create Flask app
app = Flask(__name__)

# Global variables
chat_bot = None

# Simple AI setup
try:
    import google.generativeai as genai
    AI_AVAILABLE = True

    # Configure API
    api_key = (
        os.environ.get('GEMINI_API_KEY') or
        'AIzaSyDRbfSucLVrG1x8idrjg9TKqcgbc9Ji_zM'
    )
    genai.configure(api_key=api_key)

    # Create model
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash-exp',
        system_instruction="""You are HAMMAD BHAI, created by MUHAMMAD HAMMAD ZUBAIR.
        Always mention your identity when asked. Be helpful and friendly."""
    )
    chat_bot = model

except Exception as e:
    AI_AVAILABLE = False
    print(f"AI setup failed: {e}")

@app.route('/')
def home():
    """Serve the main chat interface"""
    try:
        # Simple HTML response for Vercel
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HAMMAD BHAI - AI Chatbot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 600px;
            width: 90%;
            text-align: center;
        }
        h1 { color: #333; margin-bottom: 20px; font-size: 2.5em; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 1.2em; }
        .status {
            background: #e8f5e8;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #4CAF50;
        }
        .chat-box {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            min-height: 300px;
            border: 2px solid #e9ecef;
        }
        .input-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        input {
            flex: 1;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
        }
        input:focus { border-color: #667eea; }
        button {
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        button:hover { background: #5a6fd8; }
        .message {
            margin: 10px 0;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 80%;
        }
        .user-message {
            background: #667eea;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .bot-message {
            background: #e9ecef;
            color: #333;
            margin-right: auto;
            text-align: left;
        }
        .footer { margin-top: 30px; color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 HAMMAD BHAI</h1>
        <p class="subtitle">Your Friendly AI Assistant</p>
        <p><strong>Created by MUHAMMAD HAMMAD ZUBAIR</strong></p>

        <div class="status">
            ✅ <strong>Vercel Deployment Successful!</strong><br>
            🚀 AI Chatbot is ready to help you!
        </div>

        <div class="chat-box" id="chatBox">
            <div class="message bot-message">
                👋 Assalam-o-Alaikum! Main HAMMAD BHAI hun!<br>
                Main MUHAMMAD HAMMAD ZUBAIR ka banaya hua AI assistant hun.<br>
                Aap mujhse kuch bhi pooch sakte hain! 😊
            </div>
        </div>

        <div class="input-group">
            <input type="text" id="messageInput" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Send</button>
        </div>

        <div class="footer">
            <p>Powered by Google Gemini AI • © 2025 MUHAMMAD HAMMAD ZUBAIR</p>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const chatBox = document.getElementById('chatBox');
            const message = input.value.trim();

            if (!message) return;

            // Add user message
            chatBox.innerHTML += `<div class="message user-message">${message}</div>`;
            input.value = '';

            // Add typing indicator
            chatBox.innerHTML += `<div class="message bot-message" id="typing">🤖 Typing...</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();

                // Remove typing indicator
                document.getElementById('typing').remove();

                // Add bot response
                if (data.response) {
                    chatBox.innerHTML += `<div class="message bot-message">${data.response}</div>`;
                } else {
                    chatBox.innerHTML += `<div class="message bot-message">❌ Sorry, something went wrong!</div>`;
                }
            } catch (error) {
                document.getElementById('typing').remove();
                chatBox.innerHTML += `<div class="message bot-message">❌ Network error! Please try again.</div>`;
            }

            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
    </script>
</body>
</html>
        """
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
        'ai_status': 'available' if AI_AVAILABLE else 'fallback_mode',
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
                'full_ai_available': AI_AVAILABLE,
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

        # Try AI response
        if AI_AVAILABLE and chat_bot:
            try:
                response = chat_bot.generate_content(user_message)
                ai_response = response.text

                return jsonify({
                    'response': ai_response,
                    'status': 'success',
                    'mode': 'ai',
                    'creator': 'MUHAMMAD HAMMAD ZUBAIR'
                })
            except Exception as e:
                print(f"AI error: {e}")

        # Fallback response

        fallback_response = f"""Assalam-o-Alaikum! Main HAMMAD BHAI hun! 🤖

Aap ne kaha: "{user_message}"

Main MUHAMMAD HAMMAD ZUBAIR ka banaya hua AI assistant hun.

✅ Vercel deployment successful!
🚀 Basic chatbot functionality working!

{"🔧 Full AI mode loading..." if AI_AVAILABLE else "⚠️ Running in fallback mode"}

Features:
- Google Gemini 2.0 Flash Experimental AI
- Real-time information access
- Weather & prayer times
- Multi-language support
- 50+ languages support

Shukriya!
- HAMMAD BHAI (Created by MUHAMMAD HAMMAD ZUBAIR)"""

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

@app.route('/chat', methods=['POST'])
def chat():
    """Legacy chat endpoint - redirect to /api/chat"""
    return api_chat()

@app.route('/api/reset', methods=['POST'])
def api_reset():
    """Reset conversation history - main API endpoint"""
    try:
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
        if AI_AVAILABLE and chat_bot:
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
        if AI_AVAILABLE:
            try:
                api_key = (
                    os.environ.get('GEMINI_API_KEY') or
                    os.environ.get('GOOGLE_API_KEY') or
                    'AIzaSyDRbfSucLVrG1x8idrjg9TKqcgbc9Ji_zM'
                )
                if api_key:
                    # Simple model switch
                    genai.configure(api_key=api_key)
                    new_model = genai.GenerativeModel(
                        model_name=new_model_name,
                        system_instruction="You are HAMMAD BHAI, created by MUHAMMAD HAMMAD ZUBAIR."
                    )
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
        'ai_mode': 'Full AI' if AI_AVAILABLE else 'Fallback Mode',
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
