"""
Simplified Flask app for Vercel deployment
This is a fallback version that works independently
"""
import os
from flask import Flask, render_template, request, jsonify

# Create Flask app
app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')

# Configure for production
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# Add CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

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
            <h1>Hammad Bhai AI Chatbot</h1>
            <p>Created by MUHAMMAD HAMMAD ZUBAIR</p>
            <p>Error loading template: {str(e)}</p>
            <p>Please check if templates are properly deployed.</p>
        </body>
        </html>
        """, 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests with fallback response"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Fallback response when full AI is not available
        fallback_response = f"""
        Assalam-o-Alaikum! Main HAMMAD BHAI hun, MUHAMMAD HAMMAD ZUBAIR ka banaya hua AI assistant.

        Aap ne kaha: "{user_message}"

        Maaf kijiye, abhi main full AI mode mein nahi hun. Yeh ek basic deployment test hai.
        
        Main MUHAMMAD HAMMAD ZUBAIR ka creation hun aur Google ke sabse powerful Gemini 2.0 Flash Experimental model se powered hun.

        Jald hi main puri functionality ke saath wapas aa jaunga!

        Shukriya!
        - HAMMAD BHAI (Created by MUHAMMAD HAMMAD ZUBAIR)
        """
        
        return jsonify({
            'response': fallback_response,
            'status': 'fallback_mode'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Chat processing failed: {str(e)}',
            'response': 'Sorry, I encountered an error. Please try again.'
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Hammad Bhai Chatbot (Fallback Mode)',
        'version': '2.0',
        'creator': 'MUHAMMAD HAMMAD ZUBAIR',
        'mode': 'fallback'
    })

@app.route('/api/info')
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'Hammad Bhai AI Chatbot',
        'version': '2.0 (Fallback)',
        'creator': 'MUHAMMAD HAMMAD ZUBAIR',
        'model': 'Fallback Mode - Full AI Coming Soon',
        'status': 'Basic deployment test successful',
        'message': 'This is a simplified version for testing Vercel deployment'
    })

@app.route('/reset', methods=['POST'])
def reset_chat():
    """Reset endpoint"""
    return jsonify({'status': 'Reset successful (fallback mode)'})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
