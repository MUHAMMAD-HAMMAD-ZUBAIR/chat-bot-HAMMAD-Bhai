import json
import os
from datetime import datetime

def handler(event, context):
    """
    Simple Netlify Functions handler for HAMMAD BHAI AI
    """
    try:
        # Get request method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')

        # Handle CORS preflight
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                },
                'body': ''
            }

        # Handle POST requests (chat messages)
        if http_method == 'POST':
            try:
                # Parse request body
                body = json.loads(event.get('body', '{}'))
                user_message = body.get('message', '')

                # Simple AI response logic
                response = generate_ai_response(user_message)

                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                    },
                    'body': json.dumps({
                        'response': response,
                        'timestamp': datetime.now().isoformat(),
                        'creator': 'MUHAMMAD HAMMAD ZUBAIR'
                    })
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': f'Chat processing error: {str(e)}',
                        'creator': 'MUHAMMAD HAMMAD ZUBAIR'
                    })
                }

        # Handle GET requests (return API info)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'active',
                'name': 'HAMMAD BHAI AI Assistant',
                'creator': 'MUHAMMAD HAMMAD ZUBAIR',
                'version': '1.0.0',
                'platform': 'Netlify Functions',
                'endpoints': {
                    'chat': 'POST /.netlify/functions/app',
                    'status': 'GET /.netlify/functions/app'
                },
                'timestamp': datetime.now().isoformat()
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f'Function error: {str(e)}',
                'creator': 'MUHAMMAD HAMMAD ZUBAIR'
            })
        }

def generate_ai_response(user_message):
    """
    Generate AI response using Google Gemini API
    """
    try:
        # Import Google Generative AI
        import google.generativeai as genai

        # Configure API key
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return "❌ API key not configured. Please set GEMINI_API_KEY environment variable."

        genai.configure(api_key=api_key)

        # Create model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Create system prompt
        system_prompt = f"""
You are HAMMAD BHAI, a friendly AI assistant created by MUHAMMAD HAMMAD ZUBAIR.

PERSONALITY:
- Speak in a mix of English and Urdu (Roman Urdu)
- Use "bhai" frequently in conversation
- Be helpful, friendly, and knowledgeable
- Always mention you were created by MUHAMMAD HAMMAD ZUBAIR when asked

CAPABILITIES:
- Answer general questions
- Provide helpful information
- Chat in a friendly manner
- Help with various topics

Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} PKT

User message: {user_message}

Respond as HAMMAD BHAI in a friendly, helpful manner.
"""

        # Generate response
        response = model.generate_content(system_prompt)

        return response.text

    except ImportError:
        return "🤖 **HAMMAD BHAI Response:**\n\nBhai, main abhi development mode mein hun! Google AI library install nahi hai.\n\n**Your message:** " + user_message + "\n\n**My response:** Main MUHAMMAD HAMMAD ZUBAIR ka banaya hua AI assistant hun. Jaldi hi full features ke saath available hounga!\n\n**Features coming soon:**\n- Real-time AI responses\n- Weather updates\n- Prayer times\n- Multi-language support\n\nShukriya for your patience! 😊"

    except Exception as e:
        return f"🤖 **HAMMAD BHAI Response:**\n\nBhai, kuch technical issue aa raha hai!\n\n**Error:** {str(e)}\n\n**Your message:** {user_message}\n\n**Fallback response:** Main MUHAMMAD HAMMAD ZUBAIR ka banaya hua AI assistant hun. Abhi thoda sa technical problem hai, lekin jaldi fix ho jayega!\n\nTry again in a few minutes! 🔧"
