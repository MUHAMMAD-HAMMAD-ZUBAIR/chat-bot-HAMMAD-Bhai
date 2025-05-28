import sys
import os

# Add the root directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import the main Flask app
from app import app

def handler(event, context):
    """
    Netlify Functions handler for Flask app
    """
    try:
        # Import serverless-wsgi for Netlify
        import serverless_wsgi
        
        # Handle the request
        return serverless_wsgi.handle_request(app, event, context)
        
    except ImportError:
        # Fallback if serverless-wsgi not available
        from werkzeug.serving import WSGIRequestHandler
        from werkzeug.wrappers import Request
        from io import StringIO
        
        # Create WSGI environ from event
        environ = {
            'REQUEST_METHOD': event.get('httpMethod', 'GET'),
            'PATH_INFO': event.get('path', '/'),
            'QUERY_STRING': event.get('queryStringParameters', ''),
            'CONTENT_TYPE': event.get('headers', {}).get('content-type', ''),
            'CONTENT_LENGTH': str(len(event.get('body', ''))),
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '80',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': StringIO(event.get('body', '')),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }
        
        # Add headers
        for key, value in event.get('headers', {}).items():
            key = 'HTTP_' + key.upper().replace('-', '_')
            environ[key] = value
        
        # Response container
        response_data = {}
        
        def start_response(status, headers, exc_info=None):
            response_data['status'] = status
            response_data['headers'] = dict(headers)
        
        # Call Flask app
        response_body = app(environ, start_response)
        
        return {
            'statusCode': int(response_data.get('status', '200').split()[0]),
            'headers': response_data.get('headers', {}),
            'body': ''.join(response_body) if hasattr(response_body, '__iter__') else str(response_body)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "Internal server error", "message": "{str(e)}", "creator": "MUHAMMAD HAMMAD ZUBAIR"}}'
        }
