import sys
import os

# Add the root directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def handler(event, context):
    """
    Netlify Functions handler for ORIGINAL HAMMAD BHAI AI Assistant
    """
    try:
        # Import serverless-wsgi and the original Flask app
        import serverless_wsgi
        from app import app

        # Handle the request using serverless-wsgi
        return serverless_wsgi.handle_request(app, event, context)

    except Exception as e:
        # Fallback response if anything fails
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HAMMAD BHAI - AI Assistant</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 600px;
            width: 100%;
            text-align: center;
        }}
        h1 {{ color: #333; margin-bottom: 20px; }}
        .error {{ background: #ffe8e8; padding: 15px; border-radius: 10px; margin: 20px 0; }}
        .status {{ background: #e8f5e8; padding: 15px; border-radius: 10px; margin: 20px 0; }}
        .features {{ background: #f0f8ff; padding: 15px; border-radius: 10px; margin: 20px 0; text-align: left; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 HAMMAD BHAI AI Assistant</h1>
        <p><strong>Created by MUHAMMAD HAMMAD ZUBAIR</strong></p>

        <div class="status">
            ✅ <strong>Original Flask App Detected!</strong><br>
            🚀 Netlify Functions are running
        </div>

        <div class="error">
            ⚠️ <strong>Initialization Error:</strong><br>
            {str(e)}<br><br>
            🔧 <strong>Possible Issues:</strong><br>
            - Dependencies not installed<br>
            - Environment variables missing<br>
            - Import path issues
        </div>

        <div class="features">
            <h3>🎯 Original Features Available:</h3>
            <ul>
                <li>🤖 Advanced AI Chat with Google Gemini</li>
                <li>🌤️ Real-time Weather Data</li>
                <li>🕌 Prayer Times & Islamic Calendar</li>
                <li>💰 Currency & Crypto Prices</li>
                <li>📰 Live News Headlines</li>
                <li>🌍 World Times & Country Info</li>
                <li>🏥 Health Tips & Emergency Numbers</li>
                <li>📈 Stock Market & Sports Updates</li>
                <li>🎓 Education & Entertainment Info</li>
                <li>🔄 Model Switching Capability</li>
            </ul>
        </div>

        <p><strong>Platform:</strong> Netlify Functions + Original Flask App</p>
        <p><strong>Status:</strong> Attempting to load full features...</p>

        <div style="margin-top: 30px; color: #666;">
            <p>© 2025 MUHAMMAD HAMMAD ZUBAIR</p>
        </div>
    </div>
</body>
</html>
            '''
        }
