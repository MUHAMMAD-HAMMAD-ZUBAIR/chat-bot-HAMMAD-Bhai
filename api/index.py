"""
Vercel-optimized Flask app for HAMMAD BHAI's Chatbot
Created by MUHAMMAD HAMMAD ZUBAIR
"""
import os
from flask import Flask, render_template, request, jsonify

# Create Flask app for Vercel
app = Flask(__name__,
           template_folder='../templates',
           static_folder='../static')

# Configure for production
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# Simple conversation history for fallback mode
class SimpleConversationHistory:
    def __init__(self):
        self.history = []

    def reset(self):
        self.history = []

    def add_user_message(self, message):
        self.history.append({"role": "user", "content": message})

    def add_model_response(self, response):
        self.history.append({"role": "assistant", "content": response})

# Global conversation history
conversation_history = SimpleConversationHistory()

@app.route('/')
def index():
    """Serve the main chat interface"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"""
        <html>
        <head><title>Hammad Bhai Chatbot</title></head>
        <body>
            <h1>🤖 Hammad Bhai AI Chatbot</h1>
            <p><strong>Created by MUHAMMAD HAMMAD ZUBAIR</strong></p>
            <p>Error loading template: {str(e)}</p>
            <p>This is a fallback deployment mode.</p>
            <div style="margin: 20px; padding: 20px; border: 1px solid #ccc;">
                <h3>Quick Test:</h3>
                <p>Send a POST request to <code>/chat</code> with JSON: <code>{{"message": "Hello"}}</code></p>
                <p>Or visit <code>/health</code> for status check</p>
            </div>
        </body>
        </html>
        """, 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests with fallback response"""
    try:
        # Get user message
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        user_message = data['message'].strip()
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        # Add to conversation history
        conversation_history.add_user_message(user_message)

        # Fallback response for Vercel deployment
        fallback_response = f"""
Assalam-o-Alaikum! Main HAMMAD BHAI hun! 🤖

Aap ne kaha: "{user_message}"

Main MUHAMMAD HAMMAD ZUBAIR ka banaya hua AI assistant hun. Abhi main Vercel pe basic deployment mode mein hun.

🚀 Features coming soon:
- Google Gemini 2.0 Flash Experimental AI
- Real-time information access
- Weather, news, and prayer times
- Multi-language support

Deployment successful! Full AI features will be activated soon.

Shukriya!
- HAMMAD BHAI (Created by MUHAMMAD HAMMAD ZUBAIR)
        """

        # Add response to history
        conversation_history.add_model_response(fallback_response)

        return jsonify({
            'response': fallback_response,
            'status': 'fallback_mode',
            'deployment': 'vercel_success'
        })

    except Exception as e:
        return jsonify({
            'error': f'Chat processing failed: {str(e)}',
            'response': 'Sorry, I encountered an error. Please try again.'
        }), 500

@app.route('/reset', methods=['POST'])
def reset_chat():
    """Reset the conversation history"""
    try:
        conversation_history.reset()
        return jsonify({'status': 'Chat history reset successfully'})
    except Exception as e:
        return jsonify({'error': f'Reset failed: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Hammad Bhai Chatbot (Vercel)',
        'version': '2.0',
        'creator': 'MUHAMMAD HAMMAD ZUBAIR',
        'deployment': 'vercel_success',
        'mode': 'fallback'
    })

@app.route('/api/info')
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'Hammad Bhai AI Chatbot',
        'version': '2.0 (Vercel Deployment)',
        'creator': 'MUHAMMAD HAMMAD ZUBAIR',
        'model': 'Fallback Mode - Full AI Coming Soon',
        'status': 'Deployment Successful',
        'platform': 'Vercel',
        'features_coming_soon': [
            'Google Gemini 2.0 Flash Experimental AI',
            'Real-time information access',
            'Multi-language support',
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

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': ['/health', '/api/info', '/chat', '/reset'],
        'creator': 'MUHAMMAD HAMMAD ZUBAIR'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Please try again later',
        'creator': 'MUHAMMAD HAMMAD ZUBAIR'
    }), 500

# Add CORS headers for Vercel
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
