import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configuration for Google Gemini API
# You'll need to set your API key as an environment variable or enter it directly here
# Get your API key from https://ai.google.dev/
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDzkUNQuw_V8q54kesKdX-T_2wcqh8kCvA")  # API key provided by user

# Check if API key is provided
if not GEMINI_API_KEY:
    print("\n" + "="*50)
    print("WARNING: Gemini API Key not found!")
    print("Please edit app.py and add your API key to the GEMINI_API_KEY variable")
    print("Get your API key from https://ai.google.dev/")
    print("="*50 + "\n")
    raise ValueError("API Key is required to use the Gemini API")

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Set up the model
# Using gemini-1.5-flash which has higher quota limits than gemini-1.5-pro
model = genai.GenerativeModel('gemini-1.5-flash')

# Store conversation history
conversation_history = []

@app.route('/')
def index():
    """Render the main chat interface."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat messages and return AI responses."""
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Add user message to conversation history
        conversation_history.append({"role": "user", "parts": [user_message]})

        try:
            # Create a chat session
            chat = model.start_chat(history=conversation_history)

            # Generate a response
            response = chat.send_message(user_message)

            # Add AI response to conversation history
            conversation_history.append({"role": "model", "parts": [response.text]})

            return jsonify({
                'response': response.text,
                'conversation': conversation_history
            })

        except Exception as api_error:
            error_message = str(api_error)
            print(f"API Error: {error_message}")

            # Check for quota exceeded errors
            if "429" in error_message and "quota" in error_message:
                user_friendly_message = "API quota exceeded. The free tier of Google Gemini API has rate limits. Please try again in a minute or switch to a different model."
            elif "400" in error_message and "safety" in error_message.lower():
                user_friendly_message = "Your message was flagged by the AI safety filters. Please try a different message."
            else:
                user_friendly_message = "There was an error communicating with the AI service. Please try again later."

            # Remove the failed user message from history
            if conversation_history and conversation_history[-1]["role"] == "user":
                conversation_history.pop()

            return jsonify({
                'error': user_friendly_message,
                'technical_error': error_message
            }), 500

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred on the server.'}), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset the conversation history."""
    global conversation_history
    conversation_history = []
    return jsonify({'status': 'Conversation reset successfully'})

if __name__ == '__main__':
    app.run(debug=True)
