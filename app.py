import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from abc import ABC, abstractmethod

# ----------- Abstract Base Class for Model ------------
class BaseChatModel(ABC):
    @abstractmethod
    def start_chat(self, history):
        pass

# ----------- Gemini Model Wrapper ------------
class GeminiModel(BaseChatModel):
    def __init__(self, api_key: str, model_name: str = 'gemini-1.5-flash'):
        if not api_key:
            raise ValueError("API Key is required for Gemini API")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def start_chat(self, history):
        return self.model.start_chat(history=history)

# ----------- Conversation History Manager ------------
class ConversationHistory:
    def __init__(self):
        self.history = []

    def add_user_message(self, message):
        self.history.append({"role": "user", "parts": [message]})

    def add_model_response(self, message):
        self.history.append({"role": "model", "parts": [message]})

    def reset(self):
        self.history = []

    def get(self):
        return self.history

    def pop_last_if_user(self):
        if self.history and self.history[-1]["role"] == "user":
            self.history.pop()

# ----------- Main Chatbot Controller ------------
class ChatBot:
    def __init__(self, model: BaseChatModel):
        self.model = model
        self.history = ConversationHistory()

    def send_message(self, user_message: str) -> str:
        self.history.add_user_message(user_message)
        chat = self.model.start_chat(self.history.get())
        response = chat.send_message(user_message)
        self.history.add_model_response(response.text)
        return response.text

    def get_conversation(self):
        return self.history.get()

    def reset_conversation(self):
        self.history.reset()

    def undo_last_user_message(self):
        self.history.pop_last_if_user()

# ----------- Flask Setup ------------
app = Flask(__name__)

# Load API key (env or direct fallback)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDzkUNQuw_V8q54kesKdX-T_2wcqh8kCvA")

# Initialize Gemini model and ChatBot
gemini_model = GeminiModel(api_key=GEMINI_API_KEY)
chatbot = ChatBot(model=gemini_model)

# ----------- Flask Routes ------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        try:
            response = chatbot.send_message(user_message)
            return jsonify({
                'response': response,
                'conversation': chatbot.get_conversation()
            })

        except Exception as api_error:
            error_message = str(api_error)
            print(f"API Error: {error_message}")

            chatbot.undo_last_user_message()

            # Friendly error messages
            if "429" in error_message and "quota" in error_message:
                user_friendly_message = "API quota exceeded. Please try again later."
            elif "400" in error_message and "safety" in error_message.lower():
                user_friendly_message = "Message blocked by safety filters. Try something different."
            else:
                user_friendly_message = "AI service error. Please try again."

            return jsonify({
                'error': user_friendly_message,
                'technical_error': error_message
            }), 500

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({'error': 'Unexpected server error occurred.'}), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    chatbot.reset_conversation()
    return jsonify({'status': 'Conversation reset successfully'})

# ----------- Run Flask App ------------
if __name__ == '__main__':
    app.run(debug=True)
