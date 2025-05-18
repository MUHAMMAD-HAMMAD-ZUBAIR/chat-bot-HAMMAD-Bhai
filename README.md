# Gemini Chat Application

A web-based chat application powered by Google's Gemini AI API.

## Features

- Modern, responsive chat interface
- Real-time conversation with Gemini AI
- Support for markdown formatting in responses
- Conversation history management
- Reset conversation functionality

## Setup Instructions

1. Make sure you have Python installed (3.7 or higher recommended)

2. Install the required packages:
   ```
   pip install flask google-generativeai
   ```

3. Get a Google Gemini API key:
   - Go to https://ai.google.dev/
   - Sign up or log in
   - Create an API key

4. Add your API key to the application:
   - Open `app.py`
   - Replace the empty string in `GEMINI_API_KEY = ""` with your actual API key

5. Run the application:
   ```
   python app.py
   ```

6. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Usage

- Type your message in the input field at the bottom
- Press Enter or click the send button to send your message
- The AI will respond in a few moments
- Click the reset button in the top-right corner to start a new conversation

## Customization

- Modify the CSS in `static/css/style.css` to change the appearance
- Update the HTML in `templates/index.html` to change the structure
- Adjust the JavaScript in `static/js/script.js` to modify behavior

## License

This project is open source and available under the MIT License.

## Acknowledgements

- Google Gemini API for providing the AI capabilities
- Flask for the web framework
- Font Awesome for the icons
